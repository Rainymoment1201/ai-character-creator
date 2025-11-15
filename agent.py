# -*- coding: utf-8 -*-
"""角色创建 Agent 主程序"""

import streamlit as st
import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from prompts import (
    get_system_prompt, 
    EXTRACTION_PROMPT, 
    SD_PROMPT_TEMPLATE,
    PROFILE_GENERATION_PROMPT
)

# 加载环境变量
load_dotenv()

# 获取 API 配置（优先使用 Streamlit secrets，其次是环境变量）
def get_config(key, default=None):
    """从 Streamlit secrets 或环境变量获取配置"""
    try:
        # 尝试从 Streamlit secrets 获取
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    # 回退到环境变量
    return os.getenv(key, default)

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=get_config("OPENAI_API_KEY"),
    base_url=get_config("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# 状态定义
STATES = {
    "INIT": "初始状态",
    "IMAGE_FIRST_GUIDING": "生图优先-引导中",
    "IMAGE_FIRST_GENERATED": "图像已生成",
    "IMAGE_GENERATED_PROFILE_GUIDING": "图像已生成-引导角色信息",
    "PROFILE_FIRST_GUIDING": "角色信息优先-引导中",
    "PROFILE_FIRST_GENERATED": "角色信息已生成",
    "PROFILE_GENERATED_IMAGE_GUIDING": "角色信息已生成-引导生图",
    "BOTH_COMPLETED": "两者都完成",
    "CHAT_MODE": "聊天模式",
    "CREATING": "创建中",
    "COMPLETED": "创建完成"
}


def initialize_session_state():
    """初始化会话状态"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.state = "INIT"
        st.session_state.conversation_history = []
        st.session_state.turn_count = 0
        st.session_state.user_preference = None  # "image_first" or "profile_first"
        st.session_state.collected_info = {
            "image_info": {},
            "profile_info": {}
        }
        st.session_state.image_generated = False
        st.session_state.profile_generated = False
        st.session_state.image_url = None
        st.session_state.profile_data = None
        st.session_state.show_image_button = False
        st.session_state.show_profile_button = False
        st.session_state.show_confirm_button = False
        st.session_state.turn_count_after_image = 0
        st.session_state.turn_count_after_profile = 0
        st.session_state.last_button_index = -1  # 记录最后显示按钮的消息索引
        
        # 添加初始欢迎消息
        welcome_msg = "嗨！我来帮你创建一个专属的 AI 陪伴角色~ 🎨\n\n我们可以先设计角色的外观图像，也可以先设定角色的性格和背景。你想从哪个开始呢？"
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": welcome_msg
        })


def call_llm(messages, temperature=0.7, stream=False):
    """调用 LLM"""
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",  # SiliconFlow 上的 DeepSeek-V3 模型
            messages=messages,
            temperature=temperature,
            max_tokens=2000,
            stream=stream
        )
        
        if stream:
            return response  # 返回流式响应对象
        else:
            return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，调用 AI 时出错了：{str(e)}\n\n请检查你的 API 配置。"


def stream_llm_response(messages, temperature=0.7):
    """流式调用 LLM，返回生成器"""
    try:
        stream = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=messages,
            temperature=temperature,
            max_tokens=2000,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"抱歉，调用 AI 时出错了：{str(e)}\n\n请检查你的 API 配置。"


def extract_info_from_conversation():
    """从对话历史中提取信息"""
    conversation_text = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in st.session_state.conversation_history
    ])
    
    prompt = EXTRACTION_PROMPT.format(conversation_history=conversation_text)
    
    messages = [
        {"role": "system", "content": "你是一个信息提取助手，请严格按照 JSON 格式返回提取的信息。"},
        {"role": "user", "content": prompt}
    ]
    
    response = call_llm(messages, temperature=0.3)
    
    try:
        # 提取 JSON（处理可能的 markdown 包裹）
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
        
        extracted = json.loads(json_str)
        return extracted
    except Exception as e:
        st.error(f"信息提取失败：{str(e)}")
        return st.session_state.collected_info


def call_image_generation_api(prompt_text):
    """调用硅基流动生图 API"""
    import requests
    
    api_key = get_config("IMAGE_API_KEY")
    api_url = get_config("IMAGE_API_URL", "https://api.siliconflow.cn/v1/images/generations")
    model = get_config("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
    
    if not api_key:
        raise ValueError("IMAGE_API_KEY 未配置，请在 .env 文件中添加")
    
    # 提取正面提示词（|||前面的部分）
    if "|||" in prompt_text:
        positive_prompt = prompt_text.split("|||")[0].strip()
    else:
        positive_prompt = prompt_text.strip()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建请求参数
    payload = {
        "model": model,
        "prompt": positive_prompt,
        "image_size": "1024x1024",
        "num_inference_steps": 20
    }
    
    st.info(f"📤 发送请求到: {api_url}")
    st.info(f"📦 使用模型: {model}")
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # 显示详细的错误信息
        if response.status_code != 200:
            error_detail = response.text
            st.error(f"API 返回错误 {response.status_code}:")
            st.code(error_detail)
        
        response.raise_for_status()
        
        result = response.json()
        
        # 硅基流动返回格式：{"images": [{"url": "..."}, ...]}
        if "images" in result and len(result["images"]) > 0:
            return result["images"][0]["url"]
        else:
            raise ValueError(f"API 返回格式异常：{result}")
            
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP 错误: {e}")
        raise Exception(f"调用生图 API 失败：{str(e)}")
    except Exception as e:
        raise Exception(f"调用生图 API 失败：{str(e)}")


def generate_image_from_description():
    """根据描述生成图像"""
    st.info("🎨 正在生成图像...")
    
    # 提取图像信息
    image_info = st.session_state.collected_info.get("image_info", {})
    
    # 生成 SD prompt
    prompt = SD_PROMPT_TEMPLATE.format(character_info=json.dumps(image_info, ensure_ascii=False))
    messages = [
        {"role": "system", "content": "你是 Stable Diffusion 提示词专家。必须严格按照要求生成纯英文关键词格式的提示词，禁止使用中文，禁止长篇描述。"},
        {"role": "user", "content": prompt}
    ]
    
    sd_prompt = call_llm(messages, temperature=0.5)
    
    # 显示生成的提示词
    with st.expander("🔍 查看生成的提示词"):
        st.code(sd_prompt)
    
    # 调用硅基流动生图 API
    try:
        with st.spinner("🎨 正在调用硅基流动生图 API，请稍候..."):
            image_url = call_image_generation_api(sd_prompt)
        
        st.session_state.image_url = image_url
        st.session_state.image_generated = True
        # 不隐藏按钮，让它常驻
        # st.session_state.show_image_button = False
        
        # 更新状态
        if st.session_state.user_preference == "image_first":
            st.session_state.state = "IMAGE_GENERATED_PROFILE_GUIDING"
        
        # 添加系统消息，包含图片标记
        success_msg = "✅ 图像生成完成！\n\n[IMAGE]"  # 特殊标记，表示这里要显示图片
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": success_msg,
            "has_image": True  # 标记这条消息包含图片
        })
        
        # 添加下一步提示
        next_prompt = "图像生成好啦！✨ 接下来我们来设定角色的性格和背景吧~\n\n我可以根据这张图帮你自动生成完整的角色设定，或者你想自己一步步设计？"
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": next_prompt
        })
        
    except Exception as e:
        st.error(f"❌ 生图失败：{str(e)}")
        st.warning("请检查：\n1. IMAGE_API_KEY 是否配置正确\n2. 网络连接是否正常\n3. API 余额是否充足\n4. 模型名称是否正确")
        return
    
    st.rerun()


def display_profile_info(profile_data):
    """美观地展示角色信息"""
    st.markdown("### 📋 角色信息")
    
    # 基础信息
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**姓名 (Name)**")
        st.info(profile_data.get("Name", "未设置"))
    with col2:
        st.markdown(f"**性别 (Gender)**")
        st.info(profile_data.get("Gender", "未设置"))
    
    # 简介
    st.markdown(f"**简介 (Evaluation)**")
    st.success(profile_data.get("Evaluation", "未设置"))
    
    # 详细描述
    st.markdown(f"**详细描述 (Intro)**")
    st.write(profile_data.get("Intro", "未设置"))
    
    # 开场白
    st.markdown(f"**开场白 (FirstMsg)**")
    st.chat_message("assistant", avatar="🎭").markdown(profile_data.get("FirstMsg", "未设置"))
    
    # 标签
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**角色标签 (Categories)**")
        categories = profile_data.get("Categories", [])
        if categories:
            tags_html = " ".join([f'`{tag}`' for tag in categories])
            st.markdown(tags_html)
        else:
            st.write("未设置")
    
    with col2:
        st.markdown(f"**声音标签 (SoundTags)**")
        sound_tags = profile_data.get("SoundTags", [])
        if sound_tags:
            tags_html = " ".join([f'`{tag}`' for tag in sound_tags])
            st.markdown(tags_html)
        else:
            st.write("未设置")
    
    # 场景
    st.markdown(f"**对话场景 (Scene)**")
    st.write(profile_data.get("Scene", "未设置"))
    
    # 对话示例
    st.markdown(f"**对话示例 (DialogExample)**")
    dialog_example = profile_data.get("DialogExample", "未设置")
    if "：" in dialog_example:
        st.chat_message("assistant", avatar="💬").markdown(dialog_example.split("：", 1)[1])
    else:
        st.write(dialog_example)


def generate_profile_from_conversation():
    """根据对话生成角色信息"""
    st.info("📝 正在生成角色信息...")
    
    profile_info = st.session_state.collected_info.get("profile_info", {})
    image_description = ""
    
    if st.session_state.image_generated and st.session_state.collected_info.get("image_info"):
        image_description = f"图像描述：{json.dumps(st.session_state.collected_info['image_info'], ensure_ascii=False)}"
    
    prompt = PROFILE_GENERATION_PROMPT.format(
        known_info=json.dumps(profile_info, ensure_ascii=False),
        image_description=image_description
    )
    
    messages = [
        {"role": "system", "content": "你是角色设定专家，擅长创建有趣且立体的角色。"},
        {"role": "user", "content": prompt}
    ]
    
    response = call_llm(messages, temperature=0.8)
    
    try:
        # 提取 JSON
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
        
        profile_data = json.loads(json_str)
        st.session_state.profile_data = profile_data
        st.session_state.profile_generated = True
        # 不隐藏按钮，让它常驻
        # st.session_state.show_profile_button = False
        
        # 更新状态
        if st.session_state.user_preference == "profile_first":
            st.session_state.state = "PROFILE_GENERATED_IMAGE_GUIDING"
        
        st.success("✅ 角色信息生成完成！")
        
        # 显示生成的角色信息
        display_profile_info(profile_data)
        
        # 添加下一步提示
        if st.session_state.user_preference == "profile_first":
            next_prompt = "角色信息创建完成！🎉 现在我们来为角色生成图像吧~\n\n我可以根据角色信息自动生成图像，或者你想详细描述一下想要的图像效果？"
        else:
            next_prompt = "太棒了！角色已经完整了~ 🎉"
        
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": next_prompt
        })
        
    except Exception as e:
        st.error(f"生成角色信息失败：{str(e)}")
    
    st.rerun()


def process_user_input(user_input):
    """处理用户输入，更新状态（不包括显示）"""
    # 添加用户消息到历史
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    # 更新轮次计数
    st.session_state.turn_count += 1
    
    # 检测用户意图（在初始状态）
    if st.session_state.state == "INIT":
        user_input_lower = user_input.lower()
        if any(keyword in user_input for keyword in ["图", "外观", "形象", "长相", "样子"]):
            st.session_state.user_preference = "image_first"
            st.session_state.state = "IMAGE_FIRST_GUIDING"
        elif any(keyword in user_input for keyword in ["性格", "背景", "信息", "设定", "人设"]):
            st.session_state.user_preference = "profile_first"
            st.session_state.state = "PROFILE_FIRST_GUIDING"
    
    # 统计图像生成后的轮次
    if st.session_state.image_generated and st.session_state.state == "IMAGE_GENERATED_PROFILE_GUIDING":
        st.session_state.turn_count_after_image += 1
    
    # 统计角色信息生成后的轮次
    if st.session_state.profile_generated and st.session_state.state == "PROFILE_GENERATED_IMAGE_GUIDING":
        st.session_state.turn_count_after_profile += 1


def get_assistant_response_stream(user_input):
    """获取 AI 的流式响应"""
    # 构建系统提示词
    system_prompt = get_system_prompt(
        state=st.session_state.state,
        user_preference=st.session_state.user_preference or "",
        turn_count=st.session_state.turn_count,
        collected_info=st.session_state.collected_info
    )
    
    # 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.conversation_history)
    
    # 返回流式响应生成器
    return stream_llm_response(messages)


def update_button_visibility():
    """更新按钮可见性"""
    # 先重置所有按钮状态
    st.session_state.show_image_button = False
    st.session_state.show_profile_button = False
    
    # 图像优先流程
    if st.session_state.user_preference == "image_first":
        # 图像未生成：显示生图按钮
        if not st.session_state.image_generated and st.session_state.turn_count >= 3:
            st.session_state.show_image_button = True
        # 图像已生成，角色信息未生成：显示角色信息按钮
        elif st.session_state.image_generated and not st.session_state.profile_generated:
            st.session_state.show_profile_button = True
    
    # 角色信息优先流程
    elif st.session_state.user_preference == "profile_first":
        # 角色信息未生成：显示角色信息按钮
        if not st.session_state.profile_generated and st.session_state.turn_count >= 3:
            st.session_state.show_profile_button = True
        # 角色信息已生成，图像未生成：显示生图按钮
        elif st.session_state.profile_generated and not st.session_state.image_generated:
            st.session_state.show_image_button = True
    
    # 两个都完成后，自动进入聊天模式
    if st.session_state.image_generated and st.session_state.profile_generated:
        st.session_state.state = "CHAT_MODE"
        st.session_state.show_image_button = False
        st.session_state.show_profile_button = False


def chat_with_character():
    """和角色聊天界面"""
    st.title("💬 和角色聊天")
    
    # 初始化聊天历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
        # 添加角色的开场白
        if st.session_state.profile_data:
            first_msg = st.session_state.profile_data.get("FirstMsg", "你好！很高兴认识你~")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": first_msg
            })
    
    # 侧边栏显示角色信息
    with st.sidebar:
        st.markdown("### 🎭 角色信息")
        
        if st.session_state.image_url:
            st.image(st.session_state.image_url, use_column_width=True)
        
        if st.session_state.profile_data:
            st.markdown(f"**{st.session_state.profile_data.get('Name', '未命名角色')}**")
            st.caption(st.session_state.profile_data.get('Evaluation', ''))
            
            with st.expander("📋 查看完整信息"):
                st.json(st.session_state.profile_data)
        
        st.markdown("---")
        
        # 导出和重置按钮
        if st.session_state.profile_data:
            json_str = json.dumps(st.session_state.profile_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 下载角色信息",
                data=json_str,
                file_name=f"{st.session_state.profile_data.get('Name', 'character')}.json",
                mime="application/json",
                use_column_width=True
            )
        
        if st.button("🔄 创建新角色", use_column_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # 显示聊天历史
    st.markdown("---")
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="😊"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🎭"):
                st.markdown(msg["content"])
    
    # 用户输入
    user_input = st.chat_input(f"和 {st.session_state.profile_data.get('Name', '角色')} 说点什么...")
    
    if user_input:
        # 添加用户消息
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # 显示用户消息
        with st.chat_message("user", avatar="😊"):
            st.markdown(user_input)
        
        # 构建角色的 system prompt
        character_name = st.session_state.profile_data.get('Name', '角色')
        character_intro = st.session_state.profile_data.get('Intro', '')
        dialog_example = st.session_state.profile_data.get('DialogExample', '')
        
        system_prompt = f"""你现在要扮演 {character_name}。

角色设定：
{character_intro}

说话风格示例：
{dialog_example}

请严格按照角色设定和说话风格回复，保持角色的性格特点。
"""
        
        # 构建消息列表（只保留最近10轮对话）
        recent_history = st.session_state.chat_history[-20:]  # 最近10轮
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(recent_history)
        
        # 流式显示角色回复
        with st.chat_message("assistant", avatar="🎭"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 流式获取回复
            for chunk in stream_llm_response(messages, temperature=0.9):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # 添加角色回复到历史
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        st.rerun()


def finalize_character():
    """最终创建角色（已弃用，现在直接进入聊天模式）"""
    st.session_state.state = "COMPLETED"
    st.success("🎉 恭喜！你的角色创建完成了！")
    
    # 显示最终结果
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎨 角色图像")
        if st.session_state.image_url:
            st.image(st.session_state.image_url, use_column_width=True)
    
    with col2:
        if st.session_state.profile_data:
            display_profile_info(st.session_state.profile_data)
    
    # 导出按钮
    st.markdown("---")
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.session_state.profile_data:
            json_str = json.dumps(st.session_state.profile_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 下载角色信息 (JSON)",
                data=json_str,
                file_name=f"{st.session_state.profile_data.get('Name', 'character')}.json",
                mime="application/json"
            )
    
    with export_col2:
        if st.button("🔄 创建新角色", type="primary"):
            # 重置所有状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.balloons()


def main():
    """主程序"""
    st.set_page_config(
        page_title="AI 角色创建助手",
        page_icon="🎨",
        layout="wide"
    )
    
    # 初始化会话状态
    initialize_session_state()
    
    # 侧边栏
    with st.sidebar:
        st.title("🎨 角色创建助手")
        st.markdown("---")
        
        # 显示当前状态
        st.subheader("当前状态")
        st.info(f"**{STATES.get(st.session_state.state, '未知')}**")
        
        st.markdown("---")
        
        # 对话轮次
        st.subheader("📊 对话进度")
        st.metric("总轮次", st.session_state.turn_count)
        if st.session_state.user_preference:
            st.info(f"选择：{'先生图' if st.session_state.user_preference == 'image_first' else '先角色信息'}")
        
        st.markdown("---")
        
        # 按钮状态
        st.subheader("🔘 按钮状态")
        
        if st.session_state.show_image_button:
            st.success("🎨 生图按钮：显示中")
        else:
            st.warning("🎨 生图按钮：未显示")
        
        if st.session_state.show_profile_button:
            st.success("📝 角色信息按钮：显示中")
        else:
            st.warning("📝 角色信息按钮：未显示")
        
        if st.session_state.show_confirm_button:
            st.success("✅ 确认按钮：显示中")
        else:
            st.warning("✅ 确认按钮：未显示")
        
        st.markdown("---")
        
        # 进度追踪
        st.subheader("创建进度")
        
        if st.session_state.image_generated:
            st.success("✅ 图像已生成")
        else:
            st.warning("⏳ 图像待生成")
        
        if st.session_state.profile_generated:
            st.success("✅ 角色信息已生成")
        else:
            st.warning("⏳ 角色信息待生成")
        
        st.markdown("---")
        
        # 已收集的信息
        with st.expander("📊 已收集的信息"):
            st.json(st.session_state.collected_info)
        
        st.markdown("---")
        
        # 重置按钮
        if st.button("🔄 重新开始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # 主界面
    st.title("🎨 AI 角色创建助手")
    st.caption("让我们一起创建一个独特的 AI 陪伴角色吧！")
    
    # 如果进入聊天模式，显示聊天界面
    if st.session_state.state == "CHAT_MODE":
        chat_with_character()
        return
    
    # 如果已完成，显示完成界面
    if st.session_state.state == "COMPLETED":
        finalize_character()
        return
    
    # 对话历史显示
    st.markdown("---")
    
    # 显示历史对话，并在最后一条 AI 消息后显示按钮
    for idx, msg in enumerate(st.session_state.conversation_history):
        if msg["role"] == "user":
            with st.chat_message("user", avatar="😊"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                # 显示消息内容（移除 [IMAGE] 标记）
                content = msg["content"].replace("[IMAGE]", "").strip()
                if content:
                    st.markdown(content)
                
                # 如果消息包含图片，显示图片
                if msg.get("has_image") and st.session_state.image_url:
                    st.image(st.session_state.image_url, caption="生成的角色图像", use_column_width=True)
            
            # 判断是否在最后一条 AI 消息后显示按钮
            is_last_assistant = (idx == len(st.session_state.conversation_history) - 1)
            
            if is_last_assistant:
                # 显示按钮（在对话框下方）
                cols = st.columns(3)
                
                # 按钮1：帮我生图
                with cols[0]:
                    if st.session_state.show_image_button:
                        if st.button("🎨 帮我生图", key=f"btn_image_{idx}", type="primary"):
                            generate_image_from_description()
                
                # 按钮2：生成角色信息
                with cols[1]:
                    if st.session_state.show_profile_button:
                        if st.button("📝 生成角色信息", key=f"btn_profile_{idx}", type="primary"):
                            generate_profile_from_conversation()
                
                # 按钮3：确认创建
                with cols[2]:
                    if st.session_state.show_confirm_button:
                        if st.button("✅ 确认创建", key=f"btn_confirm_{idx}", type="primary"):
                            finalize_character()
    
    # 用户输入
    st.markdown("---")
    user_input = st.chat_input("在这里输入你的想法...")
    
    if user_input:
        # 处理用户输入并更新状态
        process_user_input(user_input)
        
        # 显示用户消息
        with st.chat_message("user", avatar="😊"):
            st.markdown(user_input)
        
        # 流式显示 AI 回复
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 流式获取回复
            for chunk in get_assistant_response_stream(user_input):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # 添加助手回复到历史
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        # 提取信息
        st.session_state.collected_info = extract_info_from_conversation()
        
        # 更新按钮可见性
        update_button_visibility()
        
        # 强制刷新以显示按钮
        st.rerun()


if __name__ == "__main__":
    main()

