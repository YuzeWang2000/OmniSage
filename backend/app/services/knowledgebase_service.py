# 知识库服务
# KnowledgeBaseService
# 功能：
# 文件： 文件上传，文件下载，文件删除，文件列表获取，文件状态维护（mysql，知识库id，用户id，文件id）
# 向量知识库： 使用chroma实现，向量知识库的初始化，向量知识库的更新（添加，上传，重新生成），向量知识库的维护（mysql，知识库id和用户id）
# rag链：使用向量数据库和LLM获得检索链
# 检索：根据query检索知识库，使用检索的结果完善rag链，返回rag链的推理结果

import logging
import os
import shutil
import uuid
from pathlib import Path
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

SUPPORTED_FILE_EXTENSIONS = {"pdf", "txt", "md", "doc", "docx"}
logger = logging.getLogger(__name__)


class VectorStoreWriteError(RuntimeError):
    """A safe, actionable summary of an embedding or vector-store failure."""


class KnowledgeBaseService:
    """
    知识库服务类
    负责管理知识库的创建、文件上传、向量化、检索等操作
    所有知识库状态都记录在数据库中，每个知识库对应user_id和knowledge_id
    """
    
    def __init__(self):
        self.base_upload_dir = str(Path(os.getcwd(), settings.UPLOAD_DIR).resolve())
        self.base_vector_dir = str(Path(os.getcwd(), settings.VECTOR_DB_PATH).resolve())
        
        # 确保基础目录存在
        os.makedirs(self.base_upload_dir, exist_ok=True)
        os.makedirs(self.base_vector_dir, exist_ok=True)
        
        # 初始化优化的RAG Chain服务
        self.rag_chain_service = OptimizedRAGChainService()

    @staticmethod
    def _path_within(root: str, *parts: str) -> Path:
        root_path = Path(root).resolve()
        candidate = root_path.joinpath(*parts).resolve()
        if candidate == root_path or not candidate.is_relative_to(root_path):
            raise ValueError("storage path escaped its configured data root")
        return candidate

    def _upload_dir(self, user_id: int, knowledge_base_id: int) -> Path:
        return self._path_within(self.base_upload_dir, f"user_{user_id}", f"kb_{knowledge_base_id}")

    def _vector_dir(self, user_id: int, knowledge_base_id: int) -> Path:
        return self._path_within(self.base_vector_dir, f"user_{user_id}", f"kb_{knowledge_base_id}")

    @staticmethod
    def _validated_stored_path(root: str, value: str | None) -> Path | None:
        if not value:
            return None
        root_path = Path(root).resolve()
        candidate = Path(value).resolve()
        if candidate == root_path or not candidate.is_relative_to(root_path):
            raise ValueError("stored path is outside its configured data root")
        return candidate

    @staticmethod
    def _quarantine(path: Path) -> Path | None:
        if not path.exists():
            return None
        target = path.with_name(f".{path.name}.deleting-{uuid.uuid4().hex}")
        path.rename(target)
        return target

    @staticmethod
    def _restore_quarantine(quarantine: Path | None, original: Path) -> None:
        if quarantine and quarantine.exists() and not original.exists():
            quarantine.rename(original)
    
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
            
            # Persist first only far enough to obtain an immutable id. Display
            # names never participate in filesystem paths.
            knowledge_base = KnowledgeBase(
                user_id=user_id, name=name, description=description,
                embedding_model=embedding_model, file_count=0,
                document_count=0, is_active=True,
            )
            db.add(knowledge_base)
            db.flush()
            kb_dir = self._upload_dir(user_id, knowledge_base.id)
            vector_dir = self._vector_dir(user_id, knowledge_base.id)
            kb_dir.mkdir(parents=True, exist_ok=False)
            vector_dir.mkdir(parents=True, exist_ok=False)
            knowledge_base.vector_db_path = str(vector_dir)
            knowledge_base_id = knowledge_base.id
            db.commit()
            
            if knowledge_base:
                return {
                    "success": True,
                    "message": f"知识库 '{name}' 创建成功",
                    "knowledge_base_id": knowledge_base_id
                }
            else:
                return {
                    "success": False,
                    "message": "知识库创建失败"
                }
                
        except Exception:
            db.rollback()
            for created in (locals().get("kb_dir"), locals().get("vector_dir")):
                if isinstance(created, Path) and created.exists():
                    try:
                        shutil.rmtree(created)
                    except OSError:
                        logger.exception("清理创建失败的知识库目录失败")
            logger.exception("创建知识库失败")
            return {
                "success": False,
                "message": "创建知识库失败"
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
            
            # UploadFile.size 可提前拒绝，但写盘时仍会执行硬上限校验。
            if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "message": f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:g}MB)"
                }
            
            # 生成文件名和路径
            original_filename = (file.filename or "").strip()
            actual_filename = os.path.basename(original_filename.replace("\\", "/"))
            if not actual_filename:
                return {"success": False, "message": "文件名不能为空"}
            file_extension = os.path.splitext(actual_filename)[1].lower().lstrip(".")
            if file_extension not in SUPPORTED_FILE_EXTENSIONS:
                supported = ", ".join(sorted(SUPPORTED_FILE_EXTENSIONS))
                return {
                    "success": False,
                    "message": f"不支持的文件类型，仅支持: {supported}",
                }
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            unique_filename = f"{timestamp}_{actual_filename}"
            
            # 保存文件
            kb_upload_dir = self._upload_dir(user_id, knowledge_base.id)
            kb_upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = self._path_within(str(kb_upload_dir), unique_filename)
            
            total_size = 0
            with file_path.open("wb") as destination:
                while chunk := file.file.read(1024 * 1024):
                    total_size += len(chunk)
                    if total_size > settings.MAX_FILE_SIZE:
                        destination.close()
                        file_path.unlink()
                        return {
                            "success": False,
                            "message": f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:g}MB)",
                        }
                    destination.write(chunk)
            
            # 处理文档
            documents = self._process_document(file_path, file_extension)
            print(f"处理后的文档数量: {len(documents)}")
            if not documents:
                file_path.unlink()
                return {
                    "success": False,
                    "message": "文档处理失败: 未能提取有效内容"
                }
            
            # Create a pending SQL row and use its immutable id as the vector
            # ownership key. SQL is committed only after vector insertion.
            knowledge_file = KnowledgeFile(
                knowledge_base_id=knowledge_base_id,
                filename=unique_filename,
                original_filename=original_filename,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                file_type=file_extension,
                document_count=len(documents),
                is_processed=False,
            )
            db.add(knowledge_file)
            db.flush()
            for index, document in enumerate(documents):
                document.metadata = {
                    **(document.metadata or {}),
                    "file_id": str(knowledge_file.id),
                    "chunk_index": index,
                    "original_filename": original_filename,
                }
            success = self._add_documents_to_vectorstore(
                documents, knowledge_base.vector_db_path,
                knowledge_base.embedding_model, knowledge_file.id,
            )
            if not success:
                self._delete_vectors_from_chroma(
                    knowledge_base.vector_db_path, knowledge_file.id,
                )
                db.rollback()
                file_path.unlink(missing_ok=True)
                return {
                    "success": False,
                    "message": "向量化处理失败"
                }

            knowledge_file.is_processed = True
            knowledge_base.file_count += 1
            knowledge_base.document_count += len(documents)
            knowledge_file_id = knowledge_file.id
            db.commit()
            return {
                "success": True,
                "message": f"文件 '{original_filename}' 上传成功并已向量化",
                "chunks": len(documents),
                "file_id": knowledge_file_id
            }
                
        except VectorStoreWriteError as exc:
            file_id = getattr(locals().get("knowledge_file"), "id", None)
            if file_id and locals().get("knowledge_base"):
                self._delete_vectors_from_chroma(knowledge_base.vector_db_path, file_id)
            db.rollback()
            if "file_path" in locals():
                Path(file_path).unlink(missing_ok=True)
            logger.exception("文件向量化失败")
            return {"success": False, "message": str(exc)}
        except Exception:
            file_id = getattr(locals().get("knowledge_file"), "id", None)
            if file_id and locals().get("knowledge_base"):
                self._delete_vectors_from_chroma(knowledge_base.vector_db_path, file_id)
            db.rollback()
            # 清理临时文件
            if 'file_path' in locals() and Path(file_path).exists():
                try:
                    Path(file_path).unlink()
                except OSError:
                    logger.exception("清理失败的上传文件失败")
            logger.exception("文件上传或索引失败")
            return {"success": False, "message": "文件上传或索引失败"}

    def update_knowledge_base(
        self,
        knowledge_base_id: int,
        user_id: int,
        name: str,
        description: Optional[str],
        db: Session,
    ) -> Dict[str, Any]:
        """Update display metadata without moving the immutable ID-based data paths."""
        knowledge_base = DatabaseService.get_knowledge_base_by_id(
            knowledge_base_id, user_id, db,
        )
        if not knowledge_base:
            return {"success": False, "status": 404, "message": "知识库不存在"}
        duplicate = DatabaseService.get_knowledge_base_by_name(user_id, name, db)
        if duplicate and duplicate.id != knowledge_base_id:
            return {"success": False, "status": 409, "message": f"知识库名称 '{name}' 已存在"}
        try:
            knowledge_base.name = name
            knowledge_base.description = description
            knowledge_base.updated_at = datetime.now()
            db.commit()
            db.refresh(knowledge_base)
            return {"success": True, "knowledge_base": knowledge_base}
        except Exception:
            db.rollback()
            logger.exception("更新知识库失败")
            return {"success": False, "status": 500, "message": "更新知识库失败"}
    
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
            logger.error("RAG 上下文生成失败")
            return ""
    
    def _process_document(self, file_path: str, file_type: str) -> List[Document]:
        """处理文档并返回分割后的文档块，使用优化的文本分割和标题增强"""
        try:
            # 根据文件类型选择加载器
            if file_type in ['txt', 'md']:
                try:
                    loader = TextLoader(file_path, encoding="utf-8")
                except Exception as e:
                    logger.warning("TextLoader 加载失败，使用通用加载器")
                    loader = UnstructuredFileLoader(file_path)
            elif file_type == 'pdf':
                try:
                    loader = PyPDFLoader(file_path)
                except Exception:
                    logger.warning("PyPDFLoader 失败，使用备用加载器")
                    loader = UnstructuredPDFLoader(file_path)
            elif file_type in ['docx', 'doc']:
                try:
                    loader = Docx2txtLoader(file_path)
                except Exception:
                    logger.warning("Docx2txtLoader 失败，使用备用加载器")
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
            logger.error("文档处理失败")
            return []
    
    def _add_documents_to_vectorstore(self, documents: List[Document], vector_db_path: str, embedding_model: str, file_id: int) -> bool:
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
                sanitized = []
                for document in documents:
                    document.metadata = {
                        str(key): value
                        for key, value in (document.metadata or {}).items()
                        if value is not None and isinstance(value, (str, int, float, bool))
                    }
                    sanitized.append(document)
                batch_size = settings.VECTOR_WRITE_BATCH_SIZE
                for start in range(0, len(sanitized), batch_size):
                    batch = sanitized[start:start + batch_size]
                    vectorstore.add_documents(
                        batch,
                        ids=[
                            f"file-{file_id}-chunk-{index}"
                            for index in range(start, start + len(batch))
                        ],
                    )
                logger.info("成功添加 %s 条文档到向量数据库", len(documents))
                return True
        except Exception as exc:
            logger.exception("添加文档到向量数据库失败")
            message = str(exc).lower()
            if "connect" in message or "connection" in message:
                detail = "无法连接 Ollama，请确认服务已启动且 OLLAMA_BASE_URL 配置正确"
            elif "not found" in message or ("model" in message and "missing" in message):
                detail = f"嵌入模型 {embedding_model} 不可用，请先执行 ollama pull {embedding_model}"
            else:
                detail = "向量化处理失败，请检查后端日志中的具体 Ollama/Chroma 错误"
            raise VectorStoreWriteError(detail) from exc
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
            vector_db_path = str(self._validated_stored_path(self.base_vector_dir, vector_db_path))
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
        except Exception:
            logger.warning("知识库检索失败，嵌入服务不可用")
            raise RuntimeError(
                f"知识库检索失败，无法使用嵌入模型 '{embedding_model}'。"
                "请确认 Ollama 服务可访问且模型已安装。"
            )
    
    def _delete_vectors_from_chroma(
        self, vector_db_path: str, file_id: int,
        stored_file_path: str | None = None,
    ) -> dict | None:
        """Delete exactly one file's vectors and return a restorable snapshot."""
        try:
            vectorstore = Chroma(persist_directory=vector_db_path)
            collection = vectorstore._collection
            snapshot = collection.get(
                where={"file_id": str(file_id)},
                include=["documents", "metadatas", "embeddings"],
            )
            # Legacy chunks predate file_id metadata. Match their exact stored
            # source filename (never a substring) so old indexes remain
            # deletable without risking a.txt matching data.txt.
            if not snapshot.get("ids") and stored_file_path:
                all_items = collection.get(include=["documents", "metadatas", "embeddings"])
                expected_name = Path(stored_file_path).name
                indexes = [
                    index for index, metadata in enumerate(all_items.get("metadatas") or [])
                    if metadata and Path(str(metadata.get("source", ""))).name == expected_name
                ]
                snapshot = {
                    key: [values[index] for index in indexes]
                    for key, values in all_items.items()
                    if isinstance(values, list)
                }
            if snapshot.get("ids"):
                collection.delete(ids=snapshot["ids"])
            return snapshot
        except Exception:
            logger.exception("从 ChromaDB 删除向量数据失败")
            return None

    @staticmethod
    def _restore_vectors(vector_db_path: str, snapshot: dict | None) -> None:
        if not snapshot or not snapshot.get("ids"):
            return
        collection = Chroma(persist_directory=vector_db_path)._collection
        collection.add(
            ids=snapshot["ids"], documents=snapshot.get("documents"),
            metadatas=snapshot.get("metadatas"), embeddings=snapshot.get("embeddings"),
        )
    
    def get_user_knowledge_bases(self, user_id: int, db: Session = None) -> List[Dict[str, Any]]:
        """获取用户的知识库列表"""
        try:
            knowledge_bases = DatabaseService.get_user_knowledge_bases(user_id, db)
            
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
                except Exception:
                    logger.error("处理知识库对象失败")
                    continue
            
            return result
        except Exception as e:
            logger.error("获取用户知识库列表失败")
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
            logger.error("获取知识库文件列表失败")
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
            
            vector_dir = self._validated_stored_path(
                self.base_vector_dir, knowledge_base.vector_db_path,
            ) or self._vector_dir(user_id, knowledge_base_id)
            upload_dirs = {self._upload_dir(user_id, knowledge_base_id)}
            for knowledge_file in knowledge_base.files:
                stored_file = self._validated_stored_path(
                    self.base_upload_dir, knowledge_file.file_path,
                )
                if stored_file:
                    upload_dirs.add(stored_file.parent)
            vector_quarantine = self._quarantine(vector_dir)
            upload_quarantines = [
                (directory, self._quarantine(directory))
                for directory in sorted(upload_dirs, key=lambda item: len(item.parts), reverse=True)
                if directory.exists()
            ]

            knowledge_base.is_active = False
            knowledge_base.updated_at = datetime.now()
            try:
                db.commit()
                success = True
            except Exception:
                db.rollback()
                self._restore_quarantine(vector_quarantine, vector_dir)
                for original, quarantined in reversed(upload_quarantines):
                    self._restore_quarantine(quarantined, original)
                raise
            
            if success:
                for quarantined in (vector_quarantine, *(item[1] for item in upload_quarantines)):
                    if quarantined and quarantined.exists():
                        try:
                            shutil.rmtree(quarantined)
                        except OSError:
                            logger.exception("清理已删除知识库的隔离目录失败")
                return {
                    "success": True,
                    "message": f"知识库 '{knowledge_base.name}' 删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "删除知识库失败"
                }
                
        except ValueError:
            logger.exception("拒绝删除越界的知识库存储路径")
            return {"success": False, "message": "知识库存储路径不安全，已拒绝删除"}
        except Exception:
            logger.exception("删除知识库失败")
            return {
                "success": False,
                "message": "删除知识库失败"
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
            
            file_path = self._validated_stored_path(self.base_upload_dir, knowledge_file.file_path)
            vector_path = self._validated_stored_path(self.base_vector_dir, knowledge_base.vector_db_path)
            file_quarantine = self._quarantine(file_path) if file_path else None
            vector_snapshot = self._delete_vectors_from_chroma(
                str(vector_path), file_id, knowledge_file.file_path,
            ) if vector_path and vector_path.exists() else {"ids": []}
            if vector_snapshot is None:
                self._restore_quarantine(file_quarantine, file_path)
                return {"success": False, "message": "向量索引删除失败，未删除文件记录"}

            db.delete(knowledge_file)
            knowledge_base.file_count = max(0, knowledge_base.file_count - 1)
            knowledge_base.document_count = max(0, knowledge_base.document_count - knowledge_file.document_count)
            try:
                db.commit()
                success = True
            except Exception:
                db.rollback()
                self._restore_vectors(str(vector_path), vector_snapshot)
                self._restore_quarantine(file_quarantine, file_path)
                raise
            
            if success:
                if file_quarantine and file_quarantine.exists():
                    file_quarantine.unlink()
                return {
                    "success": True,
                    "message": f"文件 '{knowledge_file.original_filename}' 删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "删除文件失败"
                }
                
        except ValueError:
            logger.exception("拒绝删除越界的知识库文件路径")
            return {"success": False, "message": "文件存储路径不安全，已拒绝删除"}
        except Exception:
            logger.exception("删除知识库文件失败")
            return {
                "success": False,
                "message": "删除文件失败"
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
        knowledge_base_id: int | None = None,
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
            
            if knowledge_base_id is not None:
                kb = DatabaseService.get_knowledge_base_by_id(
                    knowledge_base_id,
                    user_id,
                    db,
                )
                if not kb:
                    return None
            else:
                # 保持旧客户端行为：未指定时使用最近更新的第一个知识库。
                knowledge_bases = DatabaseService.get_user_knowledge_bases(user_id, db)
                if not knowledge_bases:
                    logger.info("当前用户没有可用知识库")
                    return None
                kb = knowledge_bases[0]
            vector_db_path = kb.vector_db_path
            logger.debug("使用已授权知识库创建 RAG Chain")

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
            
        except Exception:
            logger.error("创建 RAG Chain 失败")
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
