"""
优化的RAG Chain服务
使用LangChain的Chain实现，支持多种优化策略
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain.chains import LLMChain, RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..utils.text_splitter import ChineseRecursiveTextSplitter
from ..utils.title_enhancer import zh_title_enhance
from ..utils.reranker import LangchainReranker
from ..utils.prompts import prompt_manager
from ..config import settings
from .wiki_service import WikiKnowledgeBase, WikiService

logger = logging.getLogger(__name__)


class OptimizedRAGChainService:
    """
    优化的RAG Chain服务
    集成了多种优化策略：
    1. 中文文本分割
    2. 标题增强
    3. 重排序
    4. 上下文压缩
    5. 多种Chain类型
    """
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=settings.EMBEDDING_MODEL)
        self.base_vector_dir = settings.VECTOR_DB_PATH
        
        # 确保基础目录存在
        os.makedirs(self.base_vector_dir, exist_ok=True)
        
        # 初始化Wiki服务（默认使用自动模式）
        try:
            self.wiki_service = WikiService(mode="auto")  # 使用自动模式
            self.wiki_kb = WikiKnowledgeBase(self.wiki_service)
            logger.info(f"使用{self.wiki_service.mode}维基百科服务")
        except Exception as e:
            logger.error(f"所有Wiki服务都不可用: {str(e)}")
            self.wiki_kb = None
    
    def create_rag_chain(
        self,
        vector_db_path: str,
        llm: BaseLanguageModel,
        chain_type: str = "stuff",
        use_reranker: bool = True,
        use_title_enhance: bool = True,
        top_k: int = 5,
        score_threshold: float = 0.5,
        use_wiki: bool = False,
        **kwargs
    ) -> Any:
        """
        创建优化的RAG Chain
        
        Args:
            vector_db_path: 向量数据库路径
            llm: 语言模型
            chain_type: Chain类型 ("stuff", "map_reduce", "refine", "map_rerank")
            use_reranker: 是否使用重排序
            use_title_enhance: 是否使用标题增强
            top_k: 检索文档数量
            score_threshold: 相似度阈值
            **kwargs: 其他参数
            
        Returns:
            RAG Chain实例
        """
        try:
            # 加载向量数据库
            vectorstore = self._load_vectorstore(vector_db_path)
            if not vectorstore:
                logger.error(f"无法加载向量数据库: {vector_db_path}")
                return None
            
            # 创建检索器
            retriever = self._create_retriever(
                vectorstore, 
                top_k=top_k, 
                score_threshold=score_threshold,
                use_reranker=use_reranker
            )
            
            # 创建Chain
            if chain_type == "stuff":
                return self._create_stuff_chain(retriever, llm, use_wiki=use_wiki, **kwargs)
            elif chain_type == "map_reduce":
                return self._create_map_reduce_chain(retriever, llm, use_wiki=use_wiki, **kwargs)
            elif chain_type == "refine":
                return self._create_refine_chain(retriever, llm, use_wiki=use_wiki, **kwargs)
            elif chain_type == "map_rerank":
                return self._create_map_rerank_chain(retriever, llm, use_wiki=use_wiki, **kwargs)
            else:
                logger.warning(f"不支持的chain类型: {chain_type}，使用stuff")
                return self._create_stuff_chain(retriever, llm, use_wiki=use_wiki, **kwargs)
                
        except Exception as e:
            logger.error(f"创建RAG Chain失败: {str(e)}")
            return None
    
    def create_simple_chat_chain(
        self,
        llm: BaseLanguageModel,
        **kwargs
    ) -> Any:
        """
        创建简单的聊天Chain（不使用Prompt模板，直接使用LLM）
        
        Args:
            llm: 语言模型
            **kwargs: 其他参数
            
        Returns:
            简单的聊天Chain实例
        """
        try:
            # 创建一个简单的Chain，直接使用LLM处理消息
            class SimpleChatChain:
                def __init__(self, llm):
                    self.llm = llm
                
                def invoke(self, messages):
                    """直接调用LLM处理消息"""
                    return self.llm.invoke(messages)
                
                def stream(self, messages):
                    """流式调用LLM处理消息"""
                    return self.llm.stream(messages)
            
            return SimpleChatChain(llm)
        except Exception as e:
            logger.error(f"创建简单聊天Chain失败: {str(e)}")
            return None
    
    def create_chat_chain(
        self,
        llm: BaseLanguageModel,
        prompt_name: str = "chat_default",
        **kwargs
    ) -> Any:
        """
        创建普通聊天Chain
        
        Args:
            llm: 语言模型
            prompt_name: Prompt模板名称
            **kwargs: 其他参数
            
        Returns:
            聊天Chain实例
        """
        try:
            prompt = prompt_manager.get_prompt(prompt_name)
            # 使用新的RunnableSequence API
            return prompt | llm
        except Exception as e:
            logger.error(f"创建聊天Chain失败: {str(e)}")
            return None
    
    def create_generation_chain(
        self,
        llm: BaseLanguageModel,
        prompt_name: str,
        **kwargs
    ) -> Any:
        """
        创建生成任务Chain
        
        Args:
            llm: 语言模型
            prompt_name: Prompt模板名称
            **kwargs: 其他参数
            
        Returns:
            生成Chain实例
        """
        try:
            prompt = prompt_manager.get_prompt(prompt_name)
            # 使用新的RunnableSequence API
            return prompt | llm
        except Exception as e:
            logger.error(f"创建生成Chain失败: {str(e)}")
            return None
    
    def create_rag_chain_with_wiki(
        self,
        wiki_service: WikiService,
        llm: BaseLanguageModel,
        chain_type: str = "stuff",
        use_reranker: bool = True,
        top_k: int = 5,
        score_threshold: float = 0.5,
        **kwargs
    ) -> Any:
        """
        创建基于Wiki知识库的RAG Chain
        
        Args:
            wiki_service: Wiki服务实例
            llm: 语言模型
            chain_type: Chain类型
            use_reranker: 是否使用重排序
            top_k: 检索文档数量
            score_threshold: 相似度阈值
            **kwargs: 其他参数
            
        Returns:
            RAG Chain实例
        """
        try:
            # 创建基于Wiki的检索器
            wiki_kb = WikiKnowledgeBase(wiki_service)
            
            # 创建基础Chain
            if chain_type == "stuff":
                base_chain = self._create_wiki_stuff_chain(wiki_kb, llm, top_k, score_threshold)
            elif chain_type == "map_reduce":
                base_chain = self._create_wiki_map_reduce_chain(wiki_kb, llm, top_k, score_threshold)
            elif chain_type == "refine":
                base_chain = self._create_wiki_refine_chain(wiki_kb, llm, top_k, score_threshold)
            elif chain_type == "map_rerank":
                base_chain = self._create_wiki_map_rerank_chain(wiki_kb, llm, top_k, score_threshold)
            else:
                logger.warning(f"不支持的Chain类型: {chain_type}，使用stuff")
                base_chain = self._create_wiki_stuff_chain(wiki_kb, llm, top_k, score_threshold)
            
            return base_chain
            
        except Exception as e:
            logger.error(f"创建Wiki RAG Chain失败: {str(e)}")
            return None
    
    def _create_wiki_stuff_chain(self, wiki_kb: WikiKnowledgeBase, llm: BaseLanguageModel, top_k: int = 5, score_threshold: float = 0.5):
        """创建基于Wiki的stuff chain"""
        class WikiStuffChain:
            def __init__(self, wiki_kb, llm):
                self.wiki_kb = wiki_kb
                self.llm = llm
                
            def invoke(self, inputs):
                query = inputs.get("input", "")
                
                # 搜索Wiki知识
                wiki_results = self.wiki_kb.search_knowledge(query, limit=top_k)
                
                # 构建上下文
                context = ""
                if wiki_results:
                    context = "基于维基百科知识：\n"
                    for i, result in enumerate(wiki_results, 1):
                        context += f"{i}. {result['title']}: {result['content']}\n"
                
                # 构建提示词
                prompt = f"""你是一个智能助手，请基于以下维基百科知识来回答用户的问题。

{context}

用户问题: {query}

请提供准确、详细的回答，如果维基百科知识不足以回答问题，请说明并尝试提供一般性的回答。

回答:"""
                
                # 调用LLM
                response = self.llm.invoke(prompt)
                return {"answer": response.content if hasattr(response, 'content') else str(response)}
            
            def stream(self, inputs):
                query = inputs.get("input", "")
                
                # 搜索Wiki知识
                wiki_results = self.wiki_kb.search_knowledge(query, limit=top_k)
                
                # 构建上下文
                context = ""
                if wiki_results:
                    context = "基于维基百科知识：\n"
                    for i, result in enumerate(wiki_results, 1):
                        context += f"{i}. {result['title']}: {result['content']}\n"
                
                # 构建提示词
                prompt = f"""你是一个智能助手，请基于以下维基百科知识来回答用户的问题。

{context}

用户问题: {query}

请提供准确、详细的回答，如果维基百科知识不足以回答问题，请说明并尝试提供一般性的回答。

回答:"""
                
                # 流式调用LLM
                try:
                    # 尝试使用流式调用
                    if hasattr(self.llm, 'stream'):
                        for chunk in self.llm.stream(prompt):
                            # 直接yield chunk对象，让process_message处理
                            yield chunk
                    else:
                        # 如果不支持流式，使用普通调用
                        response = self.llm.invoke(prompt)
                        content = response.content if hasattr(response, 'content') else str(response)
                        # 按字符流式输出
                        for char in content:
                            yield char
                except Exception as e:
                    # 如果流式调用失败，回退到普通调用
                    try:
                        response = self.llm.invoke(prompt)
                        content = response.content if hasattr(response, 'content') else str(response)
                        # 按字符流式输出
                        for char in content:
                            yield char
                    except Exception as e2:
                        yield f"❌ 处理失败: {str(e2)}"
        
        return WikiStuffChain(wiki_kb, llm)
    
    def _create_wiki_map_reduce_chain(self, wiki_kb: WikiKnowledgeBase, llm: BaseLanguageModel, top_k: int = 5, score_threshold: float = 0.5):
        """创建基于Wiki的map_reduce chain（简化版本）"""
        return self._create_wiki_stuff_chain(wiki_kb, llm, top_k, score_threshold)
    
    def _create_wiki_refine_chain(self, wiki_kb: WikiKnowledgeBase, llm: BaseLanguageModel, top_k: int = 5, score_threshold: float = 0.5):
        """创建基于Wiki的refine chain（简化版本）"""
        return self._create_wiki_stuff_chain(wiki_kb, llm, top_k, score_threshold)
    
    def _create_wiki_map_rerank_chain(self, wiki_kb: WikiKnowledgeBase, llm: BaseLanguageModel, top_k: int = 5, score_threshold: float = 0.5):
        """创建基于Wiki的map_rerank chain（简化版本）"""
        return self._create_wiki_stuff_chain(wiki_kb, llm, top_k, score_threshold)
    
    def _load_vectorstore(self, vector_db_path: str) -> Optional[Chroma]:
        """加载向量数据库"""
        try:
            if os.path.exists(vector_db_path):
                return Chroma(
                    persist_directory=vector_db_path,
                    embedding_function=self.embeddings
                )
            else:
                logger.warning(f"向量数据库路径不存在: {vector_db_path}")
                return None
        except Exception as e:
            logger.error(f"加载向量数据库失败: {str(e)}")
            return None
    
    def _create_retriever(
        self, 
        vectorstore: Chroma, 
        top_k: int = 5,
        score_threshold: float = 0.5,
        use_reranker: bool = True
    ):
        """创建检索器"""
        # 基础检索器
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": top_k * 2 if use_reranker else top_k,  # 如果使用重排序，检索更多文档
                "score_threshold": score_threshold
            }
        )
        
        # 如果启用重排序
        if use_reranker:
            try:
                reranker = LangchainReranker(
                    model_name_or_path="BAAI/bge-reranker-large",
                    top_n=top_k,
                    device="cpu"
                )
                retriever = ContextualCompressionRetriever(
                    base_retriever=retriever,
                    base_compressor=reranker
                )
                logger.info("成功启用重排序功能")
            except Exception as e:
                logger.warning(f"重排序初始化失败，使用基础检索器: {str(e)}")
        
        return retriever
    
    def _create_stuff_chain(self, retriever, llm: BaseLanguageModel, use_wiki: bool = False, **kwargs):
        """创建Stuff Chain"""
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.prompts import PromptTemplate
        
        # 创建适合文档组合的prompt
        prompt_template = PromptTemplate(
            input_variables=["context", "input"],
            template="""你是一个有用的AI助手。请基于以下上下文信息来回答用户的问题。
如果上下文中没有相关信息，请说明你无法从提供的信息中找到答案，但可以基于你的知识来回答。

上下文信息：
{context}

请记住：
1. 优先使用上下文中的信息来回答问题
2. 如果上下文信息不足，可以补充你的知识
3. 回答要准确、有用、友好
4. 如果问题超出你的能力范围，请诚实说明

问题：{input}"""
        )
        
        # 创建文档组合chain
        document_chain = create_stuff_documents_chain(llm, prompt_template)
        
        # 创建检索chain
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        # 如果启用Wiki，包装chain以增强上下文
        if use_wiki:
            return self._create_wiki_enhanced_chain(retrieval_chain)
        
        return retrieval_chain
    
    def _create_wiki_enhanced_chain(self, base_chain):
        """
        创建Wiki增强的Chain
        在原有RAG基础上增加Wiki知识
        """
        class WikiEnhancedChain:
            def __init__(self, base_chain, wiki_kb):
                self.base_chain = base_chain
                self.wiki_kb = wiki_kb
            
            def invoke(self, inputs):
                # 获取原始查询
                query = inputs.get("input", "")
                
                # 获取Wiki增强的上下文
                enhanced_context = self.wiki_kb.get_enhanced_context(query)
                
                # 如果Wiki提供了额外信息，修改输入
                if "=== 维基百科补充信息 ===" in enhanced_context:
                    # 创建新的输入，包含Wiki信息
                    enhanced_inputs = inputs.copy()
                    enhanced_inputs["wiki_context"] = enhanced_context
                    
                    # 调用基础chain
                    result = self.base_chain.invoke(enhanced_inputs)
                    
                    # 在结果中添加Wiki来源信息
                    if hasattr(result, 'answer'):
                        result.answer += "\n\n---\n*部分信息来源于维基百科*"
                    elif isinstance(result, dict) and 'answer' in result:
                        result['answer'] += "\n\n---\n*部分信息来源于维基百科*"
                    
                    return result
                else:
                    # 如果没有Wiki信息，直接使用基础chain
                    return self.base_chain.invoke(inputs)
            
            def stream(self, inputs):
                # 获取原始查询
                query = inputs.get("input", "")
                
                # 获取Wiki增强的上下文
                enhanced_context = self.wiki_kb.get_enhanced_context(query)
                
                # 如果Wiki提供了额外信息
                if "=== 维基百科补充信息 ===" in enhanced_context:
                    # 创建新的输入，包含Wiki信息
                    enhanced_inputs = inputs.copy()
                    enhanced_inputs["wiki_context"] = enhanced_context
                    
                    # 流式调用基础chain
                    for chunk in self.base_chain.stream(enhanced_inputs):
                        yield chunk
                    
                    # 在最后添加Wiki来源信息
                    yield "\n\n---\n*部分信息来源于维基百科*"
                else:
                    # 如果没有Wiki信息，直接使用基础chain
                    for chunk in self.base_chain.stream(inputs):
                        yield chunk
        
        return WikiEnhancedChain(base_chain, self.wiki_kb)
    
    def _create_map_reduce_chain(self, retriever, llm: BaseLanguageModel, use_wiki: bool = False, **kwargs):
        """创建Map-Reduce Chain"""
        prompt = prompt_manager.get_prompt("rag_default")
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="map_reduce",
            retriever=retriever,
            chain_type_kwargs={
                "prompt": prompt,
                **kwargs
            }
        )
        
        # 如果启用Wiki，包装chain以增强上下文
        if use_wiki:
            return self._create_wiki_enhanced_chain(chain)
        
        return chain
    
    def _create_refine_chain(self, retriever, llm: BaseLanguageModel, use_wiki: bool = False, **kwargs):
        """创建Refine Chain"""
        prompt = prompt_manager.get_prompt("rag_default")
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="refine",
            retriever=retriever,
            chain_type_kwargs={
                "prompt": prompt,
                **kwargs
            }
        )
        
        # 如果启用Wiki，包装chain以增强上下文
        if use_wiki:
            return self._create_wiki_enhanced_chain(chain)
        
        return chain
    
    def _create_map_rerank_chain(self, retriever, llm: BaseLanguageModel, use_wiki: bool = False, **kwargs):
        """创建Map-Rerank Chain"""
        prompt = prompt_manager.get_prompt("rag_default")
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="map_rerank",
            retriever=retriever,
            chain_type_kwargs={
                "prompt": prompt,
                **kwargs
            }
        )
        
        # 如果启用Wiki，包装chain以增强上下文
        if use_wiki:
            return self._create_wiki_enhanced_chain(chain)
        
        return chain
    
    def process_documents_with_enhancement(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        use_title_enhance: bool = True
    ) -> List[Document]:
        """
        使用增强功能处理文档
        
        Args:
            documents: 原始文档列表
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            use_title_enhance: 是否使用标题增强
            
        Returns:
            处理后的文档列表
        """
        try:
            # 使用中文文本分割器
            text_splitter = ChineseRecursiveTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                keep_separator=True,
                is_separator_regex=True
            )
            
            # 分割文档
            split_docs = []
            for doc in documents:
                splits = text_splitter.split_documents([doc])
                split_docs.extend(splits)
            
            # 标题增强
            if use_title_enhance:
                split_docs = zh_title_enhance(split_docs)
                logger.info("已应用标题增强")
            
            logger.info(f"文档处理完成，共生成 {len(split_docs)} 个文档块")
            return split_docs
            
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return documents
    
    def get_available_prompts(self) -> Dict[str, str]:
        """获取可用的Prompt模板"""
        return prompt_manager.list_prompts()
    
    def get_chain_types(self) -> Dict[str, str]:
        """获取可用的Chain类型"""
        return {
            "stuff": "Stuff Chain - 将所有检索到的文档合并到一个上下文中",
            "map_reduce": "Map-Reduce Chain - 分别处理每个文档，然后合并结果",
            "refine": "Refine Chain - 迭代地改进答案",
            "map_rerank": "Map-Rerank Chain - 为每个文档生成答案并排序"
        } 