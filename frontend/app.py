import gradio as gr
import requests
import os
import json
from vosk import Model, KaldiRecognizer
import wave

API_URL = "http://localhost:8000"  # 后端地址

# 登录函数
def login_user(username, password):
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
        res.raise_for_status()
        user_data = res.json()
        user_id = user_data["user_id"]
        
        # 登录成功后立即加载对话列表
        conversations = get_user_conversations(user_id)
        choices = []
        default_conversation_id = None
        
        for conv in conversations:
            title = f"{conv['title']} ({conv['message_count']}条消息)"
            choices.append((title, conv['id']))
            if conv['title'] == "默认对话":
                default_conversation_id = conv['id']
        
        # 如果没有默认对话，选择第一个对话
        if not default_conversation_id and choices:
            default_conversation_id = choices[0][1]
        
        # 加载API key列表
        api_keys = get_user_api_keys(user_id)
        api_key_choices = []
        for key in api_keys:
            display_text = f"{key['provider']}"
            if key['model_name']:
                display_text += f" ({key['model_name']})"
            api_key_choices.append((display_text, key['id']))
        
        return (
            user_id,
            f"✅ 登录成功，欢迎 {username}",
            gr.update(visible=False),  # 隐藏登录框
            gr.update(visible=True),   # 显示聊天区
            gr.update(visible=True),   # 显示退出按钮
            gr.update(choices=choices, value=default_conversation_id),  # 更新对话列表
            default_conversation_id,  # 设置默认对话ID
            gr.update(choices=api_key_choices, value=None)  # 更新API key列表
        )
    except Exception as e:
        return None, f"❌ 登录失败: {str(e)}", gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(choices=[], value=None), None, gr.update(choices=[], value=None)

# 注册函数
def register_user(username, password, confirm_password):
    if not username or not password:
        return "❌ 用户名和密码不能为空"
    if password != confirm_password:
        return "❌ 两次输入的密码不一致"
    try:
        res = requests.post(f"{API_URL}/auth/register", json={"username": username, "password": password})
        res.raise_for_status()
        return "✅ 注册成功，请登录"
    except Exception as e:
        return f"❌ 注册失败: {str(e)}"

# 退出登录函数
def logout_user():
    return None, "✅ 已退出登录", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(choices=[], value=None), None, gr.update(choices=[], value=None)

# 获取模型列表
def get_models():
    try:
        res = requests.get(f"{API_URL}/models")
        data = res.json()
        print(data)
        # 返回所有模型列表（保持向后兼容）
        return data.get("all_models", ["None"])
    except:
        return ["None"]

# 获取分类模型列表
def get_categorized_models():
    try:
        res = requests.get(f"{API_URL}/models")
        data = res.json()
        local_models = data.get("local_models", [])
        online_models = data.get("online_models", [])
        
        categorized_models = []
        for model in local_models:
            categorized_models.append(f"🖥️ {model}")
        for model in online_models:
            categorized_models.append(f"🌐 {model}")
        
        # 确保至少有一个默认选项
        if not categorized_models:
            categorized_models = ["🖥️ openai"]
        
        return categorized_models
    except:
        return ["🖥️ openai"]

# 获取默认模型
def get_default_model():
    try:
        models = get_categorized_models()
        return models[0] if models else "🖥️ openai"
    except:
        return "🖥️ openai"

# 获取用户对话列表
def get_user_conversations(user_id):
    if not user_id:
        return []
    try:
        res = requests.get(f"{API_URL}/conversations/user/{user_id}")
        data = res.json()
        conversations = data.get("conversations", [])
        return conversations
    except:
        return []

# 获取用户API keys
def get_user_api_keys(user_id):
    if not user_id:
        return []
    try:
        res = requests.get(f"{API_URL}/api-keys/user/{user_id}")
        data = res.json()
        api_keys = data.get("api_keys", [])
        return api_keys
    except:
        return []

# 创建API key
def create_api_key(user_id, provider, api_key, model_name=None):
    if not user_id or not provider or not api_key:
        return None, "❌ 用户ID、提供商和API key不能为空"
    try:
        payload = {
            "user_id": user_id,
            "provider": provider,
            "api_key": api_key,
            "model_name": model_name
        }
        res = requests.post(f"{API_URL}/api-keys/", json=payload)
        res.raise_for_status()
        data = res.json()
        return data, f"✅ {provider} API key 创建成功"
    except Exception as e:
        return None, f"❌ 创建API key失败: {str(e)}"

# 删除API key
def delete_api_key(api_key_id, user_id):
    if not api_key_id or not user_id:
        return "❌ 参数错误"
    try:
        res = requests.delete(f"{API_URL}/api-keys/{api_key_id}?user_id={user_id}")
        res.raise_for_status()
        return "✅ API key删除成功"
    except Exception as e:
        return f"❌ 删除API key失败: {str(e)}"

# 创建新对话
def create_new_conversation(user_id, title):
    if not user_id or not title:
        return None, "❌ 用户ID和标题不能为空"
    try:
        payload = {
            "user_id": user_id,
            "title": title
        }
        res = requests.post(f"{API_URL}/conversations/", json=payload)
        res.raise_for_status()
        data = res.json()
        return data, f"✅ 对话 '{title}' 创建成功"
    except Exception as e:
        return None, f"❌ 创建对话失败: {str(e)}"

# 删除对话
def delete_conversation(conversation_id, user_id):
    if not conversation_id or not user_id:
        return "❌ 参数错误"
    try:
        res = requests.delete(f"{API_URL}/conversations/{conversation_id}?user_id={user_id}")
        res.raise_for_status()
        return "✅ 对话删除成功"
    except Exception as e:
        return f"❌ 删除对话失败: {str(e)}"

# 控制 RAG 上传文件显示
def toggle_rag_upload(rag_enabled):
    return gr.update(visible=rag_enabled)

# 切换登录注册界面
def switch_to_register():
    return gr.update(visible=False), gr.update(visible=True)

def switch_to_login():
    return gr.update(visible=True), gr.update(visible=False)

# 文件上传接口
def upload_file(file, user_id):
    if not file or not user_id:
        return "❗ 请先登录并选择文件"
    try:
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f)}
            res = requests.post(f"{API_URL}/rag/upload?user_id={user_id}", files=files)
            res.raise_for_status()
        return f"✅ 文件上传成功: {file.name}"
    except Exception as e:
        return f"❌ 上传失败: {str(e)}"

# 发送聊天消息（流式版本）
def send_message_stream(message, user_id, conversation_id, mode, model, use_rag, history):
    if not message or not user_id or not conversation_id:
        yield history
        return
    
    # 清理输入消息
    message = message.strip()
    if not message:
        yield history
        return
    
    history = history or []
    
    # 添加用户消息到历史记录
    history.append({"role": "user", "content": message})  # 用户消息
    
    # 处理模型名称，移除前缀和清理格式
    clean_model = model.strip()  # 移除首尾空格
    if clean_model.startswith("🖥️ "):
        clean_model = clean_model[2:].strip()  # 移除 "🖥️ " 前缀并再次清理空格
    elif clean_model.startswith("🌐 "):
        clean_model = clean_model[2:].strip()  # 移除 "🌐 " 前缀并再次清理空格
    
    clean_model = clean_model.strip()
    
    payload = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message": message,
        "model": clean_model,
        "mode": mode.lower(),       # "chat" or "generate"
        "use_rag": use_rag
    }
    
    try:
        # 显示加载状态
        history.append({"role": "assistant", "content": "🤖 正在思考中..."})
        yield history
        
        # 使用流式接口
        import requests
        response = requests.post(f"{API_URL}/chat/stream", json=payload, stream=True, timeout=60)
        response.raise_for_status()
        
        # 移除加载状态
        history.pop()
        
        # 初始化AI回复
        ai_response = ""
        history.append({"role": "assistant", "content": ai_response})
        yield history
        
        # 处理流式响应
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # 移除 'data: ' 前缀
                        
                        if 'error' in data:
                            # 处理错误
                            history.pop()
                            history.append({"role": "assistant", "content": f"❌ {data['error']}"})
                            yield history
                            break
                        
                        if 'chunk' in data:
                            chunk = data['chunk']
                            ai_response += chunk
                            # 更新历史记录中的AI回复
                            history[-1] = {"role": "assistant", "content": ai_response}
                            yield history
                        
                        if data.get('done', False):
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
    except requests.exceptions.Timeout:
        history.pop()  # 移除"正在思考中..."
        history.append({"role": "assistant", "content": "❌ 请求超时，请稍后重试"})
        yield history
    except requests.exceptions.RequestException as e:
        history.pop()  # 移除"正在思考中..."
        history.append({"role": "assistant", "content": f"❌ 网络请求失败：{str(e)}"})
        yield history
    except Exception as e:
        history.pop()  # 移除"正在思考中..."
        history.append({"role": "assistant", "content": f"❌ 处理失败：{str(e)}"})
        yield history

# 加载对话历史
def load_conversation_history(conversation_id, user_id):
    if not conversation_id or not user_id:
        return []
    
    try:
        # 这里需要后端提供获取对话历史的接口
        # 暂时返回空历史，后续可以扩展
        return []
    except Exception as e:
        print(f"加载对话历史失败: {str(e)}")
        return []

# 语音转文字
def transcribe(audio_path):
    try:
        # 检查模型是否存在
        model_path = "vosk-model-small-cn-0.22"  # 根据你下载的模型调整
        if not os.path.exists(model_path):
            return "❌ 请先下载 Vosk 中文模型到项目目录"
        
        # 加载模型
        model = Model(model_path)
        
        # 读取音频
        wf = wave.open(audio_path, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        
        # 识别
        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text += result.get('text', '')
        
        # 最终结果
        final_result = json.loads(rec.FinalResult())
        text += final_result.get('text', '')
        
        return text.strip() if text.strip() else "未识别到语音"
        
    except Exception as e:
        return f"❌ 语音识别失败: {str(e)}"

# === Gradio UI ===
with gr.Blocks(
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1600px !important;
        margin: 0 auto !important;
    }
    .chatbot {
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
    }
    .chatbot .message {
        border-radius: 15px !important;
        margin: 6px 0 !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
        padding: 8px 12px !important;
    }
    .chatbot .message.user {
        background-color: #007bff !important;
        color: white !important;
        margin-left: 20% !important;
    }
    .chatbot .message.bot {
        background-color: #f8f9fa !important;
        color: #333 !important;
        margin-right: 20% !important;
    }
    .chatbot .message .content {
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    .chatbot .message p {
        font-size: 13px !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }
    .chatbot .message div {
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    .chatbot .message span {
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    .chatbot * {
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    .send-btn {
        height: 100% !important;
        border-radius: 8px !important;
    }
    .input-box {
        border-radius: 8px !important;
    }
    .conversation-list {
        max-height: 400px !important;
        overflow-y: auto !important;
    }
    .sidebar {
        background-color: #f8f9fa !important;
        border-radius: 10px !important;
        padding: 15px !important;
        border: 1px solid #e0e0e0 !important;
    }
    .main-chat-area {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 20px !important;
        border: 1px solid #e0e0e0 !important;
    }
    .audio-input .audio-component input {
        height: 40px !important;
        max-height: 40px !important;
    }
    .collapsible-section {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        background-color: #fafafa !important;
    }
    .toggle-btn {
        border-radius: 6px !important;
        font-size: 12px !important;
        padding: 6px 12px !important;
    }
    .toggle-btn:hover {
        background-color: #e9ecef !important;
    }
    """
) as demo:
    gr.Markdown("## 🧠 OmniSage")
    # gr.Markdown("## 🧠 全知智者")

    user_id = gr.State()
    conversation_id = gr.State()
    login_status = gr.Markdown("请登录")
    
    # 折叠状态跟踪
    api_key_visible = gr.State(False)
    audio_visible = gr.State(False)

    # === 登录区 ===
    with gr.Column(visible=True) as login_area:
        # 登录表单
        with gr.Column(visible=True) as login_form:
            username = gr.Textbox(label="用户名")
            password = gr.Textbox(label="密码", type="password")
            login_btn = gr.Button("登录", variant="primary")
            switch_to_register_btn = gr.Button("没有账户？点击注册", variant="secondary")
        
        # 注册表单
        with gr.Column(visible=False) as register_form:
            reg_username = gr.Textbox(label="用户名")
            reg_password = gr.Textbox(label="密码", type="password")
            reg_confirm_password = gr.Textbox(label="确认密码", type="password")
            register_btn = gr.Button("注册", variant="primary")
            switch_to_login_btn = gr.Button("已有账户？点击登录", variant="secondary")
            register_status = gr.Markdown()

    # === 聊天区 ===
    with gr.Column(visible=False) as chat_area:
        with gr.Row():
            # 左侧：对话管理
            with gr.Column(scale=1, elem_classes="sidebar") as sidebar:
                gr.Markdown("### 💬 对话管理")
                
                # 新建对话
                with gr.Row():
                    new_conversation_title = gr.Textbox(
                        placeholder="输入对话标题...",
                        label="新对话标题",
                        scale=3
                    )
                    new_conversation_btn = gr.Button("新建", variant="primary", scale=1)
                
                new_conversation_status = gr.Markdown()
                
                # 对话列表
                gr.Markdown("**我的对话**")
                conversation_list = gr.Dropdown(
                    choices=[],
                    label="选择对话",
                    interactive=True
                )
                
                with gr.Row():
                    delete_conversation_btn = gr.Button("删除对话", variant="stop", size="sm")
                    refresh_conversations_btn = gr.Button("刷新", variant="secondary", size="sm")
                
                delete_status = gr.Markdown()
            
            # 中间：聊天界面 (最大化宽度)
            with gr.Column(scale=6, elem_classes="main-chat-area") as main_chat:
                # 聊天历史显示区域
                chatbot = gr.Chatbot(
                    height=350,
                    show_label=False,
                    container=True,
                    type="messages",
                    avatar_images=["👤", "🧠"],
                    show_copy_button=True
                )
                
                # 输入区域
                with gr.Row():
                    with gr.Column(scale=8):
                        msg = gr.Textbox(
                            placeholder="请输入内容...",
                            show_label=False,
                            lines=2,
                            max_lines=4
                        )
                    with gr.Column(scale=1):
                        send_btn = gr.Button("发送", variant="primary", size="lg")
            
            # 右侧：控制栏
            with gr.Column(scale=1, elem_classes="sidebar") as control_sidebar:
                gr.Markdown("### ⚙️ 控制面板")
                
                # 对话模式
                mode = gr.Radio(choices=["Chat", "Generate"], label="对话模式", value="Chat")
                
                # 启用RAG
                use_rag = gr.Checkbox(label="启用 RAG", value=False)
                
                # 模型选择
                model = gr.Dropdown(choices=get_categorized_models(), label="模型", value=get_default_model())
                
                # 高级功能折叠区域
                gr.Markdown("**🔧 高级功能**")
                
                # API Key管理折叠
                with gr.Column(visible=False, elem_classes="collapsible-section") as api_key_section:
                    gr.Markdown("**🔑 API Key管理**")
                    
                    with gr.Row():
                        api_provider = gr.Dropdown(
                            choices=["deepseek", "openai", "anthropic", "google"],
                            label="提供商",
                            value="deepseek"
                        )
                    
                    api_key_input = gr.Textbox(
                        label="API Key",
                        type="password",
                        placeholder="输入你的API key..."
                    )
                    
                    api_model_name = gr.Textbox(
                        label="模型名称（可选）",
                        placeholder="如：deepseek-chat, gpt-4..."
                    )
                    
                    with gr.Row():
                        add_api_key_btn = gr.Button("添加", variant="primary", size="sm")
                        refresh_api_keys_btn = gr.Button("刷新", variant="secondary", size="sm")
                    
                    api_key_status = gr.Markdown()
                    
                    # API Key列表
                    api_key_list = gr.Dropdown(
                        choices=[],
                        label="我的API Keys",
                        interactive=True
                    )
                    
                    delete_api_key_btn = gr.Button("删除选中", variant="stop", size="sm")
                    delete_api_key_status = gr.Markdown()
                
                # 音频输入折叠
                with gr.Column(visible=False, elem_classes="collapsible-section") as audio_section:
                    gr.Markdown("**🎤 语音输入**")
                    mic = gr.Audio(type="filepath", label="录音", show_label=True)
                
                # 控制按钮
                with gr.Row():
                    toggle_api_key_btn = gr.Button("🔑 API Key", variant="secondary", size="sm", scale=1, elem_classes="toggle-btn")
                    toggle_audio_btn = gr.Button("🎤 语音", variant="secondary", size="sm", scale=1, elem_classes="toggle-btn")
                
                # RAG文件上传区域
                with gr.Column(visible=False) as rag_upload:
                    file_input = gr.File(label="上传文档")
                    upload_status = gr.Markdown()

    logout_btn = gr.Button("退出登录", visible=False, variant="stop")

    # === 事件绑定 ===
    login_btn.click(
        login_user,
        inputs=[username, password],
        outputs=[user_id, login_status, login_area, chat_area, logout_btn, conversation_list, conversation_id, api_key_list]
    )

    # 注册相关事件
    register_btn.click(
        register_user,
        inputs=[reg_username, reg_password, reg_confirm_password],
        outputs=[register_status]
    )
    
    # 切换界面
    switch_to_register_btn.click(
        switch_to_register,
        outputs=[login_form, register_form]
    )
    
    switch_to_login_btn.click(
        switch_to_login,
        outputs=[login_form, register_form]
    )

    logout_btn.click(
        logout_user,
        outputs=[user_id, login_status, login_area, chat_area, logout_btn, conversation_list, conversation_id, api_key_list]
    )

    # 新建对话
    def create_conversation_and_update(user_id, title):
        """创建新对话并更新列表"""
        if not title.strip():
            return gr.update(choices=[], value=None), "❌ 请输入对话标题", gr.update(value=""), None
        
        conversation_data, status_msg = create_new_conversation(user_id, title.strip())
        
        if conversation_data:
            # 更新对话列表
            conversations = get_user_conversations(user_id)
            choices = []
            for conv in conversations:
                title_text = f"{conv['title']} ({conv['message_count']}条消息)"
                choices.append((title_text, conv['id']))
            
            return gr.update(choices=choices, value=conversation_data['id']), status_msg, gr.update(value=""), conversation_data['id']
        else:
            return gr.update(choices=[], value=None), status_msg, gr.update(value=""), None
    
    new_conversation_btn.click(
        create_conversation_and_update,
        inputs=[user_id, new_conversation_title],
        outputs=[conversation_list, new_conversation_status, new_conversation_title, conversation_id]
    )
    
    # 删除对话
    def delete_conversation_and_update(conversation_id, user_id):
        """删除对话并更新列表"""
        status_msg = delete_conversation(conversation_id, user_id)
        
        if "成功" in status_msg:
            # 更新对话列表
            conversations = get_user_conversations(user_id)
            choices = []
            default_conversation_id = None
            
            for conv in conversations:
                title = f"{conv['title']} ({conv['message_count']}条消息)"
                choices.append((title, conv['id']))
                if conv['title'] == "默认对话":
                    default_conversation_id = conv['id']
            
            return gr.update(choices=choices, value=default_conversation_id), status_msg, default_conversation_id
        else:
            return gr.update(choices=[], value=None), status_msg, None
    
    delete_conversation_btn.click(
        delete_conversation_and_update,
        inputs=[conversation_id, user_id],
        outputs=[conversation_list, delete_status, conversation_id]
    )
    
    # 刷新对话列表
    def refresh_conversations(user_id):
        """刷新对话列表"""
        conversations = get_user_conversations(user_id)
        choices = []
        current_value = None
        
        for conv in conversations:
            title = f"{conv['title']} ({conv['message_count']}条消息)"
            choices.append((title, conv['id']))
            if conv['title'] == "默认对话":
                current_value = conv['id']
        
        return gr.update(choices=choices, value=current_value)
    
    refresh_conversations_btn.click(
        refresh_conversations,
        inputs=[user_id],
        outputs=[conversation_list]
    )
    
    # 切换对话
    def on_conversation_change(conversation_id):
        """切换对话时清空聊天历史"""
        return conversation_id, []  # 返回空的消息列表
    
    conversation_list.change(
        on_conversation_change,
        inputs=[conversation_list],
        outputs=[conversation_id, chatbot]
    )

    use_rag.change(toggle_rag_upload, inputs=use_rag, outputs=rag_upload)

    file_input.upload(upload_file, inputs=[file_input, user_id], outputs=upload_status)

    # 发送消息的两种方式：回车和点击按钮
    def send_and_clear(message, user_id, conversation_id, mode, model, use_rag, history):
        """发送消息并清空输入框"""
        if not message.strip():
            return history, ""
        
        # 使用流式处理
        for updated_history in send_message_stream(message, user_id, conversation_id, mode, model, use_rag, history):
            yield updated_history, ""
    
    # 回车发送
    msg.submit(
        send_and_clear,
        inputs=[msg, user_id, conversation_id, mode, model, use_rag, chatbot],
        outputs=[chatbot, msg]
    )
    
    # 按钮发送
    send_btn.click(
        send_and_clear,
        inputs=[msg, user_id, conversation_id, mode, model, use_rag, chatbot],
        outputs=[chatbot, msg]
    )

    mic.change(transcribe, inputs=mic, outputs=msg)

    # 折叠控制函数
    def toggle_api_key_section(current_visible):
        """切换API Key管理区域的显示状态"""
        new_visible = not current_visible
        return new_visible, gr.update(visible=new_visible)
    
    def toggle_audio_section(current_visible):
        """切换音频输入区域的显示状态"""
        new_visible = not current_visible
        return new_visible, gr.update(visible=new_visible)
    
    # 折叠控制事件
    toggle_api_key_btn.click(
        toggle_api_key_section,
        inputs=[api_key_visible],
        outputs=[api_key_visible, api_key_section]
    )
    
    toggle_audio_btn.click(
        toggle_audio_section,
        inputs=[audio_visible],
        outputs=[audio_visible, audio_section]
    )

    # API Key管理事件
    def add_api_key_and_update(user_id, provider, api_key, model_name):
        """添加API key并更新列表"""
        if not api_key.strip():
            return gr.update(choices=[], value=None), "❌ 请输入API key", gr.update(value=""), gr.update(value="")
        
        api_key_data, status_msg = create_api_key(user_id, provider, api_key.strip(), model_name.strip() if model_name else None)
        
        if api_key_data:
            # 更新API key列表
            api_keys = get_user_api_keys(user_id)
            choices = []
            for key in api_keys:
                display_text = f"{key['provider']}"
                if key['model_name']:
                    display_text += f" ({key['model_name']})"
                choices.append((display_text, key['id']))
            
            return gr.update(choices=choices, value=api_key_data['id']), status_msg, gr.update(value=""), gr.update(value="")
        else:
            return gr.update(choices=[], value=None), status_msg, gr.update(value=""), gr.update(value="")
    
    add_api_key_btn.click(
        add_api_key_and_update,
        inputs=[user_id, api_provider, api_key_input, api_model_name],
        outputs=[api_key_list, api_key_status, api_key_input, api_model_name]
    )
    
    # 刷新API key列表
    def refresh_api_keys(user_id):
        """刷新API key列表"""
        api_keys = get_user_api_keys(user_id)
        choices = []
        
        for key in api_keys:
            display_text = f"{key['provider']}"
            if key['model_name']:
                display_text += f" ({key['model_name']})"
            choices.append((display_text, key['id']))
        
        return gr.update(choices=choices, value=None)
    
    refresh_api_keys_btn.click(
        refresh_api_keys,
        inputs=[user_id],
        outputs=[api_key_list]
    )
    
    # 删除API key
    def delete_api_key_and_update(api_key_id, user_id):
        """删除API key并更新列表"""
        status_msg = delete_api_key(api_key_id, user_id)
        
        if "成功" in status_msg:
            # 更新API key列表
            api_keys = get_user_api_keys(user_id)
            choices = []
            
            for key in api_keys:
                display_text = f"{key['provider']}"
                if key['model_name']:
                    display_text += f" ({key['model_name']})"
                choices.append((display_text, key['id']))
            
            return gr.update(choices=choices, value=None), status_msg
        else:
            return gr.update(choices=[], value=None), status_msg
    
    delete_api_key_btn.click(
        delete_api_key_and_update,
        inputs=[api_key_list, user_id],
        outputs=[api_key_list, delete_api_key_status]
    )

demo.launch()
