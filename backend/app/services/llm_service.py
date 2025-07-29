# backend/app/services/llm_service.py
from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_ollama import ChatOllama, OllamaLLM

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
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

    
    def get_rag_context(self, message: str) -> str:
        """从向量数据库中检索相关文档"""
        vectorstore = self.get_vectorstore()
        print("=" * 20, "获得向量数据库", "=" * 20)
        if not vectorstore:
            return ""
        
        try:
            retriever = vectorstore.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": 3}
            )
            docs = retriever.get_relevant_documents(message)
            if docs:
                context = "\n".join([doc.page_content for doc in docs])
                print("=" * 20, "RAG检索结果", "=" * 20)
                print(docs)
                print(f"RAG检索到 {len(docs)} 条相关文档")
                print("相关文档内容:", context)
                return f"\n\n相关文档信息：\n{context}\n\n基于以上信息回答："
        except Exception as e:
            print(f"RAG检索失败: {str(e)}")
        
        return ""
    
    def process_message(self, payload: Dict[str, Any], user_id: int = None, db = None):
        """
        流式处理消息
        """
        message = payload.get("message", "")
        model_name = payload.get("model", settings.DEFAULT_MODEL)
        mode = payload.get("mode", "chat")
        use_rag = payload.get("use_rag", False)
        chat_history = payload.get("chat_history", [])
        
        # 构建消息列表
        messages = []
        
        # 添加聊天历史
        for hist in chat_history:
            if hist.get("role") == "user":
                messages.append(HumanMessage(content=hist.get("content", "")))
            elif hist.get("role") == "assistant":
                messages.append(AIMessage(content=hist.get("content", "")))
        
        # 处理当前消息
        if use_rag:
            print("=" * 20, "RAG处理", "=" * 20)        
            rag_context = self.get_rag_context(message)
            if rag_context:
                enhanced_message = message + rag_context
                messages.append(HumanMessage(content=enhanced_message))
            else:
                messages.append(HumanMessage(content=message))
        else:
            messages.append(HumanMessage(content=message))
        
        # 调用模型
        try:
            llm = self.get_llm(model_name, mode, user_id, db)
            if hasattr(llm, 'stream'):
                print("使用流式API")
                # 同步流式API
                try:
                    in_reasoning = False 
                    for chunk in llm.stream(messages):
                        # print(f"LLM返回的chunk: {chunk}")
                        # 判断是否有reasoning_content
                        reasoning_content = ""
                        if hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs.get("reasoning_content"):
                            reasoning_content = chunk.additional_kwargs["reasoning_content"]
                            # 推理阶段开始
                            if not in_reasoning:
                                yield "<think>"
                                yield " \n"
                                in_reasoning = True
                            yield reasoning_content
                        else:
                            # 推理阶段结束
                            if in_reasoning:
                                yield " \n"
                                yield "</think>"
                                yield " \n\n"
                                in_reasoning = False
                            # 正常内容输出
                            if hasattr(chunk, 'content') and chunk.content:
                                yield chunk.content
                    # 如果推理阶段还未关闭，最后补一个</think>
                    if in_reasoning:
                        yield "</think>"
                        yield " \n"
                except Exception as e:
                    yield f"❌ 流式处理失败: {str(e)}"
            else:
                # 模拟流式输出
                print("使用模拟流式输出")
                try:
                    response = llm.invoke(messages) if hasattr(llm, 'invoke') else llm(messages)
                    content = response.content if hasattr(response, 'content') else str(response)
                    
                    # 按字符流式输出
                    for char in content:
                        yield char
                except Exception as e:
                    yield f"❌ 处理失败: {str(e)}"
                    
        except Exception as e:
            yield f"❌ 模型调用失败: {str(e)}"
    
    def process_document(self, file_path: str, file_type: str) -> List:
        """处理文档并返回分割后的文档块"""
        print(f"开始处理文档: {file_path}, 类型: {file_type}")
        try:
            # 根据文件类型选择加载器
            if file_type in ['txt', 'md']:
                loader = TextLoader(file_path)
            elif file_type == 'pdf':
                try:
                    # 首先尝试使用 PyPDFLoader
                    loader = PyPDFLoader(file_path)
                except Exception:
                    # 如果失败,使用 UnstructuredPDFLoader 作为后备
                    print("PyPDFLoader 失败,使用 UnstructuredPDFLoader")
                    loader = UnstructuredPDFLoader(file_path)
            elif file_type in ['docx', 'doc']:
                try:
                    # 首先尝试使用 Docx2txtLoader
                    loader = Docx2txtLoader(file_path)
                except Exception:
                    # 如果失败,使用 UnstructuredWordDocumentLoader 作为后备
                    print("Docx2txtLoader 失败,使用 UnstructuredWordDocumentLoader")
                    loader = UnstructuredWordDocumentLoader(file_path)
            else:
                # 对于其他类型文件,使用通用的 UnstructuredFileLoader
                loader = UnstructuredFileLoader(file_path)
            
            documents = loader.load()
            
            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
            )
            
            return text_splitter.split_documents(documents)
        except Exception as e:
            print(f"文档处理失败: {str(e)}")
            return []
    
    def add_documents_to_vectorstore(self, documents: List) -> bool:
        """将文档添加到向量数据库"""
        try:
            vectorstore = self.get_vectorstore()
            if vectorstore and documents:
                vectorstore.add_documents(documents)
                print(f"成功添加 {len(documents)} 条文档到向量数据库")
                for doc in documents:
                    print(doc)
                print("=" * 20, "向量数据库添加文档成功", "=" * 20)
                
                return True
        except Exception as e:
            print(f"添加文档到向量数据库失败: {str(e)}")
        return False

# 全局LLM控制器实例
llm_controller = LLMController()
