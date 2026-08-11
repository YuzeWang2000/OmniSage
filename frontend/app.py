import gradio as gr
import requests
import os
import json
from concurrent.futures import ThreadPoolExecutor
from vosk import Model, KaldiRecognizer
import wave

# API_URL = "http://localhost:8000"  # 后端地址
API_URL = os.getenv("API_URL", "http://localhost:8000")
# 登录函数
def login_user(username, password):
    try:
        res = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        res.raise_for_status()
        user_data = res.json()
        user_id = user_data["user_id"]
        
        # 三组互不依赖的数据并行加载，避免登录后串行等待多个接口。
        with ThreadPoolExecutor(max_workers=3) as executor:
            conversations_future = executor.submit(get_user_conversations, user_id)
            api_keys_future = executor.submit(get_user_api_keys, user_id)
            knowledge_bases_future = executor.submit(fetch_user_knowledge_bases, user_id)
            conversations = conversations_future.result()
            api_keys = api_keys_future.result()
            knowledge_base_data = knowledge_bases_future.result()

        default_conversation_id = None
        
        for conv in conversations:
            if conv['title'] == "默认对话":
                default_conversation_id = conv['id']
        
        # 如果没有默认对话，选择第一个对话
        if not default_conversation_id and conversations:
            default_conversation_id = conversations[0]["id"]

        recent_choices, more_choices = split_conversation_choices(
            conversations, default_conversation_id
        )
        
        # 首页登录不需要立即读取消息，进入聊天页时再按需加载。
        chat_history = []

        api_key_choices = []
        for key in api_keys:
            display_text = f"{key['provider']}"
            if key['model_name']:
                display_text += f" ({key['model_name']})"
            api_key_choices.append((display_text, key['id']))
        
        knowledge_bases = format_knowledge_base_choices(knowledge_base_data)
        search_knowledge_bases = format_knowledge_base_choices(
            knowledge_base_data, compact=True
        )
        
        return (
            user_id,
            f"**{username}**",
            f"✅ 登录成功，欢迎 {username}",
            gr.update(visible=False),  # 隐藏登录框
            gr.update(visible=True),   # 显示聊天区
            gr.update(visible=True),   # 显示退出按钮
            gr.update(choices=recent_choices, value=default_conversation_id),
            gr.update(choices=more_choices, value=None),
            default_conversation_id,  # 设置默认对话ID
            gr.update(choices=api_key_choices, value=None),  # 更新API key列表
            chat_history,  # 返回聊天历史
            gr.update(choices=knowledge_bases, value=None),  # 更新知识库卡片
            gr.update(choices=search_knowledge_bases, value=None),
        )
    except Exception as e:
        return (None, 
                "",
                f"❌ 登录失败: {str(e)}", 
                gr.update(), 
                gr.update(visible=False), 
                gr.update(visible=False), 
                gr.update(choices=[], value=None), 
                gr.update(choices=[], value=None),
                None, 
                gr.update(choices=[], value=None),
                [],
                gr.update(choices=[], value=None),
                gr.update(choices=[], value=None))

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
    return (None,
             "",
             "✅ 已退出登录", 
             gr.update(visible=True), 
             gr.update(visible=False), 
             gr.update(visible=False), 
             gr.update(choices=[], value=None), 
             gr.update(choices=[], value=None),
             None, 
             gr.update(choices=[], value=None),
             [],
             gr.update(choices=[], value=None),
             gr.update(choices=[], value=None))

# 获取分类模型列表
def get_categorized_models():
    try:
        res = requests.get(f"{API_URL}/models", timeout=10)
        res.raise_for_status()
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
            categorized_models = ["None available models"]
        
        return categorized_models
    except Exception as exc:
        print(f"获取模型列表失败: {exc}")
        return ["None available models"]

# 获取默认模型
def get_default_model():
    try:
        models = get_categorized_models()
        return models[0] if models else "None available models"
    except:
        return "None available models"

# 获取用户对话列表
def get_user_conversations(user_id):
    if not user_id:
        return []
    try:
        res = requests.get(f"{API_URL}/conversations/user/{user_id}", timeout=10)
        res.raise_for_status()
        data = res.json()
        conversations = data.get("conversations", [])
        return conversations
    except:
        return []


RECENT_CONVERSATION_LIMIT = 8


def split_conversation_choices(conversations, selected_id=None):
    """将聊天历史拆成常用列表和“查看更多”下拉列表。"""
    all_choices = [(conv["title"], conv["id"]) for conv in conversations]
    recent_choices = all_choices[:RECENT_CONVERSATION_LIMIT]

    # 从“查看更多”选择旧对话后，把它临时提升到可见列表，方便继续
    # 使用左侧列表的右键重命名、删除功能。
    if selected_id and all(value != selected_id for _, value in recent_choices):
        selected_choice = next(
            (choice for choice in all_choices if choice[1] == selected_id), None
        )
        if selected_choice:
            recent_choices = [selected_choice] + recent_choices[
                : RECENT_CONVERSATION_LIMIT - 1
            ]

    recent_ids = {value for _, value in recent_choices}
    more_choices = [
        choice for choice in all_choices if choice[1] not in recent_ids
    ]
    return recent_choices, more_choices

# 获取用户API keys
def get_user_api_keys(user_id):
    if not user_id:
        return []
    try:
        res = requests.get(f"{API_URL}/api-keys/user/{user_id}", timeout=10)
        res.raise_for_status()
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


def rename_conversation(conversation_id, user_id, title):
    """更新对话标题。"""
    if not conversation_id or not user_id or not (title or "").strip():
        return "❌ 对话标题不能为空"
    try:
        res = requests.patch(
            f"{API_URL}/conversations/{conversation_id}",
            json={"user_id": user_id, "title": title.strip()},
            timeout=10,
        )
        res.raise_for_status()
        return "✅ 对话重命名成功"
    except Exception as exc:
        return f"❌ 对话重命名失败: {exc}"

# 控制 RAG 上传文件显示
def toggle_rag_upload(rag_enabled):
    return gr.update(visible=rag_enabled)

# 切换登录注册界面
def switch_to_register():
    return gr.update(visible=False), gr.update(visible=True)

def switch_to_login():
    return gr.update(visible=True), gr.update(visible=False)


def search_content(query, source, knowledge_base_id, user_id):
    """Search Wiki or one user-selected knowledge base."""
    query = (query or "").strip()
    if not query:
        return "请输入要搜索的内容。"

    try:
        if source == "指定知识库":
            if not user_id:
                return "请先登录。"
            if not knowledge_base_id:
                return "请选择要搜索的知识库。"
            res = requests.get(
                f"{API_URL}/rag/knowledge-bases/{knowledge_base_id}/search",
                params={"user_id": user_id, "query": query, "top_k": 5},
                timeout=30,
            )
            res.raise_for_status()
            data = res.json()
            results = data.get("results", [])
            if not results:
                return f"未在 **{data.get('knowledge_base_name', '所选知识库')}** 中找到相关内容。"
            items = [
                f"### {index}\n\n{item.get('content', '')}"
                for index, item in enumerate(results, start=1)
            ]
            return "## 搜索结果\n\n" + "\n\n---\n\n".join(items)

        res = requests.get(
            f"{API_URL}/rag/enhance-context-with-wiki",
            params={"query": query}, timeout=30,
        )
        res.raise_for_status()
        context = (res.json().get("enhanced_context") or "").strip()
        return context or f"未找到与 **{query}** 相关的内容。"
    except Exception as exc:
        return f"❌ 搜索失败：{exc}"

# 文件上传接口
# 已废弃的upload_file函数 - 使用upload_file_to_knowledge_base替代
# def upload_file(file, user_id):
#     if not file or not user_id:
#         return "❗ 请先登录并选择文件"
#     try:
#         with open(file.name, "rb") as f:
#             files = {"file": (file.name, f)}
#             res = requests.post(f"{API_URL}/rag/upload?user_id={user_id}", files=files)
#             res.raise_for_status()
#         return f"✅ 文件上传成功: {file.name}"
#     except Exception as e:
#         return f"❌ 上传失败: {str(e)}"

# 知识库管理相关函数
def fetch_user_knowledge_bases(user_id):
    """只请求一次知识库数据，供卡片和搜索选择器共同使用。"""
    if not user_id:
        return []
    try:
        res = requests.get(f"{API_URL}/rag/knowledge-bases/{user_id}", timeout=10)
        res.raise_for_status()
        return res.json().get("knowledge_bases", [])
    except Exception as e:
        print(f"获取知识库列表失败: {str(e)}")
        return []


def format_knowledge_base_choices(knowledge_bases, compact=False):
    choices = []
    for kb in knowledge_bases:
        if compact:
            display_text = kb["name"]
        else:
            description = (kb.get("description") or "暂无描述").strip()
            created_at = str(kb.get("created_at", ""))[:10]
            display_text = (
                f"▣  {kb['name']}\n"
                f"{kb['file_count']} 个文件 · {kb['document_count']} 个文档块\n"
                f"{description}\n{created_at}"
            )
        choices.append((display_text, kb['id']))
    return choices


def get_user_knowledge_bases(user_id, compact=False):
    """获取并格式化用户知识库列表。"""
    return format_knowledge_base_choices(
        fetch_user_knowledge_bases(user_id), compact=compact
    )

def create_knowledge_base(user_id, name, description=""):
    """创建知识库"""
    if not user_id or not name:
        return "❗ 请先登录并输入知识库名称"
    try:
        payload = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "embedding_model": "nomic-embed-text"
        }
        res = requests.post(f"{API_URL}/rag/knowledge-bases", json=payload)
        res.raise_for_status()
        return f"✅ 知识库 '{name}' 创建成功"
    except Exception as e:
        return f"❌ 创建知识库失败: {str(e)}"

def delete_knowledge_base(knowledge_base_id, user_id):
    """删除知识库"""
    if not knowledge_base_id or not user_id:
        return "❗ 请先选择要删除的知识库"
    try:
        res = requests.delete(f"{API_URL}/rag/knowledge-bases/{knowledge_base_id}?user_id={user_id}")
        res.raise_for_status()
        return f"✅ 知识库删除成功"
    except Exception as e:
        return f"❌ 删除知识库失败: {str(e)}"

def upload_file_to_knowledge_base(file, knowledge_base_id, user_id):
    """上传文件到指定知识库"""
    if not file or not knowledge_base_id or not user_id:
        return "❗ 请先选择知识库和文件"
    try:
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f)}
            res = requests.post(f"{API_URL}/rag/knowledge-bases/{knowledge_base_id}/files?user_id={user_id}", files=files)
            res.raise_for_status()
            data = res.json()
            return f"✅ 文件上传成功: {file.name} (生成了{data.get('chunks', 0)}个文档块)"
    except Exception as e:
        return f"❌ 上传失败: {str(e)}"

def get_knowledge_base_files(knowledge_base_id, user_id):
    """获取知识库的文件列表"""
    if not knowledge_base_id or not user_id:
        return []
    try:
        res = requests.get(f"{API_URL}/rag/knowledge-bases/{knowledge_base_id}/files?user_id={user_id}")
        res.raise_for_status()
        data = res.json()
        files = data.get("files", [])
        
        choices = []
        for file_info in files:
            # 只显示文件名，不显示完整路径
            filename = os.path.basename(file_info['original_filename'])
            display_text = f"{filename} ({file_info['document_count']}个文档块)"
            choices.append((display_text, file_info['id']))
        
        return choices
    except Exception as e:
        print(f"获取文件列表失败: {str(e)}")
        return []

def delete_file_from_knowledge_base(file_id, knowledge_base_id, user_id):
    """从知识库中删除文件"""
    if not file_id or not knowledge_base_id or not user_id:
        return "❗ 请先选择要删除的文件"
    try:
        res = requests.delete(f"{API_URL}/rag/knowledge-bases/{knowledge_base_id}/files/{file_id}?user_id={user_id}")
        res.raise_for_status()
        return f"✅ 文件删除成功"
    except Exception as e:
        return f"❌ 删除文件失败: {str(e)}"

def get_knowledge_base_stats(user_id):
    """获取用户知识库统计信息"""
    if not user_id:
        return "❗ 请先登录"
    try:
        res = requests.get(f"{API_URL}/rag/stats/{user_id}")
        res.raise_for_status()
        data = res.json()
        stats = f"📊 知识库统计: {data.get('total_knowledge_bases', 0)}个知识库, {data.get('total_files', 0)}个文件, {data.get('total_documents', 0)}个文档块"
        return stats
    except Exception as e:
        return f"❌ 获取统计信息失败: {str(e)}"

def get_wiki_status():
    """获取Wiki知识状态"""
    try:
        res = requests.get(f"{API_URL}/rag/wiki/status")
        res.raise_for_status()
        data = res.json()
        
        if data["success"]:
            mode = data["mode"]
            stats = data["stats"]
            
            if mode == "offline":
                total_articles = stats.get("total_articles", 0)
                db_size = stats.get("database_size_mb", 0)
                return f"""
                📚 **Wiki知识状态**
                - 服务类型: 离线模式
                - 文章总数: {total_articles:,}
                - 数据库大小: {db_size:.1f} MB
                - 状态: ✅ 可用
                """
            elif mode == "online":
                return f"""
                📚 **Wiki知识状态**
                - 服务类型: 在线模式
                - 状态: ✅ 可用
                """
            else:
                return f"""
                📚 **Wiki知识状态**
                - 服务类型: {mode}
                - 状态: ⚠️ 异常
                """
        else:
            return "❌ Wiki知识服务不可用"
    except Exception as e:
        return f"❌ 获取Wiki状态失败: {str(e)}"

def switch_wiki_mode(mode):
    """切换Wiki服务模式"""
    try:
        res = requests.post(f"{API_URL}/rag/wiki/switch-mode?mode={mode}")
        res.raise_for_status()
        data = res.json()
        
        if data["success"]:
            return f"✅ {data['message']}"
        else:
            return f"❌ 切换失败: {data.get('detail', '未知错误')}"
    except Exception as e:
        return f"❌ 切换Wiki模式失败: {str(e)}"

# 发送聊天消息（流式版本）
def send_message(message, user_id, conversation_id, mode, model, use_rag, use_wiki, history, stream):
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
        "use_rag": use_rag,
        "use_wiki": use_wiki,       # 添加Wiki知识支持
        "use_reranker": False,
        "stream": stream
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
        # yield history
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
        res = requests.get(f"{API_URL}/conversations/{conversation_id}/messages?user_id={user_id}")
        data = res.json()
        messages = data.get("messages", [])
        
        chat_history = []
        for msg in messages:
            chat_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return chat_history
    except Exception as e:
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
    .tab-btn {
        border-radius: 8px !important;
        font-size: 12px !important;
        padding: 8px 12px !important;
        margin: 2px !important;
        transition: all 0.3s ease !important;
    }
    .tab-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    .tab-btn.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    .tab-btn.secondary {
        background: #f8f9fa !important;
        color: #6c757d !important;
        border: 1px solid #dee2e6 !important;
    }
    .tab-content {
        padding: 15px !important;
        border-radius: 10px !important;
        background: white !important;
        margin-top: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    .sidebar {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    .main-chat-area {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    .chatbot {
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    .send-btn {
        height: 100% !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    .send-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    .input-box {
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        transition: border-color 0.3s ease !important;
    }
    .input-box:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    body, .gradio-container {
        background: #f5f7fb !important;
        color: #18202b !important;
    }
    html, body, #root {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
    }
    .gradio-container {
        width: 100vw !important;
        height: 100vh !important;
        min-width: 1180px !important;
        max-width: none !important;
        padding: 24px 28px 40px !important;
        overflow: auto !important;
    }
    .app-brand h2 {
        margin: 0 0 24px !important;
        color: #121820 !important;
        font-size: 36px !important;
        letter-spacing: -0.02em !important;
        text-align: center !important;
    }
    .login-page {
        min-height: calc(100vh - 64px) !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .login-card {
        width: 420px !important;
        max-width: calc(100vw - 40px) !important;
        padding: 28px !important;
        border: 1px solid #e1e6ed !important;
        border-radius: 20px !important;
        background: #fff !important;
        box-shadow: 0 18px 50px rgba(16, 24, 40, .10) !important;
    }
    .top-nav {
        align-items: center !important;
        gap: 8px !important;
        width: min(900px, 100%) !important;
        margin: 0 auto 26px !important;
        padding: 7px !important;
        border: 1px solid #30343b !important;
        border-radius: 999px !important;
        background: #17191d !important;
        box-shadow: 0 16px 36px rgba(16, 24, 40, 0.16) !important;
    }
    .top-nav > div {
        gap: 8px !important;
    }
    .nav-btn {
        min-width: 0 !important;
        height: 50px !important;
        padding: 0 22px !important;
        border: 0 !important;
        border-radius: 999px !important;
        background: transparent !important;
        color: #f5f7fa !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transition: color .2s ease, background .2s ease, transform .2s ease !important;
    }
    .nav-btn:hover {
        background: #292c31 !important;
        transform: translateY(-1px) !important;
    }
    .nav-btn.primary {
        background: #f7f8fa !important;
        color: #11151a !important;
        box-shadow: inset 0 -3px 0 #21d4c2 !important;
    }
    .legacy-tabs {
        display: none !important;
    }
    .page-shell {
        min-height: 660px !important;
    }
    .welcome-page {
        min-height: 570px !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid #e5e9f0 !important;
        border-radius: 24px !important;
        background: #ffffff !important;
        box-shadow: 0 18px 50px rgba(16, 24, 40, 0.07) !important;
        text-align: center !important;
    }
    .welcome-copy h1 {
        margin: 0 !important;
        color: #111827 !important;
        font-size: clamp(38px, 6vw, 68px) !important;
        line-height: 1.08 !important;
        letter-spacing: -0.045em !important;
    }
    .welcome-user p {
        margin: 18px 0 0 !important;
        color: #667085 !important;
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    .content-card, .sidebar, .main-chat-area {
        border: 1px solid #e3e8ef !important;
        border-radius: 20px !important;
        background: #ffffff !important;
        box-shadow: 0 12px 34px rgba(16, 24, 40, 0.07) !important;
    }
    .content-card {
        padding: 24px !important;
    }
    .sidebar {
        padding: 20px !important;
        background: #ffffff !important;
    }
    .main-chat-area {
        padding: 22px !important;
        background: #ffffff !important;
    }
    .conversation-history {
        max-height: 510px !important;
        overflow-y: auto !important;
    }
    .conversation-history .wrap {
        display: flex !important;
        flex-direction: column !important;
        gap: 4px !important;
    }
    .conversation-history label {
        width: 100% !important;
        padding: 11px 12px !important;
        border: 0 !important;
        border-radius: 9px !important;
        background: transparent !important;
        cursor: pointer !important;
        color: #514a46 !important;
        font-size: 15px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .conversation-history label:hover,
    .conversation-history label:has(input:checked) {
        background: #eef1f5 !important;
        color: #15191f !important;
    }
    .conversation-history input[type="radio"] {
        display: none !important;
    }
    .context-bridge {
        display: none !important;
    }
    #conversation-context-menu {
        position: fixed;
        z-index: 2000;
        min-width: 138px;
        padding: 6px;
        border: 1px solid #dfe3e8;
        border-radius: 10px;
        background: #fff;
        box-shadow: 0 12px 32px rgba(0, 0, 0, .18);
    }
    #conversation-context-menu button {
        width: 100%;
        padding: 9px 12px;
        border: 0;
        border-radius: 7px;
        background: transparent;
        text-align: left;
        cursor: pointer;
    }
    #conversation-context-menu button:hover { background: #f1f3f5; }
    #conversation-context-menu button.danger { color: #d92d20; }
    .chat-action-btn {
        width: 74px !important;
        min-width: 74px !important;
        max-width: 74px !important;
        height: 48px !important;
        padding: 0 10px !important;
        align-self: center !important;
    }
    .voice-trigger {
        width: 48px !important;
        min-width: 48px !important;
        max-width: 48px !important;
        font-size: 20px !important;
    }
    .voice-panel {
        margin-top: 8px !important;
        padding: 14px !important;
        border: 1px solid #dfe4eb !important;
        border-radius: 14px !important;
        background: #f8fafc !important;
    }
    .voice-recorder {
        width: 100% !important;
        min-height: 120px !important;
        overflow: visible !important;
    }
    .settings-panel {
        max-width: 980px !important;
        margin: 0 auto !important;
    }
    .page-title h2 {
        margin-top: 0 !important;
        font-size: 28px !important;
        letter-spacing: -0.02em !important;
    }
    .search-wrap {
        max-width: 920px !important;
        margin: 46px auto 0 !important;
    }
    .search-result {
        min-height: 280px !important;
        margin-top: 16px !important;
        padding: 24px !important;
        border: 1px solid #e3e8ef !important;
        border-radius: 18px !important;
        background: #fff !important;
    }
    .search-source .wrap {
        gap: 10px !important;
    }
    .kb-toolbar {
        align-items: center !important;
        justify-content: space-between !important;
        margin-bottom: 16px !important;
    }
    .kb-create-trigger {
        max-width: 180px !important;
    }
    .kb-grid .wrap {
        display: grid !important;
        grid-template-columns: repeat(3, minmax(260px, 1fr)) !important;
        gap: 16px !important;
        padding: 4px !important;
    }
    .kb-grid label {
        min-height: 150px !important;
        align-items: flex-start !important;
        padding: 18px !important;
        border: 1px solid #dfe4eb !important;
        border-radius: 14px !important;
        background: #fff !important;
        box-shadow: 0 5px 16px rgba(16, 24, 40, .05) !important;
        cursor: pointer !important;
        transition: border-color .2s ease, transform .2s ease, box-shadow .2s ease !important;
    }
    .kb-grid label:hover {
        transform: translateY(-2px) !important;
        border-color: #22b8a9 !important;
        box-shadow: 0 10px 24px rgba(16, 24, 40, .10) !important;
    }
    .kb-grid label:has(input:checked) {
        border-color: #12b8a6 !important;
        box-shadow: 0 0 0 2px rgba(18, 184, 166, .18) !important;
    }
    .kb-grid label > span:last-child {
        white-space: pre-line !important;
        line-height: 1.7 !important;
        font-size: 14px !important;
    }
    .kb-grid input[type="radio"] {
        margin-top: 5px !important;
    }
    .kb-detail {
        margin-top: 22px !important;
        padding: 22px !important;
        border: 1px solid #dfe4eb !important;
        border-radius: 16px !important;
        background: #f9fafb !important;
    }
    .kb-modal {
        position: fixed !important;
        inset: 50% auto auto 50% !important;
        z-index: 1000 !important;
        width: 520px !important;
        max-width: calc(100vw - 40px) !important;
        padding: 24px !important;
        transform: translate(-50%, -50%) !important;
        border: 1px solid #d8dee8 !important;
        border-radius: 18px !important;
        background: #fff !important;
        box-shadow: 0 30px 90px rgba(0, 0, 0, .28) !important;
    }
    .logout-row {
        margin-top: 18px !important;
        justify-content: flex-end !important;
    }
    .logout-btn {
        max-width: 140px !important;
    }
    @media (max-width: 1180px) {
        .gradio-container { padding: 18px !important; }
        .top-nav { border-radius: 22px !important; }
        .nav-btn { height: 44px !important; padding: 0 10px !important; font-size: 14px !important; }
        .welcome-page { min-height: 430px !important; }
        .kb-grid .wrap { grid-template-columns: repeat(2, minmax(260px, 1fr)) !important; }
    }
    """
) as demo:
    user_id = gr.State()
    conversation_id = gr.State()
    
    # === 登录区 ===
    with gr.Column(visible=True, elem_classes="login-page") as login_area:
        gr.Markdown("## ◈ OmniSage", elem_classes="app-brand")
        login_status = gr.Markdown("请登录")
        # 登录表单
        with gr.Column(visible=True, elem_classes="login-card") as login_form:
            username = gr.Textbox(label="用户名")
            password = gr.Textbox(label="密码", type="password")
            login_btn = gr.Button("登录", variant="primary")
            switch_to_register_btn = gr.Button("没有账户？点击注册", variant="secondary")
        
        # 注册表单
        with gr.Column(visible=False, elem_classes="login-card") as register_form:
            reg_username = gr.Textbox(label="用户名")
            reg_password = gr.Textbox(label="密码", type="password")
            reg_confirm_password = gr.Textbox(label="确认密码", type="password")
            register_btn = gr.Button("注册", variant="primary")
            switch_to_login_btn = gr.Button("已有账户？点击登录", variant="secondary")
            register_status = gr.Markdown()

    # === 登录后的应用区 ===
    with gr.Column(visible=False) as chat_area:
        with gr.Row(elem_classes="top-nav"):
            home_nav_btn = gr.Button("⌂  主页", variant="primary", elem_classes="nav-btn")
            knowledge_nav_btn = gr.Button("知识库", variant="secondary", elem_classes="nav-btn")
            chat_nav_btn = gr.Button("聊天", variant="secondary", elem_classes="nav-btn")
            search_nav_btn = gr.Button("搜索", variant="secondary", elem_classes="nav-btn")
            settings_nav_btn = gr.Button("设置", variant="secondary", elem_classes="nav-btn")

        with gr.Column(visible=True, elem_classes="welcome-page") as home_page:
            gr.Markdown("# Welcome to OmniSage", elem_classes="welcome-copy")
            home_username = gr.Markdown(elem_classes="welcome-user")

        with gr.Column(visible=False, elem_classes="search-wrap") as search_page:
            gr.Markdown("## 搜索", elem_classes="page-title")
            gr.Markdown("选择 Wiki 或指定知识库作为搜索范围。")
            search_source = gr.Radio(
                choices=["Wiki", "指定知识库"], value="Wiki",
                label="搜索范围", elem_classes="search-source"
            )
            search_kb_list = gr.Dropdown(
                choices=[], label="选择知识库", visible=False, interactive=True
            )
            with gr.Row():
                search_input = gr.Textbox(
                    placeholder="输入关键词或问题...", show_label=False, scale=8
                )
                search_btn = gr.Button("搜索", variant="primary", scale=1)
            search_result = gr.Markdown(
                "搜索结果将在这里显示。", elem_classes="search-result"
            )

        with gr.Row():
            # 左侧：管理面板
            with gr.Column(visible=False, scale=1, elem_classes="sidebar") as sidebar:
                # 标签页按钮
                with gr.Row(elem_classes="legacy-tabs"):
                    tab_conversation_btn = gr.Button("💬 对话管理", variant="primary", size="sm", elem_classes="tab-btn")
                    tab_knowledge_btn = gr.Button("📚 知识库", variant="secondary", size="sm", elem_classes="tab-btn")
                    tab_settings_btn = gr.Button("⚙️ 设置", variant="secondary", size="sm", elem_classes="tab-btn")
                
                # 对话管理标签页
                with gr.Column(visible=True, elem_classes="tab-content") as conversation_tab:
                    gr.Markdown("### 聊天")
                    new_conversation_btn = gr.Button("＋ 新建对话", variant="primary")
                    new_conversation_status = gr.Markdown()
                    
                    # 对话列表
                    gr.Markdown("**我的对话**")
                    conversation_list = gr.Radio(
                        choices=[],
                        label="聊天历史",
                        show_label=False,
                        interactive=True,
                        elem_classes="conversation-history",
                    )
                    
                    more_conversation_list = gr.Dropdown(
                        choices=[], label="查看更多对话", interactive=True
                    )
                    
                    delete_status = gr.Markdown()

                    # 由右键菜单调用的桥接组件，不占用可见布局。
                    context_conversation_title = gr.Textbox(
                        elem_id="context-conversation-title", elem_classes="context-bridge"
                    )
                    context_rename_btn = gr.Button(
                        "rename", elem_id="context-rename", elem_classes="context-bridge"
                    )
                    context_delete_btn = gr.Button(
                        "delete", elem_id="context-delete", elem_classes="context-bridge"
                    )
            
                # 知识库管理标签页
                with gr.Column(visible=False, elem_classes="tab-content") as knowledge_tab:
                    with gr.Row(elem_classes="kb-toolbar"):
                        gr.Markdown("### ▣ 知识库")
                        with gr.Row():
                            refresh_kb_btn = gr.Button("刷新", variant="secondary", size="sm")
                            open_new_kb_btn = gr.Button(
                                "＋ 新建知识库", variant="primary",
                                elem_classes="kb-create-trigger"
                            )

                    knowledge_base_list = gr.Radio(
                        choices=[], label="我的知识库", show_label=False,
                        interactive=True, elem_classes="kb-grid"
                    )

                    # 只有点击知识库卡片后才显示文件与删除管理。
                    with gr.Column(visible=False, elem_classes="kb-detail") as kb_detail_panel:
                        selected_kb_title = gr.Markdown("### 知识库详情")
                        kb_stats = gr.Markdown()
                        with gr.Row():
                            kb_file_input = gr.File(label="选择文件上传到知识库", scale=4)
                            kb_upload_btn = gr.Button("上传文件", variant="primary", scale=1)
                        kb_upload_status = gr.Markdown()
                        kb_file_list = gr.Dropdown(
                            choices=[], label="知识库文件", interactive=True
                        )
                        with gr.Row():
                            delete_kb_file_btn = gr.Button("删除所选文件", variant="stop", size="sm")
                            delete_kb_btn = gr.Button("删除知识库", variant="stop", size="sm")
                        delete_kb_file_status = gr.Markdown()
                        delete_kb_status = gr.Markdown()

                    # Gradio 5.41 没有原生 Modal，使用固定定位面板实现弹窗。
                    with gr.Column(visible=False, elem_classes="kb-modal") as new_kb_modal:
                        gr.Markdown("### 新建知识库")
                        new_kb_name = gr.Textbox(
                            placeholder="输入知识库名称...", label="知识库名称"
                        )
                        new_kb_description = gr.Textbox(
                            placeholder="知识库描述（可选）...", label="知识库描述", lines=3
                        )
                        with gr.Row():
                            cancel_new_kb_btn = gr.Button("取消", variant="secondary")
                            new_kb_btn = gr.Button("创建", variant="primary")
                        new_kb_status = gr.Markdown()
            
                # 设置标签页
                with gr.Column(visible=False, elem_classes=["tab-content", "settings-panel"]) as settings_tab:
                    gr.Markdown("### ⚙️ 设置")
                    
                    # Wiki知识说明
                    gr.Markdown("""
                    **📚 Wiki知识功能说明**
                    - 启用Wiki知识后，AI会结合维基百科信息回答您的问题
                    - 支持离线模式（本地维基百科数据库）和在线模式
                    - 可以与RAG功能同时使用，提供更全面的知识支持
                    """)
                    
                    # 启用Wiki知识
                    use_wiki = gr.Checkbox(
                        label="启用 Wiki知识", 
                        value=False, 
                        info="使用维基百科知识增强回答。启用后，AI会结合维基百科信息提供更准确的回答。"
                    )
                    
                    # Wiki状态显示
                    with gr.Row():
                        with gr.Column(scale=3):
                            wiki_status = gr.Markdown(get_wiki_status())
                        with gr.Column(scale=1):
                            refresh_wiki_status_btn = gr.Button("🔄 刷新", variant="secondary", size="sm")
                    
                    # Wiki模式切换
                    with gr.Row():
                        with gr.Column(scale=1):
                            switch_to_online_btn = gr.Button("🌐 切换到在线模式", variant="secondary", size="sm")
                        with gr.Column(scale=1):
                            switch_to_offline_btn = gr.Button("💾 切换到离线模式", variant="secondary", size="sm")
                    
                    wiki_switch_status = gr.Markdown()
                
                # 对话模式
                mode = gr.Radio(choices=["Chat", "Generate"], label="对话模式", value="Chat")
                
                # 启用RAG
                use_rag = gr.Checkbox(label="启用 RAG", value=False)
                
                # 模型选择
                model = gr.Dropdown(choices=get_categorized_models(), label="模型", value=get_default_model())
                
                # 高级功能折叠区域
                advanced_title = gr.Markdown("**🔧 高级功能**")
                
                # API Key管理
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
                
            # 右侧：聊天界面
            with gr.Column(visible=False, scale=4, elem_classes="main-chat-area") as main_chat:
                # 聊天历史显示区域
                chatbot = gr.Chatbot(
                    height=500,
                    show_label=False,
                    container=True,
                    type="messages",
                    avatar_images=["👤", "🧠"],
                    show_copy_button=True
                )
                
                # 输入区域
                with gr.Row(equal_height=True):
                    with gr.Column(scale=8):
                        message_input = gr.Textbox(
                            placeholder="请输入内容...",
                            show_label=False,
                            lines=2,
                            max_lines=4
                        )
                    voice_btn = gr.Button(
                        "🎤", variant="secondary", scale=0,
                        elem_classes=["chat-action-btn", "voice-trigger"],
                    )
                    send_btn = gr.Button(
                        "发送", variant="primary", scale=0,
                        elem_classes="chat-action-btn",
                    )
                with gr.Column(visible=False, elem_classes="voice-panel") as voice_panel:
                    mic = gr.Audio(
                        sources=["microphone"], type="filepath",
                        label="语音输入", show_label=True, container=True,
                        elem_classes="voice-recorder",
                    )
                    close_voice_btn = gr.Button("关闭语音输入", variant="secondary", size="sm")

    logout_btn = gr.Button(
        "退出登录", visible=False, variant="secondary", elem_classes="logout-btn"
    )

    # === 事件绑定 ===
    login_btn.click(
        login_user,
        inputs=[username, password],
        outputs=[user_id, home_username, login_status, login_area, chat_area, logout_btn, conversation_list, more_conversation_list, conversation_id, api_key_list, chatbot, knowledge_base_list, search_kb_list]
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
        outputs=[user_id, home_username, login_status, login_area, chat_area, logout_btn, conversation_list, more_conversation_list, conversation_id, api_key_list, chatbot, knowledge_base_list, search_kb_list]
    )

    # 新建对话
    def create_conversation_and_update(user_id):
        """直接创建空白对话，标题由首条消息自动生成。"""
        conversation_data, status_msg = create_new_conversation(user_id, "新对话")
        
        if conversation_data:
            conversations = get_user_conversations(user_id)
            recent_choices, more_choices = split_conversation_choices(
                conversations, conversation_data["id"]
            )
            return (
                gr.update(choices=recent_choices, value=conversation_data['id']),
                gr.update(choices=more_choices, value=None),
                status_msg,
                conversation_data['id'],
                [],
            )
        return gr.update(), gr.update(), status_msg, None, []
    
    new_conversation_btn.click(
        create_conversation_and_update,
        inputs=[user_id],
        outputs=[conversation_list, more_conversation_list, new_conversation_status, conversation_id, chatbot]
    )
    
    # 删除对话
    def delete_conversation_and_update(conversation_id, user_id):
        """删除对话并更新列表"""
        status_msg = delete_conversation(conversation_id, user_id)
        
        if "成功" in status_msg:
            conversations = get_user_conversations(user_id)
            default_conversation_id = (
                conversations[0]["id"] if conversations else None
            )
            recent_choices, more_choices = split_conversation_choices(
                conversations, default_conversation_id
            )
            history = load_conversation_history(default_conversation_id, user_id)
            return (
                gr.update(choices=recent_choices, value=default_conversation_id),
                gr.update(choices=more_choices, value=None),
                status_msg, default_conversation_id, history,
            )
        return gr.update(), gr.update(), status_msg, conversation_id, gr.update()
    
    context_delete_btn.click(
        delete_conversation_and_update,
        inputs=[conversation_list, user_id],
        outputs=[conversation_list, more_conversation_list, delete_status, conversation_id, chatbot]
    )

    def rename_conversation_and_update(conversation_id, user_id, title):
        status_msg = rename_conversation(conversation_id, user_id, title)
        if "成功" not in status_msg:
            return gr.update(), gr.update(), status_msg
        conversations = get_user_conversations(user_id)
        recent_choices, more_choices = split_conversation_choices(
            conversations, conversation_id
        )
        return (
            gr.update(choices=recent_choices, value=conversation_id),
            gr.update(choices=more_choices, value=None),
            status_msg,
        )

    context_rename_btn.click(
        rename_conversation_and_update,
        inputs=[conversation_list, user_id, context_conversation_title],
        outputs=[conversation_list, more_conversation_list, delete_status],
    )
    
    # 切换对话
    def on_conversation_change(conversation_id, user_id):
        """切换对话时清空聊天历史"""
        if conversation_id is not None:
            chat_history = load_conversation_history(conversation_id, user_id)
            return conversation_id, chat_history
        return conversation_id, []  # 返回空的消息列表
    
    conversation_list.input(
        on_conversation_change,
        inputs=[conversation_list, user_id],
        outputs=[conversation_id, chatbot]
    )

    def on_more_conversation_change(selected_id, user_id):
        """从下拉框选择旧对话，并将它提升到可见历史列表。"""
        if selected_id is None:
            return gr.update(), None, [], gr.update()
        conversations = get_user_conversations(user_id)
        recent_choices, more_choices = split_conversation_choices(
            conversations, selected_id
        )
        chat_history = load_conversation_history(selected_id, user_id)
        return (
            gr.update(choices=recent_choices, value=selected_id),
            selected_id,
            chat_history,
            gr.update(choices=more_choices, value=None),
        )

    more_conversation_list.input(
        on_more_conversation_change,
        inputs=[more_conversation_list, user_id],
        outputs=[conversation_list, conversation_id, chatbot, more_conversation_list],
    )

    # RAG文件上传（已移至知识库管理）
    # use_rag.change(toggle_rag_upload, inputs=use_rag, outputs=rag_upload)

    # 旧的文件上传事件（已移至知识库管理）
    # file_input.upload(upload_file, inputs=[file_input, user_id], outputs=upload_status)

    # 发送消息的两种方式：回车和点击按钮
    def send_and_clear(message, user_id, conversation_id, mode, model, use_rag, use_wiki, history):
        """发送消息并清空输入框"""
        if not message.strip():
            yield history, "", gr.update(), gr.update()
            return
        stream = True
        latest_history = history
        for updated_history in send_message(message, user_id, conversation_id, mode, model, use_rag, use_wiki, history, stream):
            latest_history = updated_history
            yield updated_history, "", gr.update(), gr.update()

        conversations = get_user_conversations(user_id)
        recent_choices, more_choices = split_conversation_choices(
            conversations, conversation_id
        )
        yield (
            latest_history,
            "",
            gr.update(choices=recent_choices, value=conversation_id),
            gr.update(choices=more_choices, value=None),
        )
    
    # 回车发送
    message_input.submit(
        send_and_clear,
        inputs=[message_input, user_id, conversation_id, mode, model, use_rag, use_wiki, chatbot],
        outputs=[chatbot, message_input, conversation_list, more_conversation_list]
    )
    
    # 按钮发送
    send_btn.click(
        send_and_clear,
        inputs=[message_input, user_id, conversation_id, mode, model, use_rag, use_wiki, chatbot],
        outputs=[chatbot, message_input, conversation_list, more_conversation_list]
    )

    voice_btn.click(lambda: gr.update(visible=True), outputs=[voice_panel])
    close_voice_btn.click(lambda: gr.update(visible=False), outputs=[voice_panel])

    def transcribe_and_close(audio_path):
        return transcribe(audio_path), gr.update(visible=False)

    # 录音停止后再执行识别，避免点击开始录制时就触发空文件处理。
    mic.stop_recording(
        transcribe_and_close,
        inputs=[mic],
        outputs=[message_input, voice_panel],
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

    # 知识库管理事件
    open_new_kb_btn.click(
        lambda: gr.update(visible=True), outputs=[new_kb_modal]
    )
    cancel_new_kb_btn.click(
        lambda: (gr.update(visible=False), "", "", ""),
        outputs=[new_kb_modal, new_kb_name, new_kb_description, new_kb_status],
    )

    def create_knowledge_base_and_update(user_id, name, description):
        """创建知识库并更新列表"""
        name = (name or "").strip()
        if not name:
            return gr.update(), gr.update(), "❌ 请输入知识库名称", gr.update(), gr.update(), gr.update(visible=True)
        
        status_msg = create_knowledge_base(user_id, name, description.strip() if description else "")
        
        if "成功" in status_msg:
            knowledge_bases = get_user_knowledge_bases(user_id)
            search_choices = get_user_knowledge_bases(user_id, compact=True)
            return (
                gr.update(choices=knowledge_bases, value=None),
                gr.update(choices=search_choices, value=None),
                status_msg, "", "", gr.update(visible=False),
            )
        return gr.update(), gr.update(), status_msg, gr.update(), gr.update(), gr.update(visible=True)
    
    new_kb_btn.click(
        create_knowledge_base_and_update,
        inputs=[user_id, new_kb_name, new_kb_description],
        outputs=[knowledge_base_list, search_kb_list, new_kb_status, new_kb_name, new_kb_description, new_kb_modal]
    )
    
    # 删除知识库
    def delete_knowledge_base_and_update(knowledge_base_id, user_id):
        """删除知识库并更新列表"""
        status_msg = delete_knowledge_base(knowledge_base_id, user_id)
        
        if "成功" in status_msg:
            knowledge_bases = get_user_knowledge_bases(user_id)
            search_choices = get_user_knowledge_bases(user_id, compact=True)
            return (
                gr.update(choices=knowledge_bases, value=None),
                gr.update(choices=search_choices, value=None),
                status_msg,
                gr.update(visible=False),
            )
        return gr.update(), gr.update(), status_msg, gr.update()
    
    delete_kb_btn.click(
        delete_knowledge_base_and_update,
        inputs=[knowledge_base_list, user_id],
        outputs=[knowledge_base_list, search_kb_list, delete_kb_status, kb_detail_panel]
    )
    
    # 刷新知识库列表
    def refresh_knowledge_bases(user_id):
        """刷新知识库列表"""
        knowledge_bases = get_user_knowledge_bases(user_id)
        search_choices = get_user_knowledge_bases(user_id, compact=True)
        return (
            gr.update(choices=knowledge_bases, value=None),
            gr.update(choices=search_choices, value=None),
            gr.update(visible=False),
        )
    
    refresh_kb_btn.click(
        refresh_knowledge_bases,
        inputs=[user_id],
        outputs=[knowledge_base_list, search_kb_list, kb_detail_panel]
    )
    
    # 知识库选择变化时更新文件列表和统计信息
    def on_knowledge_base_change(knowledge_base_id, user_id):
        """知识库选择变化时的处理"""
        if not knowledge_base_id or not user_id:
            return gr.update(choices=[], value=None), "", gr.update(visible=False), "### 知识库详情"
        
        # 更新文件列表
        files = get_knowledge_base_files(knowledge_base_id, user_id)
        
        # 更新统计信息
        stats = get_knowledge_base_stats(user_id)
        
        compact_choices = get_user_knowledge_bases(user_id, compact=True)
        selected_name = next(
            (label for label, value in compact_choices if value == knowledge_base_id),
            "知识库详情",
        )
        return gr.update(choices=files, value=None), stats, gr.update(visible=True), f"### {selected_name}"
    
    knowledge_base_list.change(
        on_knowledge_base_change,
        inputs=[knowledge_base_list, user_id],
        outputs=[kb_file_list, kb_stats, kb_detail_panel, selected_kb_title]
    )
    
    # 上传文件到知识库
    def upload_file_to_kb_and_update(file, knowledge_base_id, user_id):
        """上传文件到知识库并更新文件列表"""
        if not file or not knowledge_base_id or not user_id:
            return "❗ 请先选择知识库和文件", gr.update(), gr.update(), gr.update()
        
        status_msg = upload_file_to_knowledge_base(file, knowledge_base_id, user_id)
        
        if "成功" in status_msg:
            files = get_knowledge_base_files(knowledge_base_id, user_id)
            cards = get_user_knowledge_bases(user_id)
            search_choices = get_user_knowledge_bases(user_id, compact=True)
            return (
                status_msg,
                gr.update(choices=files, value=None),
                gr.update(choices=cards, value=knowledge_base_id),
                gr.update(choices=search_choices),
            )
        return status_msg, gr.update(), gr.update(), gr.update()
    
    kb_upload_btn.click(
        upload_file_to_kb_and_update,
        inputs=[kb_file_input, knowledge_base_list, user_id],
        outputs=[kb_upload_status, kb_file_list, knowledge_base_list, search_kb_list]
    )
    
    # 删除知识库文件
    def delete_kb_file_and_update(file_id, knowledge_base_id, user_id):
        """删除知识库文件并更新列表"""
        if not file_id or not knowledge_base_id or not user_id:
            return gr.update(), "❗ 请先选择要删除的文件", gr.update(), gr.update(), gr.update()
        
        status_msg = delete_file_from_knowledge_base(file_id, knowledge_base_id, user_id)
        
        if "成功" in status_msg:
            # 更新文件列表
            files = get_knowledge_base_files(knowledge_base_id, user_id)
            stats = get_knowledge_base_stats(user_id)
            cards = get_user_knowledge_bases(user_id)
            search_choices = get_user_knowledge_bases(user_id, compact=True)
            return (
                gr.update(choices=files, value=None), status_msg, stats,
                gr.update(choices=cards, value=knowledge_base_id),
                gr.update(choices=search_choices),
            )
        return gr.update(), status_msg, "删除失败", gr.update(), gr.update()
    
    delete_kb_file_btn.click(
        delete_kb_file_and_update,
        inputs=[kb_file_list, knowledge_base_list, user_id],
        outputs=[kb_file_list, delete_kb_file_status, kb_stats, knowledge_base_list, search_kb_list]
    )

    # 顶部主导航：主页、知识库、聊天、搜索和设置。
    page_outputs = [
        home_page, sidebar, main_chat, search_page, new_kb_modal,
        conversation_tab, knowledge_tab, settings_tab,
        mode, use_rag, model, advanced_title,
        api_key_section,
        home_nav_btn, knowledge_nav_btn, chat_nav_btn, search_nav_btn, settings_nav_btn,
    ]

    def switch_main_page(page):
        is_home = page == "home"
        is_knowledge = page == "knowledge"
        is_chat = page == "chat"
        is_search = page == "search"
        is_settings = page == "settings"
        return (
            gr.update(visible=is_home),
            gr.update(visible=is_knowledge or is_chat or is_settings),
            gr.update(visible=is_chat),
            gr.update(visible=is_search),
            gr.update(visible=False),
            gr.update(visible=is_chat),
            gr.update(visible=is_knowledge),
            gr.update(visible=is_settings),
            gr.update(visible=is_settings),
            gr.update(visible=is_settings),
            gr.update(visible=is_settings),
            gr.update(visible=is_settings),
            gr.update(visible=is_settings),
            gr.update(variant="primary" if is_home else "secondary"),
            gr.update(variant="primary" if is_knowledge else "secondary"),
            gr.update(variant="primary" if is_chat else "secondary"),
            gr.update(variant="primary" if is_search else "secondary"),
            gr.update(variant="primary" if is_settings else "secondary"),
        )

    home_nav_btn.click(lambda: switch_main_page("home"), outputs=page_outputs)
    knowledge_nav_btn.click(lambda: switch_main_page("knowledge"), outputs=page_outputs)
    chat_nav_btn.click(lambda: switch_main_page("chat"), outputs=page_outputs)
    chat_nav_btn.click(
        on_conversation_change,
        inputs=[conversation_list, user_id],
        outputs=[conversation_id, chatbot],
    )
    search_nav_btn.click(lambda: switch_main_page("search"), outputs=page_outputs)
    settings_nav_btn.click(lambda: switch_main_page("settings"), outputs=page_outputs)

    # 每次登录后都从主页开始，避免保留上一次退出时的页面状态。
    login_btn.click(lambda: switch_main_page("home"), outputs=page_outputs)

    search_source.change(
        lambda source: gr.update(visible=source == "指定知识库"),
        inputs=[search_source], outputs=[search_kb_list],
    )
    search_btn.click(
        search_content,
        inputs=[search_input, search_source, search_kb_list, user_id],
        outputs=[search_result],
    )
    search_input.submit(
        search_content,
        inputs=[search_input, search_source, search_kb_list, user_id],
        outputs=[search_result],
    )
    
    # Wiki状态刷新
    refresh_wiki_status_btn.click(
        lambda: get_wiki_status(),
        outputs=[wiki_status]
    )
    
    # Wiki模式切换
    def switch_wiki_to_online_and_update():
        """切换到在线模式并更新状态"""
        result = switch_wiki_mode("online")
        new_status = get_wiki_status()
        return result, new_status
    
    def switch_wiki_to_offline_and_update():
        """切换到离线模式并更新状态"""
        result = switch_wiki_mode("offline")
        new_status = get_wiki_status()
        return result, new_status
    
    switch_to_online_btn.click(
        switch_wiki_to_online_and_update,
        outputs=[wiki_switch_status, wiki_status]
    )
    
    switch_to_offline_btn.click(
        switch_wiki_to_offline_and_update,
        outputs=[wiki_switch_status, wiki_status]
    )

    # 为聊天历史添加原生右键菜单，并通过隐藏的 Gradio 组件调用后端事件。
    demo.load(
        fn=None,
        js="""
        () => {
            if (window.__omnisageConversationMenuReady) return [];
            window.__omnisageConversationMenuReady = true;

            const closeMenu = () => {
                document.getElementById('conversation-context-menu')?.remove();
            };

            document.addEventListener('click', closeMenu);
            document.addEventListener('contextmenu', (event) => {
                const label = event.target.closest('.conversation-history label');
                if (!label) return;
                event.preventDefault();
                closeMenu();

                const radio = label.querySelector('input[type="radio"]');
                if (radio && !radio.checked) label.click();
                const currentTitle = label.innerText.trim();

                const menu = document.createElement('div');
                menu.id = 'conversation-context-menu';
                menu.style.left = `${event.clientX}px`;
                menu.style.top = `${event.clientY}px`;

                const rename = document.createElement('button');
                rename.textContent = '重命名';
                rename.onclick = (clickEvent) => {
                    clickEvent.stopPropagation();
                    const nextTitle = window.prompt('重命名对话', currentTitle);
                    if (!nextTitle || !nextTitle.trim()) return closeMenu();
                    const field = document.querySelector(
                        '#context-conversation-title textarea, #context-conversation-title input'
                    );
                    if (field) {
                        const prototype = field instanceof HTMLTextAreaElement
                            ? window.HTMLTextAreaElement.prototype
                            : window.HTMLInputElement.prototype;
                        const setter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
                        setter?.call(field, nextTitle.trim());
                        field.dispatchEvent(new Event('input', { bubbles: true }));
                        document.querySelector('#context-rename button')?.click();
                    }
                    closeMenu();
                };

                const remove = document.createElement('button');
                remove.textContent = '删除';
                remove.className = 'danger';
                remove.onclick = (clickEvent) => {
                    clickEvent.stopPropagation();
                    if (window.confirm(`确定删除“${currentTitle}”吗？`)) {
                        document.querySelector('#context-delete button')?.click();
                    }
                    closeMenu();
                };

                menu.append(rename, remove);
                document.body.appendChild(menu);
            });
            return [];
        }
        """,
    )

demo.launch()
