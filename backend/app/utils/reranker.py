import os
from typing import Any, List, Optional, Sequence
from langchain_core.documents import Document
from langchain.callbacks.manager import Callbacks
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from pydantic import Field, PrivateAttr
import logging

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import CrossEncoder
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence_transformers not available. Reranker will not work.")


class LangchainReranker(BaseDocumentCompressor):
    """使用CrossEncoder进行文档重排序的压缩器"""
    
    model_name_or_path: str = Field(description="重排序模型名称或路径")
    _model: Any = PrivateAttr()
    top_n: int = Field(description="返回的top N个文档")
    device: str = Field(description="设备类型")
    max_length: int = Field(description="最大长度")
    batch_size: int = Field(description="批处理大小")
    num_workers: int = Field(description="工作进程数")

    def __init__(self,
                 model_name_or_path: str,
                 top_n: int = 3,
                 device: str = "cpu",
                 max_length: int = 512,  # 默认减小最大长度
                 batch_size: int = 8,    # 默认减小批次大小
                 num_workers: int = 0,   # 默认关闭多进程
                 ):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence_transformers is required for LangchainReranker")
            
        super().__init__(
            top_n=top_n,
            model_name_or_path=model_name_or_path,
            device=device,
            max_length=max_length,
            batch_size=batch_size,
            num_workers=num_workers,
        )
        print(f"初始化LangchainReranker，模型: {model_name_or_path}, 设备: {device}, 最大长度: {max_length}, 批次大小: {batch_size}, 工作进程数: {num_workers}")
        try:
            self._model = CrossEncoder(
                model_name_or_path=model_name_or_path, 
                max_length=max_length, 
                device=device
            )
            logger.info(f"成功加载重排序模型: {model_name_or_path}")
        except Exception as e:
            logger.error(f"加载重排序模型失败: {str(e)}")
            # 使用一个更小的备用模型
            try:
                logger.info("尝试使用备用重排序模型...")
                self._model = CrossEncoder(
                    model_name_or_path="cross-encoder/ms-marco-MiniLM-L-2-v2", 
                    max_length=256, 
                    device=device
                )
                logger.info("成功加载备用重排序模型")
            except Exception as e2:
                logger.error(f"备用模型也加载失败: {str(e2)}")
                raise e2

    def compress_documents(
            self,
            documents: Sequence[Document],
            query: str,
            callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        使用CrossEncoder重排序API压缩文档
        
        Args:
            documents: 要压缩的文档序列
            query: 用于压缩文档的查询
            callbacks: 压缩过程中运行的回调
            
        Returns:
            压缩后的文档序列
        """
        if len(documents) == 0:
            return []
            
        doc_list = list(documents)
        _docs = [d.page_content for d in doc_list]
        
        # 对文档进行长度截断，避免张量尺寸不匹配
        max_doc_length = self.max_length - 100  # 为query留出空间
        _docs = [doc[:max_doc_length] if len(doc) > max_doc_length else doc for doc in _docs]
        
        sentence_pairs = [[query, _doc] for _doc in _docs]
        
        try:
            # 使用较小的批次大小避免张量尺寸问题
            effective_batch_size = min(self.batch_size, len(sentence_pairs), 16)
            
            results = self._model.predict(
                sentences=sentence_pairs,
                batch_size=effective_batch_size,
                convert_to_tensor=True,
                show_progress_bar=False  # 关闭进度条
            )
            
            # 确保results是tensor类型
            if not hasattr(results, 'topk'):
                import torch
                results = torch.tensor(results)
            
            top_k = self.top_n if self.top_n < len(results) else len(results)
            values, indices = results.topk(top_k)
            
            final_results = []
            for value, index in zip(values, indices):
                doc = doc_list[index]
                doc.metadata["relevance_score"] = float(value)
                final_results.append(doc)
                
            return final_results
            
        except Exception as e:
            logger.error(f"重排序过程中发生错误: {str(e)}")
            logger.warning("重排序失败，返回原始文档顺序")
            # 如果重排序失败，返回原始文档的前top_n个
            return documents[:self.top_n] 