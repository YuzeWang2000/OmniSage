# 知识库服务
# KnowledgeBaseService
# 功能：
# 文件： 文件上传，文件下载，文件删除，文件列表获取，文件状态维护（mysql，知识库id，用户id，文件id）
# 向量知识库： 使用chroma实现，向量知识库的初始化，向量知识库的更新（添加，上传，重新生成），向量知识库的维护（mysql，知识库id和用户id）
# rag链：使用向量数据库和LLM获得检索链
# 检索：根据query检索知识库，使用检索的结果完善rag链，返回rag链的推理结果

import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredFileLoader, 
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader
)
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from ..config import settings
from ..models import User, KnowledgeBase, KnowledgeFile
from .database_service import DatabaseService
from .rag_chain_service import OptimizedRAGChainService


class KnowledgeBaseService:
    """
    知识库服务类
    负责管理知识库的创建、文件上传、向量化、检索等操作
    所有知识库状态都记录在数据库中，每个知识库对应user_id和knowledge_id
    """
    
    def __init__(self):
        self.base_upload_dir = os.path.join(os.getcwd(), settings.UPLOAD_DIR)
        self.base_vector_dir = os.path.join(os.getcwd(), settings.VECTOR_DB_PATH)
        
        # 确保基础目录存在
        os.makedirs(self.base_upload_dir, exist_ok=True)
        os.makedirs(self.base_vector_dir, exist_ok=True)
        
        # 初始化优化的RAG Chain服务
        self.rag_chain_service = OptimizedRAGChainService()
    
    def create_knowledge_base(self, user_id: int, name: str, description: str = None, 
                            embedding_model: str = "nomic-embed-text", db: Session = None) -> Dict[str, Any]:
        """
        创建知识库
        
        Args:
            user_id: 用户ID
            name: 知识库名称
            description: 知识库描述
            embedding_model: 嵌入模型名称
            db: 数据库会话
            
        Returns:
            Dict: 包含创建结果的字典
        """
        try:
            # 检查知识库名称是否已存在
            existing_kb = DatabaseService.get_knowledge_base_by_name(user_id, name, db)
            if existing_kb:
                return {
                    "success": False,
                    "message": f"知识库名称 '{name}' 已存在"
                }
            
            # 创建知识库目录
            kb_dir = os.path.join(self.base_upload_dir, f"user_{user_id}", f"kb_{name}")
            vector_dir = os.path.join(self.base_vector_dir, f"user_{user_id}", f"kb_{name}")
            os.makedirs(kb_dir, exist_ok=True)
            os.makedirs(vector_dir, exist_ok=True)
            
            # 创建知识库记录
            knowledge_base = DatabaseService.create_knowledge_base(
                user_id=user_id,
                name=name,
                description=description,
                embedding_model=embedding_model,
                vector_db_path=vector_dir,
                db=db
            )
            
            if knowledge_base:
                return {
                    "success": True,
                    "message": f"知识库 '{name}' 创建成功",
                    "knowledge_base_id": knowledge_base.id
                }
            else:
                return {
                    "success": False,
                    "message": "知识库创建失败"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"创建知识库失败: {str(e)}"
            }
    
    def upload_file_to_knowledge_base(self, knowledge_base_id: int, user_id: int, 
                                    file, db: Session = None) -> Dict[str, Any]:
        """
        上传文件到指定知识库
        
        Args:
            knowledge_base_id: 知识库ID
            user_id: 用户ID
            file: 上传的文件对象
            db: 数据库会话
            
        Returns:
            Dict: 包含处理结果的字典
        """
        try:
            # 验证知识库是否存在且属于该用户
            knowledge_base = DatabaseService.get_knowledge_base_by_id(knowledge_base_id, user_id, db)
            print(f"上传文件到知识库: {knowledge_base.name if knowledge_base else '未知知识库'}")
            if not knowledge_base:
                return {
                    "success": False,
                    "message": "知识库不存在或无权限访问"
                }
            
            # 检查文件大小
            if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "message": f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024}MB)"
                }
            
            # 生成文件名和路径
            original_filename = file.filename
            print(f"上传文件: {original_filename}, 大小: {file.size if hasattr(file, 'size') else '未知'}")
            if original_filename and '/' in original_filename:
                actual_filename = os.path.basename(original_filename)
            else:
                actual_filename = original_filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = actual_filename.split('.')[-1].lower() if '.' in actual_filename else 'txt'
            unique_filename = f"{timestamp}_{actual_filename}"
            
            # 保存文件
            kb_upload_dir = os.path.join(self.base_upload_dir, f"user_{user_id}", f"kb_{knowledge_base.name}")
            file_path = os.path.join(kb_upload_dir, unique_filename)
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # 处理文档
            documents = self._process_document(file_path, file_extension)
            print(f"处理后的文档数量: {len(documents)}")
            print(f"文档内容示例: {documents[0].page_content[:100] if documents else '无内容'}")
            if not documents:
                return {
                    "success": False,
                    "message": "文档处理失败: 未能提取有效内容"
                }
            
            # 添加到向量数据库
            success = self._add_documents_to_vectorstore(documents, knowledge_base.vector_db_path, knowledge_base.embedding_model)
            if not success:
                return {
                    "success": False,
                    "message": "向量化处理失败"
                }
            
            # 保存文件记录到数据库
            knowledge_file = DatabaseService.create_knowledge_file(
                knowledge_base_id=knowledge_base_id,
                filename=unique_filename,
                original_filename=original_filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type=file_extension,
                document_count=len(documents),
                is_processed=True,
                db=db
            )
            
            if knowledge_file:
                # 更新知识库统计信息
                DatabaseService.update_knowledge_base_stats(knowledge_base_id, db)
                
                return {
                    "success": True,
                    "message": f"文件 '{original_filename}' 上传成功并已向量化",
                    "chunks": len(documents),
                    "file_id": knowledge_file.id
                }
            else:
                return {
                    "success": False,
                    "message": "文件记录保存失败"
                }
                
        except Exception as e:
            # 清理临时文件
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            return {
                "success": False,
                "message": f"文件上传失败: {str(e)}"
            }
    
    def get_rag_context(self, user_id: int, message: str, top_k: int = 3, db: Session = None) -> str:
        """
        获取RAG上下文 - 从用户的所有知识库中检索相关文档
        
        Args:
            user_id: 用户ID
            message: 用户消息
            top_k: 检索的文档数量
            db: 数据库会话
            
        Returns:
            str: RAG上下文字符串
        """
        try:
            # 获取用户的所有活跃知识库
            knowledge_bases = DatabaseService.get_user_active_knowledge_bases(user_id, db)
            if not knowledge_bases:
                print("没有活跃知识库")
                return ""
            
            all_results = []
            
            # 从每个知识库中检索
            for kb in knowledge_bases:
                print(f"检索知识库: {kb.name}")
                if kb.vector_db_path and os.path.exists(kb.vector_db_path):
                    search_response = self.search_knowledge_base(
                        message,
                        kb.vector_db_path,
                        kb.embedding_model,
                        top_k,
                    )
                    for result in search_response["results"]:
                        result["knowledge_base"] = kb.name
                    all_results.extend(search_response["results"])
            
            # 按相似度排序并取前top_k个
            all_results.sort(key=lambda item: item["score"], reverse=True)
            top_results = all_results[:top_k]
            
            if not top_results:
                return ""
            
            # 生成上下文
            context_parts = []
            for result in top_results:
                source = result.get("source") or result.get("knowledge_base") or "知识库"
                context_parts.append(f"[来源: {source}]\n{result['content']}")
            
            context = "\n".join(context_parts)
            print(f"RAG检索到 {len(top_results)} 条相关文档")
            
            return f"\n\n相关文档信息：\n{context}\n\n基于以上信息回答："
            
        except Exception as e:
            print(f"RAG上下文生成失败: {str(e)}")
            return ""
    
    def _process_document(self, file_path: str, file_type: str) -> List[Document]:
        """处理文档并返回分割后的文档块，使用优化的文本分割和标题增强"""
        try:
            # 根据文件类型选择加载器
            if file_type in ['txt', 'md']:
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                except Exception as e:
                    print(f"TextLoader 加载失败: {str(e)}")
                    loader = UnstructuredFileLoader(file_path)
            elif file_type == 'pdf':
                try:
                    loader = PyPDFLoader(file_path)
                except Exception:
                    print("PyPDFLoader 失败,使用 UnstructuredPDFLoader")
                    loader = UnstructuredPDFLoader(file_path)
            elif file_type in ['docx', 'doc']:
                try:
                    loader = Docx2txtLoader(file_path)
                except Exception:
                    print("Docx2txtLoader 失败,使用 UnstructuredWordDocumentLoader")
                    loader = UnstructuredWordDocumentLoader(file_path)
            else:
                loader = UnstructuredFileLoader(file_path)
            
            documents = loader.load()
            # 使用优化的文档处理（中文文本分割 + 标题增强）
            processed_documents = self.rag_chain_service.process_documents_with_enhancement(
                documents=documents,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                use_title_enhance=True
            )
            
            return processed_documents
        except Exception as e:
            print(f"文档处理失败: {str(e)}")
            return []
    
    def _add_documents_to_vectorstore(self, documents: List[Document], vector_db_path: str, embedding_model: str) -> bool:
        """将文档添加到指定知识库的向量数据库"""
        try:
            embeddings = OllamaEmbeddings(
                model=embedding_model,
                base_url=settings.OLLAMA_BASE_URL,
            )
            vectorstore = Chroma(
                persist_directory=vector_db_path,
                embedding_function=embeddings
            )
            
            if documents:
                vectorstore.add_documents(documents)
                print(f"成功添加 {len(documents)} 条文档到向量数据库: {vector_db_path}")
                return True
        except Exception as e:
            print(f"添加文档到向量数据库失败: {str(e)}")
        return False
    
    def search_knowledge_base(
        self,
        query: str,
        vector_db_path: str,
        embedding_model: str,
        top_k: int,
        min_score: float | None = None,
    ) -> Dict[str, Any]:
        """检索知识库并返回经过动态阈值过滤的结构化引用结果。"""
        try:
            embeddings = OllamaEmbeddings(
                model=embedding_model,
                base_url=settings.OLLAMA_BASE_URL,
            )
            vectorstore = Chroma(
                persist_directory=vector_db_path,
                embedding_function=embeddings
            )
            candidate_k = min(
                max(top_k, top_k * settings.SEARCH_CANDIDATE_MULTIPLIER),
                50,
            )
            docs_with_scores = vectorstore.similarity_search_with_relevance_scores(
                query, k=candidate_k
            )
            if not docs_with_scores:
                return {"threshold": None, "results": []}

            best_score = float(docs_with_scores[0][1])
            floor = settings.SEARCH_MIN_SCORE if min_score is None else min_score
            threshold = max(floor, best_score - settings.SEARCH_SCORE_MARGIN)

            results = []
            for doc, raw_score in docs_with_scores:
                score = float(raw_score)
                if score < threshold:
                    continue

                metadata = doc.metadata or {}
                raw_source = metadata.get("source") or metadata.get("file_name")
                source = os.path.basename(str(raw_source)) if raw_source else None

                page = metadata.get("page_number")
                if page is not None:
                    try:
                        page = int(page)
                    except (TypeError, ValueError):
                        page = None
                if page is None and metadata.get("page") is not None:
                    try:
                        page = int(metadata["page"]) + 1
                    except (TypeError, ValueError):
                        page = None

                section = (
                    metadata.get("section")
                    or metadata.get("title")
                    or metadata.get("heading")
                )
                results.append(
                    {
                        "content": doc.page_content,
                        "score": score,
                        "source": source,
                        "page": page,
                        "section": str(section) if section else None,
                    }
                )
                if len(results) >= top_k:
                    break

            return {"threshold": threshold, "results": results}
        except Exception as e:
            error_text = str(e).strip() or repr(e)
            raise RuntimeError(
                f"知识库检索失败，无法使用嵌入模型 '{embedding_model}'。"
                f"请确认 Ollama 服务可访问且模型已安装。原始错误: {error_text}"
            ) from e
    
    def _delete_vectors_from_chroma(self, vector_db_path: str, filename: str) -> bool:
        """从ChromaDB中删除指定文件的向量数据"""
        try:
            # 初始化嵌入模型（使用默认模型）
            embeddings = OllamaEmbeddings(
                model=settings.EMBEDDING_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
            )
            
            # 加载向量数据库
            vectorstore = Chroma(
                persist_directory=vector_db_path,
                embedding_function=embeddings
            )
            
            # 获取所有文档的元数据
            collection = vectorstore._collection
            
            # 获取所有文档
            all_results = collection.get()
            
            if not all_results['ids']:
                print(f"ChromaDB中没有找到任何文档")
                return False
            
            # 查找包含该文件名的文档
            matching_ids = []
            for i, metadata in enumerate(all_results['metadatas']):
                if metadata and 'source' in metadata:
                    source_path = metadata['source']
                    # 从source路径中提取文件名
                    source_filename = os.path.basename(source_path)
                    # 从原始文件名中提取文件名（去掉路径）
                    original_filename = os.path.basename(filename)
                    
                    print(f"比较: source_filename='{source_filename}' vs original_filename='{original_filename}'")
                    
                    # 检查原始文件名是否包含在source文件名中（处理时间戳前缀）
                    if original_filename in source_filename:
                        matching_ids.append(all_results['ids'][i])
                        print(f"找到匹配文档: {source_path}")
            
            if matching_ids:
                # 删除匹配的向量数据
                collection.delete(ids=matching_ids)
                print(f"从ChromaDB中删除了 {len(matching_ids)} 个向量")
                return True
            else:
                print(f"在ChromaDB中未找到文件 '{filename}' 的向量数据")
                return False
                
        except Exception as e:
            print(f"从ChromaDB删除向量数据失败: {str(e)}")
            return False
    
    def get_user_knowledge_bases(self, user_id: int, db: Session = None) -> List[Dict[str, Any]]:
        """获取用户的知识库列表"""
        try:
            print(f"正在从数据库获取用户 {user_id} 的知识库...")
            knowledge_bases = DatabaseService.get_user_knowledge_bases(user_id, db)
            print(f"从数据库获取到 {len(knowledge_bases)} 个知识库")
            
            result = []
            for kb in knowledge_bases:
                try:
                    kb_dict = {
                        "id": kb.id,
                        "user_id": kb.user_id,
                        "name": kb.name,
                        "description": kb.description,
                        "embedding_model": kb.embedding_model,
                        "vector_db_path": kb.vector_db_path,
                        "file_count": kb.file_count,
                        "document_count": kb.document_count,
                        "is_active": kb.is_active,
                        "created_at": kb.created_at,
                        "updated_at": kb.updated_at
                    }
                    result.append(kb_dict)
                except Exception as kb_error:
                    print(f"处理知识库对象时出错: {kb_error}")
                    print(f"知识库对象: {kb}")
                    continue
            
            print(f"成功处理 {len(result)} 个知识库")
            return result
        except Exception as e:
            print(f"获取用户知识库列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_knowledge_base_files(self, knowledge_base_id: int, user_id: int, db: Session = None) -> List[Dict[str, Any]]:
        """获取知识库的文件列表"""
        try:
            files = DatabaseService.get_knowledge_base_files(knowledge_base_id, user_id, db)
            result = []
            for file in files:
                result.append({
                    "id": file.id,
                    "filename": file.filename,
                    "original_filename": file.original_filename,
                    "file_path": file.file_path,
                    "file_size": file.file_size,
                    "file_type": file.file_type,
                    "document_count": file.document_count,
                    "is_processed": file.is_processed,
                    "created_at": file.created_at,
                    "updated_at": file.updated_at
                })
            return result
        except Exception as e:
            print(f"获取知识库文件列表失败: {str(e)}")
            return []
    
    def delete_knowledge_base(self, knowledge_base_id: int, user_id: int, db: Session = None) -> Dict[str, Any]:
        """删除知识库"""
        try:
            # 验证知识库是否存在且属于该用户
            knowledge_base = DatabaseService.get_knowledge_base_by_id(knowledge_base_id, user_id, db)
            if not knowledge_base:
                return {
                    "success": False,
                    "message": "知识库不存在或无权限访问"
                }
            
            # 删除向量数据库文件
            if knowledge_base.vector_db_path and os.path.exists(knowledge_base.vector_db_path):
                shutil.rmtree(knowledge_base.vector_db_path)
            
            # 删除上传的文件
            kb_upload_dir = os.path.join(self.base_upload_dir, f"user_{user_id}", f"kb_{knowledge_base.name}")
            if os.path.exists(kb_upload_dir):
                shutil.rmtree(kb_upload_dir)
            
            # 删除数据库记录
            success = DatabaseService.delete_knowledge_base(knowledge_base_id, user_id, db)
            
            if success:
                return {
                    "success": True,
                    "message": f"知识库 '{knowledge_base.name}' 删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "删除知识库失败"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"删除知识库失败: {str(e)}"
            }
    
    def delete_file_from_knowledge_base(self, file_id: int, knowledge_base_id: int, user_id: int, db: Session = None) -> Dict[str, Any]:
        """从知识库中删除文件"""
        try:
            # 验证文件是否存在且属于该知识库
            knowledge_file = DatabaseService.get_knowledge_file_by_id(file_id, knowledge_base_id, user_id, db)
            if not knowledge_file:
                return {
                    "success": False,
                    "message": "文件不存在或无权限访问"
                }
            
            # 获取知识库信息
            knowledge_base = DatabaseService.get_knowledge_base_by_id(knowledge_base_id, user_id, db)
            if not knowledge_base:
                return {
                    "success": False,
                    "message": "知识库不存在或无权限访问"
                }
            
            # 删除物理文件
            if os.path.exists(knowledge_file.file_path):
                os.remove(knowledge_file.file_path)
            
            # 从ChromaDB中删除向量数据
            try:
                if knowledge_base.vector_db_path and os.path.exists(knowledge_base.vector_db_path):
                    print(f"开始从ChromaDB删除文件 '{knowledge_file.original_filename}' 的向量数据...")
                    print(f"向量数据库路径: {knowledge_base.vector_db_path}")
                    # 使用文件名作为过滤条件删除向量数据
                    success = self._delete_vectors_from_chroma(knowledge_base.vector_db_path, knowledge_file.original_filename)
                    if success:
                        print(f"[OK] 已从ChromaDB中删除文件 '{knowledge_file.original_filename}' 的向量数据")
                    else:
                        print(f"[ERROR] 从ChromaDB删除文件 '{knowledge_file.original_filename}' 的向量数据失败")
                else:
                    print(f"[WARN] 向量数据库路径不存在: {knowledge_base.vector_db_path}")
            except Exception as e:
                print(f"从ChromaDB删除向量数据时出错: {str(e)}")
                import traceback
                traceback.print_exc()
                # 即使向量删除失败，也继续删除其他数据
            
            # 删除数据库记录
            success = DatabaseService.delete_knowledge_file(file_id, knowledge_base_id, user_id, db)
            
            if success:
                # 更新知识库统计信息
                DatabaseService.update_knowledge_base_stats(knowledge_base_id, db)
                
                return {
                    "success": True,
                    "message": f"文件 '{knowledge_file.original_filename}' 删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "删除文件失败"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"删除文件失败: {str(e)}"
            }


    def create_rag_chain_for_user(
        self, 
        user_id: int, 
        llm, 
        chain_type: str = "stuff",
        use_reranker: bool = True,
        top_k: int = 5,
        score_threshold: float = 0.5,
        use_wiki: bool = False,  # 添加Wiki知识支持
        db: Session = None
    ):
        """
        为用户创建RAG Chain
        
        Args:
            user_id: 用户ID
            llm: 语言模型
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
            # 如果启用Wiki知识，优先使用Wiki知识库
            if use_wiki:
                print("[SEARCH] 使用Wiki知识库进行RAG")
                
                wiki_kb = self.rag_chain_service.get_wiki_knowledge_base()
                if wiki_kb:
                    wiki_service = wiki_kb.wiki_service
                    
                    # 检查Wiki数据库是否可用
                    stats = wiki_service.get_database_stats()
                    if stats.get("service_type") in ["online", "offline"]:
                        print(f"[OK] Wiki数据库可用，模式: {wiki_service.mode}")
                        if stats.get("service_type") == "offline":
                            print(f"   包含 {stats['stats']['total_articles']} 篇文章")
                        # 使用Wiki知识库创建RAG Chain
                        return self.rag_chain_service.create_rag_chain_with_wiki(
                            wiki_service=wiki_service,
                            llm=llm,
                            chain_type=chain_type,
                            use_reranker=use_reranker,
                            top_k=top_k,
                            score_threshold=score_threshold
                        )
                    else:
                        print("[WARN] Wiki数据库不可用，回退到用户知识库")
                else:
                    print("[WARN] Wiki服务未初始化，回退到用户知识库")
            
            # 获取用户的第一个知识库（简化处理，实际可以支持多知识库）
            knowledge_bases = DatabaseService.get_user_knowledge_bases(user_id, db)
            print("用户知识库:", knowledge_bases)
            if not knowledge_bases:
                print(f"用户 {user_id} 没有知识库")
                return None
            
            # 使用第一个知识库
            kb = knowledge_bases[0]
            vector_db_path = kb.vector_db_path
            print(f"使用知识库 '{kb.name}' 的向量数据库: {vector_db_path}")
            print("用户的数据库有：", knowledge_bases)

            # 创建RAG Chain
            rag_chain = self.rag_chain_service.create_rag_chain(
                vector_db_path=vector_db_path,
                llm=llm,
                chain_type=chain_type,
                use_reranker=use_reranker,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            return rag_chain
            
        except Exception as e:
            print(f"创建RAG Chain失败: {str(e)}")
            return None
    
    def create_simple_chat_chain(
        self,
        llm
    ):
        """
        创建简单聊天Chain（不使用Prompt模板）
        
        Args:
            llm: 语言模型
            
        Returns:
            简单聊天Chain实例
        """
        return self.rag_chain_service.create_simple_chat_chain(llm)
    
    def create_chat_chain(
        self,
        llm,
        prompt_name: str = "chat_default"
    ):
        """
        创建聊天Chain
        
        Args:
            llm: 语言模型
            prompt_name: Prompt模板名称
            
        Returns:
            聊天Chain实例
        """
        return self.rag_chain_service.create_chat_chain(llm, prompt_name)
    
    def create_generation_chain(
        self,
        llm,
        prompt_name: str
    ):
        """
        创建生成任务Chain
        
        Args:
            llm: 语言模型
            prompt_name: Prompt模板名称
            
        Returns:
            生成Chain实例
        """
        return self.rag_chain_service.create_generation_chain(llm, prompt_name)
    
    def get_available_prompts(self):
        """获取可用的Prompt模板"""
        return self.rag_chain_service.get_available_prompts()
    
    def get_chain_types(self):
        """获取可用的Chain类型"""
        return self.rag_chain_service.get_chain_types()


# 全局知识库服务实例
knowledge_base_service = KnowledgeBaseService()
