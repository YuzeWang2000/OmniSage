# backend/app/services/llm_service.py
from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_ollama import ChatOllama, OllamaLLM

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PlaywrightURLLoader,
    UnstructuredFileLoader, 
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader
)
import os
from typing import List, Dict, Any, Optional
from ..config import settings
online_models = ["deepseek-chat", "deepseek-reasoner"]
class LLMController:
    """
    统一的LLM控制器，负责处理所有模型调用
    """
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=settings.EMBEDDING_MODEL)
        self.persist_dir = settings.VECTOR_DB_PATH
        self._vectorstore = None
    
    def get_vectorstore(self) -> Optional[Chroma]:
        """获取向量数据库实例"""
        if self._vectorstore is None:
            try:
                if os.path.exists(self.persist_dir):
                    self._vectorstore = Chroma(
                        persist_directory=self.persist_dir, 
                        embedding_function=self.embeddings
                    )
            except Exception as e:
                print(f"向量数据库初始化失败: {str(e)}")
        return self._vectorstore
    
    def get_llm(self, model_name: str, mode: str = "chat", user_id: int = None, db = None):
        """获取LLM实例"""
        if model_name in online_models:
            if model_name.startswith("deepseek"):
                from langchain_deepseek import ChatDeepSeek
                
                # 尝试从数据库获取用户的API key
                api_key = settings.DEEPSEEK_API_KEY  # 默认使用全局配置
                if user_id and db:
                    from ..services.database_service import DatabaseService
                    user_api_key = DatabaseService.get_user_api_key_by_provider(user_id, "deepseek", db)
                    if user_api_key and user_api_key.is_active:
                        api_key = user_api_key.api_key
                        print(f"使用用户 {user_id} 的DeepSeek API key: {api_key[:10]}...{api_key[-4:]}")
                    else:
                        print(f"用户 {user_id} 没有有效的DeepSeek API key，使用全局配置")
                else:
                    print(f"使用全局DeepSeek API key: {api_key[:10]}...{api_key[-4:]}")
                
                # 在线模型
                return ChatDeepSeek(
                    model=model_name,
                    temperature=settings.DEFAULT_TEMPERATURE,
                    api_key=api_key
                )
            elif model_name.startswith("gpt"):
                # OpenAI模型
                api_key = settings.OPENAI_API_KEY  # 默认使用全局配置
                if user_id and db:
                    from ..services.database_service import DatabaseService
                    user_api_key = DatabaseService.get_user_api_key_by_provider(user_id, "openai", db)
                    if user_api_key and user_api_key.is_active:
                        api_key = user_api_key.api_key
                        print(f"使用用户 {user_id} 的OpenAI API key: {api_key[:10]}...{api_key[-4:]}")
                    else:
                        print(f"用户 {user_id} 没有有效的OpenAI API key，使用全局配置")
                else:
                    print(f"使用全局OpenAI API key: {api_key[:10]}...{api_key[-4:]}")
                
                return ChatOpenAI(
                    model=model_name,
                    temperature=settings.DEFAULT_TEMPERATURE,
                    api_key=api_key
                )
            else:
                raise ValueError(f"不支持的在线模型: {model_name}")
        else:
            # 本地Ollama模型
            if mode == "chat":
                return ChatOllama(
                    model=model_name,
                    temperature=settings.DEFAULT_TEMPERATURE
                )
            elif mode == "generate":
                return OllamaLLM(
                    model=model_name,
                    temperature=settings.DEFAULT_TEMPERATURE
                )
            else:
                raise ValueError(f"不支持的模型模式: {mode}")

    # def get_rag_context(self, message: str, user_id: int = None, db = None) -> str:
    #     """从向量数据库中检索相关文档（传统方法）"""
    #     if not user_id or not db:
    #         print("没有用户ID或数据库")
    #         return ""
    #     from .knowledgebase_service import knowledge_base_service
    #     return knowledge_base_service.get_rag_context(user_id, message, top_k=3, db=db)
    
    def create_rag_chain(
        self,
        user_id: int,
        model_name: str,
        chain_type: str = "stuff",
        use_reranker: bool = True,
        top_k: int = 5,
        score_threshold: float = 0.5,
        use_wiki: bool = False,  # 添加Wiki知识支持
        db = None
    ):
        """
        创建RAG Chain
        
        Args:
            user_id: 用户ID
            model_name: 模型名称
            chain_type: Chain类型
            use_reranker: 是否使用重排序
            top_k: 检索文档数量
            score_threshold: 相似度阈值
            use_wiki: 是否使用Wiki知识
            db: 数据库会话
            
        Returns:
            RAG Chain实例或None
        """
        try:
            # 获取LLM实例
            llm = self.get_llm(model_name, mode="chat", user_id=user_id, db=db)
            if not llm:
                return None
            
            # 创建RAG Chain
            from .knowledgebase_service import knowledge_base_service
            return knowledge_base_service.create_rag_chain_for_user(
                user_id=user_id,
                llm=llm,
                chain_type=chain_type,
                use_reranker=use_reranker,
                top_k=top_k,
                score_threshold=score_threshold,
                use_wiki=use_wiki,  # 传递Wiki参数
                db=db
            )
        except Exception as e:
            print(f"创建RAG Chain失败: {str(e)}")
            return None
    
    def create_simple_chat_chain(
        self,
        model_name: str,
        user_id: int = None,
        db = None
    ):
        """
        创建简单聊天Chain（不使用Prompt模板）
        
        Args:
            model_name: 模型名称
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            简单聊天Chain实例
        """
        try:
            # 获取LLM实例
            llm = self.get_llm(model_name, mode="chat", user_id=user_id, db=db)
            if not llm:
                return None
            
            # 创建简单聊天Chain
            from .knowledgebase_service import knowledge_base_service
            return knowledge_base_service.create_simple_chat_chain(llm)
        except Exception as e:
            print(f"创建简单聊天Chain失败: {str(e)}")
            return None
    
    def create_chat_chain(
        self,
        model_name: str,
        prompt_name: str = "chat_default",
        user_id: int = None,
        db = None
    ):
        """
        创建聊天Chain
        
        Args:
            model_name: 模型名称
            prompt_name: Prompt模板名称
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            聊天Chain实例
        """
        try:
            # 获取LLM实例
            llm = self.get_llm(model_name, mode="chat", user_id=user_id, db=db)
            if not llm:
                return None
            
            # 创建聊天Chain
            from .knowledgebase_service import knowledge_base_service
            return knowledge_base_service.create_chat_chain(llm, prompt_name)
        except Exception as e:
            print(f"创建聊天Chain失败: {str(e)}")
            return None
    
    def create_generation_chain(
        self,
        model_name: str,
        prompt_name: str,
        user_id: int = None,
        db = None
    ):
        """
        创建生成任务Chain
        
        Args:
            model_name: 模型名称
            prompt_name: Prompt模板名称
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            生成Chain实例
        """
        try:
            # 获取LLM实例
            llm = self.get_llm(model_name, mode="generate", user_id=user_id, db=db)
            if not llm:
                return None
            
            # 创建生成Chain
            from .knowledgebase_service import knowledge_base_service
            return knowledge_base_service.create_generation_chain(llm, prompt_name)
        except Exception as e:
            print(f"创建生成Chain失败: {str(e)}")
            return None
    
    def get_available_prompts(self):
        """获取可用的Prompt模板"""
        from .knowledgebase_service import knowledge_base_service
        return knowledge_base_service.get_available_prompts()
    
    def get_chain_types(self):
        """获取可用的Chain类型"""
        from .knowledgebase_service import knowledge_base_service
        return knowledge_base_service.get_chain_types()
    
    def process_message(self, payload: Dict[str, Any], user_id: int = None, db = None):
        """
        流式处理消息 - 统一使用Chain方式
        """
        message = payload.get("message", "")
        model_name = payload.get("model", settings.DEFAULT_MODEL)
        mode = payload.get("mode", "chat")
        use_rag = payload.get("use_rag", False)
        use_wiki = payload.get("use_wiki", False)  # 获取Wiki参数
        chat_history = payload.get("chat_history", [])
        chain_type = payload.get("chain_type", "stuff")
        # 根据模式选择合适的默认prompt
        default_prompt = "generate_default" if mode == "generate" else "chat_default"
        prompt_name = payload.get("prompt_name", default_prompt)
        use_reranker = payload.get("use_reranker", True)
        top_k = payload.get("top_k", 5)
        score_threshold = payload.get("score_threshold", 0.5)
        print("=" * 20, "处理消息", "=" * 20)
        print(payload)
        print("=" * 20, "处理消息", "=" * 20)
        try:
            # 如果启用了Wiki知识，优先使用RAG模式
            if use_wiki and not use_rag:
                print("🔍 检测到Wiki知识请求，自动启用RAG模式")
                use_rag = True
            
            if use_rag:
                print("=" * 20, "RAG Chain处理", "=" * 20)
                # 根据mode选择不同的RAG Chain
                if mode == "generate":
                    print("使用RAG生成Chain")
                    rag_chain = self.create_rag_chain(
                        user_id=user_id,
                        model_name=model_name,
                        chain_type=chain_type,
                        use_reranker=use_reranker,
                        top_k=top_k,
                        score_threshold=score_threshold,
                        use_wiki=use_wiki,  # 传递Wiki参数
                        db=db
                    )
                else:
                    # 默认使用聊天模式
                    print("使用RAG聊天Chain")
                    rag_chain = self.create_rag_chain(
                        user_id=user_id,
                        model_name=model_name,
                        chain_type=chain_type,
                        use_reranker=use_reranker,
                        top_k=top_k,
                        score_threshold=score_threshold,
                        use_wiki=use_wiki,  # 传递Wiki参数
                        db=db
                    )
                # rag_test = True
                # if rag_test:
                #     from .knowledgebase_service import knowledge_base_service
                #     rag_context = knowledge_base_service.get_rag_context(user_id=user_id,message=message, top_k=top_k, db=db)
                if rag_chain:
                    # print("=" * 20, "RAG Chain处理", "=" * 20)
                    # print(rag_chain)
                    # print("=" * 20, "RAG Chain处理", "=" * 20)
                    # 流式处理RAG Chain
                    if hasattr(rag_chain, 'stream'):
                        print("使用RAG Chain流式API")
                        try:
                            in_reasoning = False
                            for chunk in rag_chain.stream({"input": message}):
                                # 处理推理内容
                                if hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs.get("reasoning_content"):
                                    reasoning_content = chunk.additional_kwargs["reasoning_content"]
                                    if not in_reasoning:
                                        yield "<think>"
                                        yield " \n"
                                        in_reasoning = True
                                    yield reasoning_content
                                else:
                                    if in_reasoning:
                                        yield " \n"
                                        yield "</think>"
                                        yield " \n\n"
                                        in_reasoning = False
                                    # 正常内容输出
                                    if hasattr(chunk, 'content') and chunk.content:
                                        yield chunk.content
                                    elif hasattr(chunk, 'result'):
                                        yield chunk.result
                                    elif hasattr(chunk, 'answer'):
                                        yield chunk.answer
                                    elif hasattr(chunk, 'answer_text'):
                                        yield chunk.answer_text
                                    elif isinstance(chunk, dict):
                                        # 处理新的RunnableBinding格式
                                        if 'answer' in chunk:
                                            yield chunk['answer']
                                        elif 'result' in chunk:
                                            yield chunk['result']
                                        elif 'content' in chunk:
                                            yield chunk['content']
                                        elif 'answer_text' in chunk:
                                            yield chunk['answer_text']
                            
                            if in_reasoning:
                                yield "</think>"
                                yield " \n"
                        except Exception as e:
                            yield f"❌ RAG Chain流式处理失败: {str(e)}"
                    else:
                        # 非流式RAG Chain
                        print("使用RAG Chain非流式API")
                        try:
                            result = rag_chain.invoke({"input": message})
                            answer = result.answer if hasattr(result, 'answer') else result.result if hasattr(result, 'result') else str(result)
                            
                            # 按字符流式输出
                            for char in answer:
                                yield char
                        except Exception as e:
                            yield f"❌ RAG Chain处理失败: {str(e)}"
                else:
                    # 如果RAG Chain创建失败，抛出异常而不是回退
                    print("RAG Chain创建失败")
                    raise Exception("RAG Chain创建失败，请检查知识库配置")
            else:
                # 根据mode选择不同的Chain处理（不使用RAG）
                if mode == "generate":
                    print("=" * 20, "生成Chain处理", "=" * 20)
                    # 使用生成Chain
                    generation_chain = self.create_generation_chain(
                        model_name=model_name,
                        prompt_name=prompt_name,
                        user_id=user_id,
                        db=db
                    )
                    print("=" * 20, "生成Chain处理", "=" * 20)
                    print(generation_chain)
                    print("=" * 20, "生成Chain处理", "=" * 20)
                    
                    if generation_chain:
                        # 流式处理生成Chain
                        if hasattr(generation_chain, 'stream'):
                            print("使用生成Chain流式API")
                            try:
                                in_reasoning = False
                                for chunk in generation_chain.stream({"input": message}):
                                    # 处理推理内容
                                    if hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs.get("reasoning_content"):
                                        print("=" * 20, "处理推理内容", "=" * 20)
                                        print(chunk)
                                        print("=" * 20, "处理推理内容", "=" * 20)
                                        reasoning_content = chunk.additional_kwargs["reasoning_content"]
                                        if not in_reasoning:
                                            yield "<think>"
                                            yield " \n"
                                            in_reasoning = True
                                        yield reasoning_content
                                    else:
                                        if in_reasoning:
                                            yield " \n"
                                            yield "</think>"
                                            yield " \n\n"
                                            in_reasoning = False
                                        print("=" * 20, "处理正常内容", "=" * 20)
                                        print(chunk)
                                        print("=" * 20, "处理正常内容", "=" * 20)
                                        # 正常内容输出
                                        if hasattr(chunk, 'content') and chunk.content:
                                            yield chunk.content
                                        elif hasattr(chunk, 'result'):
                                            yield chunk.result
                                        elif hasattr(chunk, 'answer'):
                                            yield chunk.answer
                                        elif hasattr(chunk, 'answer_text'):
                                            yield chunk.answer_text
                                        elif isinstance(chunk, dict):
                                            # 处理新的RunnableSequence格式
                                            if 'answer' in chunk:
                                                yield chunk['answer']
                                            elif 'result' in chunk:
                                                yield chunk['result']
                                            elif 'content' in chunk:
                                                yield chunk['content']
                                            elif 'answer_text' in chunk:
                                                yield chunk['answer_text']
                                        else:
                                            yield chunk
                                
                                if in_reasoning:
                                    yield "</think>"
                                    yield " \n"
                            except Exception as e:
                                yield f"❌ 生成Chain流式处理失败: {str(e)}"
                        else:
                            # 非流式生成Chain
                            print("使用生成Chain非流式API")
                            try:
                                result = generation_chain.invoke({"input": message})
                                answer = result.answer if hasattr(result, 'answer') else result.result if hasattr(result, 'result') else str(result)
                                
                                # 按字符流式输出
                                for char in answer:
                                    yield char
                            except Exception as e:
                                yield f"❌ 生成Chain处理失败: {str(e)}"
                    else:
                        # 如果生成Chain创建失败，抛出异常而不是回退
                        print("生成Chain创建失败")
                        raise Exception("生成Chain创建失败，请检查模型配置")
                    return  # 生成模式处理完成，直接返回
                else:
                    # 默认使用聊天模式
                    print("=" * 20, "聊天Chain处理", "=" * 20)
                    
                    # 初始化chat_chain变量
                    chat_chain = None
                    
                    # 根据是否有prompt_name选择不同的聊天Chain
                    if prompt_name and prompt_name != "chat_default":
                        # 使用带Prompt模板的聊天Chain
                        chat_chain = self.create_chat_chain(
                            model_name=model_name,
                            prompt_name=prompt_name,
                            user_id=user_id,
                            db=db
                        )
                    else:
                        # 使用简单聊天Chain
                        chat_chain = self.create_simple_chat_chain(
                            model_name=model_name,
                            user_id=user_id,
                            db=db
                        )
                
                if chat_chain:
                    # 构建聊天历史
                    history_messages = []
                    for hist in chat_history:
                        if hist.get("role") == "user":
                            history_messages.append(HumanMessage(content=hist.get("content", "")))
                        elif hist.get("role") == "assistant":
                            history_messages.append(AIMessage(content=hist.get("content", "")))
                    
                    # 构建完整的消息列表（包含历史）
                    full_messages = history_messages + [HumanMessage(content=message)]
                    
                    # 流式处理
                    if hasattr(chat_chain, 'stream'):
                        print("使用简单聊天Chain流式API")
                        try:
                            in_reasoning = False
                            for chunk in chat_chain.stream(full_messages):
                                if hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs.get("reasoning_content"):
                                    reasoning_content = chunk.additional_kwargs["reasoning_content"]
                                    if not in_reasoning:
                                        yield "<think>"
                                        yield " \n"
                                        in_reasoning = True
                                    yield reasoning_content
                                else:
                                    if in_reasoning:
                                        yield " \n"
                                        yield "</think>"
                                        yield " \n\n"
                                        in_reasoning = False
                                    if hasattr(chunk, 'content') and chunk.content:
                                        yield chunk.content
                            
                            if in_reasoning:
                                yield "</think>"
                                yield " \n"
                        except Exception as e:
                            yield f"❌ 简单聊天Chain流式处理失败: {str(e)}"
                    else:
                        # 非流式聊天Chain
                        print("使用简单聊天Chain非流式API")
                        try:
                            response = chat_chain.invoke(full_messages)
                            content = response.content if hasattr(response, 'content') else str(response)
                            
                            # 按字符流式输出
                            for char in content:
                                yield char
                        except Exception as e:
                            yield f"❌ 简单聊天Chain处理失败: {str(e)}"
                else:
                    # 如果简单聊天Chain创建失败，回退到传统方式
                    print("简单聊天Chain创建失败")
                    raise Exception("简单聊天Chain创建失败，请检查模型配置")
                    
        except Exception as e:
            yield f"❌ Chain处理失败: {str(e)}"
    
    # def process_document(self, file_path: str, file_type: str) -> List:
    #     """处理文档并返回分割后的文档块"""
    #     print(f"开始处理文档: {file_path}, 类型: {file_type}")
    #     try:
    #         # 根据文件类型选择加载器
    #         if file_type in ['txt', 'md']:
    #             loader = TextLoader(file_path)
    #         elif file_type == 'pdf':
    #             try:
    #                 # 首先尝试使用 PyPDFLoader
    #                 loader = PyPDFLoader(file_path)
    #             except Exception:
    #                 # 如果失败,使用 UnstructuredPDFLoader 作为后备
    #                 print("PyPDFLoader 失败,使用 UnstructuredPDFLoader")
    #                 loader = UnstructuredPDFLoader(file_path)
    #         elif file_type in ['docx', 'doc']:
    #             try:
    #                 # 首先尝试使用 Docx2txtLoader
    #                 loader = Docx2txtLoader(file_path)
    #             except Exception:
    #                 # 如果失败,使用 UnstructuredWordDocumentLoader 作为后备
    #                 print("Docx2txtLoader 失败,使用 UnstructuredWordDocumentLoader")
    #                 loader = UnstructuredWordDocumentLoader(file_path)
    #         else:
    #             # 对于其他类型文件,使用通用的 UnstructuredFileLoader
    #             loader = UnstructuredFileLoader(file_path)
            
    #         documents = loader.load()
            
    #         # 文本分割
    #         text_splitter = RecursiveCharacterTextSplitter(
    #             chunk_size=settings.CHUNK_SIZE,
    #             chunk_overlap=settings.CHUNK_OVERLAP,
    #             length_function=len,
    #         )
            
    #         return text_splitter.split_documents(documents)
    #     except Exception as e:
    #         print(f"文档处理失败: {str(e)}")
    #         return []
    
    # def add_documents_to_vectorstore(self, documents: List) -> bool:
    #     """将文档添加到向量数据库"""
    #     try:
    #         vectorstore = self.get_vectorstore()
    #         if vectorstore and documents:
    #             vectorstore.add_documents(documents)
    #             print(f"成功添加 {len(documents)} 条文档到向量数据库")
    #             for doc in documents:
    #                 print(doc)
    #             print("=" * 20, "向量数据库添加文档成功", "=" * 20)
                
    #             return True
    #     except Exception as e:
    #         print(f"添加文档到向量数据库失败: {str(e)}")
    #     return False

# 全局LLM控制器实例
llm_controller = LLMController()
