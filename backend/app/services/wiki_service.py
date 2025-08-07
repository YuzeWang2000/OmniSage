#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的Wiki知识服务
支持在线和离线模式，默认使用离线模式
集成zhwiki数据处理，使用Chroma向量数据库
"""

import os
import json
import logging
import requests
import subprocess
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

@dataclass
class WikiArticle:
    """维基百科文章"""
    title: str
    content: str
    url: str
    categories: List[str]
    links: List[str]
    summary: str
    article_id: Optional[int] = None

class WikiService:
    """统一的Wiki知识服务"""
    
    def __init__(self, mode: str = "auto", data_dir: str = "wiki_data"):
        """
        初始化Wiki服务
        
        Args:
            mode: 服务模式，"online"、"offline" 或 "auto"，默认为 "auto"
            data_dir: 离线数据目录
        """
        self.mode = mode
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 向量数据库路径
        self.vector_db_path = self.data_dir / "wiki_vectors"
        self.vector_db_path.mkdir(exist_ok=True)
        
        # 维基百科数据转储URL
        self.wiki_dump_url = "https://dumps.wikimedia.org/zhwiki/latest/"
        self.articles_file = "zhwiki-latest-pages-articles.xml.bz2"
        
        # 在线API配置
        self.wikipedia_api_url = "https://zh.wikipedia.org/api/rest_v1"
        self.search_api_url = "https://zh.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OmniSage/1.0 (https://github.com/your-repo)'
        })
        
        # 嵌入模型
        self.embedding_model = "nomic-embed-text"
        self.embeddings = OllamaEmbeddings(model=self.embedding_model)
        
        # 根据模式初始化服务
        if self.mode == "auto":
            self._init_auto_mode()
        elif self.mode == "online":
            self._init_online_mode()
        elif self.mode == "offline":
            self._init_offline_mode()
    
    def _init_auto_mode(self):
        """自动模式：优先使用在线模式，失败时切换到离线模式"""
        try:
            # 测试在线模式是否可用
            test_response = self.session.get(f"{self.wikipedia_api_url}/page/summary/测试", timeout=5)
            if test_response.status_code == 200:
                self.mode = "online"
                logger.info("✅ 在线维基百科服务可用，使用在线模式")
                return
        except Exception as e:
            logger.warning(f"在线模式不可用: {str(e)}")
        
        # 在线模式不可用，尝试离线模式
        try:
            self._init_vectorstore()
            if self._check_offline_available():
                self.mode = "offline"
                logger.info("✅ 离线维基百科服务可用，使用离线模式")
            else:
                # 离线模式也不可用，强制使用在线模式（可能会失败）
                self.mode = "online"
                logger.warning("⚠️ 离线模式不可用，强制使用在线模式")
        except Exception as e:
            logger.error(f"离线模式初始化失败: {str(e)}")
            self.mode = "online"
            logger.warning("⚠️ 强制使用在线模式")
    
    def _init_online_mode(self):
        """初始化在线模式"""
        self.mode = "online"
        logger.info("✅ 使用在线维基百科服务")
    
    def _init_offline_mode(self):
        """初始化离线模式"""
        self.mode = "offline"
        self._init_vectorstore()
        if not self._check_offline_available():
            logger.warning("⚠️ 离线模式不可用，将回退到在线模式")
            self.mode = "online"
        else:
            logger.info("✅ 使用离线维基百科服务")
    
    def switch_mode(self, new_mode: str) -> bool:
        """
        切换服务模式
        
        Args:
            new_mode: 新的服务模式，"online" 或 "offline"
        
        Returns:
            bool: 切换是否成功
        """
        if new_mode == self.mode:
            return True
        
        if new_mode == "online":
            try:
                # 测试在线模式是否可用
                test_response = self.session.get(f"{self.wikipedia_api_url}/page/summary/测试", timeout=5)
                if test_response.status_code == 200:
                    self.mode = "online"
                    logger.info("✅ 切换到在线维基百科服务")
                    return True
                else:
                    logger.error("❌ 在线模式不可用")
                    return False
            except Exception as e:
                logger.error(f"❌ 在线模式不可用: {str(e)}")
                return False
        
        elif new_mode == "offline":
            try:
                self._init_vectorstore()
                if self._check_offline_available():
                    self.mode = "offline"
                    logger.info("✅ 切换到离线维基百科服务")
                    return True
                else:
                    logger.error("❌ 离线模式不可用")
                    return False
            except Exception as e:
                logger.error(f"❌ 离线模式不可用: {str(e)}")
                return False
        
        return False
    
    def _init_vectorstore(self):
        """初始化Chroma向量数据库"""
        try:
            self.vectorstore = Chroma(
                collection_name="wiki_articles",  # 指定collection名称
                persist_directory=str(self.vector_db_path),
                embedding_function=self.embeddings
            )
            logger.info("Chroma向量数据库初始化完成")
        except Exception as e:
            logger.error(f"向量数据库初始化失败: {str(e)}")
            # 如果初始化失败，设置为None，后续会回退到在线模式
            self.vectorstore = None
    
    def _check_offline_available(self) -> bool:
        """检查离线模式是否可用"""
        try:
            if not hasattr(self, 'vectorstore') or self.vectorstore is None:
                logger.debug("vectorstore is None")
                return False
            
            # 检查向量数据库是否有数据
            collection = self.vectorstore._collection
            if collection is None:
                logger.debug("collection is None")
                return False
                
            count = collection.count()
            logger.debug(f"Vector database has {count} documents")
            return count > 0
        except Exception as e:
            logger.error(f"检查离线模式可用性失败: {str(e)}")
            return False
    
    def download_wiki_dump(self, force_download: bool = False) -> bool:
        """
        下载维基百科数据转储
        """
        if self.mode != "offline":
            logger.warning("在线模式不需要下载数据转储")
            return True
            
        dump_file = self.data_dir / self.articles_file
        
        if dump_file.exists() and not force_download:
            logger.info("维基百科数据转储已存在，跳过下载")
            return True
        
        try:
            logger.info("开始下载维基百科数据转储...")
            url = f"{self.wiki_dump_url}{self.articles_file}"
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dump_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"下载进度: {progress:.1f}%")
            
            logger.info("维基百科数据转储下载完成")
            return True
            
        except Exception as e:
            logger.error(f"下载维基百科数据转储失败: {str(e)}")
            return False
    
    def install_wikiextractor(self) -> bool:
        """
        安装WikiExtractor
        """
        if self.mode != "offline":
            return True
            
        try:
            logger.info("检查WikiExtractor...")
            
            # 检查是否已安装
            result = subprocess.run(['wikiextractor', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("WikiExtractor已安装")
                return True
            
            # 尝试安装
            logger.info("安装WikiExtractor...")
            subprocess.run(['pip', 'install', 'wikiextractor'], check=True)
            
            logger.info("WikiExtractor安装完成")
            return True
            
        except Exception as e:
            logger.error(f"安装WikiExtractor失败: {str(e)}")
            return False
    
    def process_extracted_articles(self, extract_dir: str = "extracted") -> bool:
        """
        处理提取的文章并存储到向量数据库
        """
        if self.mode != "offline":
            logger.warning("在线模式不需要处理提取的文章")
            return True
            
        try:
            extract_path = self.data_dir / extract_dir
            
            if not extract_path.exists():
                logger.error("提取目录不存在")
                return False
            
            logger.info("开始处理提取的文章...")
            
            # 初始化文本分割器
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
            )
            
            processed_count = 0
            documents = []
            
            # 遍历所有提取的文件
            for file_path in extract_path.rglob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            article_data = json.loads(line.strip())
                            
                            # 提取文章信息
                            title = article_data.get('title', '')
                            content = article_data.get('text', '')
                            
                            # 跳过重定向和特殊页面
                            if title.startswith('Wikipedia:') or title.startswith('Template:'):
                                continue
                            
                            # 生成摘要（前500字符）
                            summary = content[:500] + "..." if len(content) > 500 else content
                            
                            # 提取链接
                            links = []
                            if 'links' in article_data:
                                links = [link.get('title', '') for link in article_data['links']]
                            
                            # 创建Document对象
                            doc = Document(
                                page_content=content,
                                metadata={
                                    'title': title,
                                    'summary': summary,
                                    'url': f"https://zh.wikipedia.org/wiki/{title.replace(' ', '_')}",
                                    'categories': json.dumps([]),  # 简化处理
                                    'links': json.dumps(links),
                                    'article_id': article_data.get('id'),
                                    'source': f"wikipedia_{title}"
                                }
                            )
                            
                            # 分割文档
                            splits = text_splitter.split_documents([doc])
                            documents.extend(splits)
                            
                            processed_count += 1
                            
                            if processed_count % 1000 == 0:
                                logger.info(f"已处理 {processed_count} 篇文章")
                                
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.warning(f"处理文章时出错: {str(e)}")
                            continue
            
            # 批量添加到向量数据库
            if documents:
                logger.info(f"开始添加 {len(documents)} 个文档块到向量数据库...")
                self.vectorstore.add_documents(documents)
                logger.info(f"成功添加 {len(documents)} 个文档块到向量数据库")
            
            logger.info(f"文章处理完成，共处理 {processed_count} 篇文章")
            return True
            
        except Exception as e:
            logger.error(f"处理提取的文章失败: {str(e)}")
            return False
    
    def search_articles(self, query: str, limit: int = 10) -> List[WikiArticle]:
        """
        搜索文章
        """
        if self.mode == "offline" and self._check_offline_available():
            return self._search_offline(query, limit)
        else:
            # 如果离线模式不可用，回退到在线模式
            if self.mode == "offline":
                logger.warning("离线模式不可用，回退到在线模式")
            return self._search_online(query, limit)
    
    def _search_offline(self, query: str, limit: int = 10) -> List[WikiArticle]:
        """
        离线搜索文章（使用向量数据库）
        """
        try:
            # 使用向量数据库搜索
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": limit}
            )
            
            docs = retriever.get_relevant_documents(query)
            
            articles = []
            for doc in docs:
                metadata = doc.metadata
                article = WikiArticle(
                    title=metadata.get('title', ''),
                    content=doc.page_content,
                    summary=metadata.get('summary', ''),
                    categories=json.loads(metadata.get('categories', '[]')),  # 添加categories参数
                    links=json.loads(metadata.get('links', '[]')),
                    url=metadata.get('url', ''),
                    article_id=metadata.get('article_id')
                )
                articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"离线搜索文章失败: {str(e)}")
            return []
    
    def _search_online(self, query: str, limit: int = 10) -> List[WikiArticle]:
        """
        在线搜索文章
        """
        try:
            # 使用维基百科搜索API
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': limit,
                'srnamespace': 0,  # 只搜索主命名空间
                'srprop': 'snippet|title|timestamp'
            }
            
            response = self.session.get(self.search_api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages = []
            
            for item in data['query']['search']:
                page = self._get_page_content(item['title'])
                if page:
                    page.score = self._calculate_relevance_score(query, page)
                    pages.append(page)
            
            # 按相关性排序
            pages.sort(key=lambda x: x.score, reverse=True)
            return pages
            
        except Exception as e:
            logger.error(f"在线搜索文章失败: {str(e)}")
            return []
    
    def _get_page_content(self, title: str) -> Optional[WikiArticle]:
        """
        获取页面内容（在线模式）
        """
        try:
            # 获取页面摘要
            summary_url = f"{self.wikipedia_api_url}/page/summary/{quote(title)}"
            summary_response = self.session.get(summary_url)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # 获取完整内容
            content_url = f"{self.wikipedia_api_url}/page/html/{quote(title)}"
            content_response = self.session.get(content_url)
            content_response.raise_for_status()
            
            # 获取分类信息
            categories = self._get_page_categories(title)
            
            return WikiArticle(
                title=title,
                content=content_response.text,
                url=summary_data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                summary=summary_data.get('extract', ''),
                categories=categories,
                links=[]
            )
            
        except Exception as e:
            logger.error(f"获取页面内容失败 {title}: {str(e)}")
            return None
    
    def _get_page_categories(self, title: str) -> List[str]:
        """
        获取页面分类（在线模式）
        """
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'titles': title,
                'prop': 'categories',
                'cllimit': 20
            }
            
            response = self.session.get(self.search_api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]
            
            if 'categories' in pages[page_id]:
                return [cat['title'].replace('Category:', '') for cat in pages[page_id]['categories']]
            
            return []
            
        except Exception as e:
            logger.error(f"获取页面分类失败: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, query: str, page: WikiArticle) -> float:
        """
        计算相关性分数
        """
        score = 0.0
        
        # 标题匹配
        if query.lower() in page.title.lower():
            score += 10.0
        
        # 摘要匹配
        query_words = query.lower().split()
        for word in query_words:
            if word in page.summary.lower():
                score += 2.0
        
        # 分类匹配
        for category in page.categories:
            if any(word in category.lower() for word in query_words):
                score += 1.0
        
        return score
    
    def get_article_by_title(self, title: str) -> Optional[WikiArticle]:
        """
        根据标题获取文章
        """
        if self.mode == "offline" and self._check_offline_available():
            return self._get_article_by_title_offline(title)
        else:
            # 如果离线模式不可用，回退到在线模式
            if self.mode == "offline":
                logger.warning("离线模式不可用，回退到在线模式")
            return self._get_page_content(title)
    
    def _get_article_by_title_offline(self, title: str) -> Optional[WikiArticle]:
        """
        根据标题获取文章（离线模式）
        """
        try:
            # 使用向量数据库搜索标题
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 1}
            )
            
            # 构建搜索查询
            search_query = f"title:{title}"
            docs = retriever.get_relevant_documents(search_query)
            
            if docs:
                doc = docs[0]
                metadata = doc.metadata
                return WikiArticle(
                    title=metadata.get('title', ''),
                    content=doc.page_content,
                    summary=metadata.get('summary', ''),
                    categories=json.loads(metadata.get('categories', '[]')),  # 添加categories参数
                    links=json.loads(metadata.get('links', '[]')),
                    url=metadata.get('url', ''),
                    article_id=metadata.get('article_id')
                )
            
            return None
            
        except Exception as e:
            logger.error(f"获取文章失败: {str(e)}")
            return None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        """
        if self.mode == "online":
            return {
                "service_type": "online",
                "stats": {
                    "total_articles": "N/A",
                    "database_size_mb": "N/A"
                }
            }
        
        try:
            # 检查离线模式是否可用
            if not self._check_offline_available():
                return {
                    "service_type": "offline_unavailable",
                    "stats": {
                        "total_articles": 0,
                        "database_size_mb": 0,
                        "message": "离线数据不可用，需要初始化"
                    }
                }
            
            # 获取向量数据库统计信息
            collection = self.vectorstore._collection
            count = collection.count()
            
            # 计算数据库大小
            db_size = sum(f.stat().st_size for f in self.vector_db_path.rglob('*') if f.is_file()) / (1024 * 1024)
            
            return {
                "service_type": "offline",
                "stats": {
                    'total_articles': count,
                    'avg_article_length': 1000,  # 估算值
                    'database_size_mb': round(db_size, 2),
                    'index_size_mb': round(db_size, 2)  # Chroma包含索引
                }
            }
            
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {str(e)}")
            return {
                "service_type": "offline_error",
                "stats": {
                    'total_articles': 0,
                    'avg_article_length': 0,
                    'database_size_mb': 0,
                    'index_size_mb': 0,
                    'error': str(e)
                }
            }

class WikiKnowledgeBase:
    """Wiki知识库集成"""
    
    def __init__(self, wiki_service: WikiService):
        self.wiki_service = wiki_service
        self.cache = {}  # 简单的内存缓存
        self.cache_ttl = 3600  # 1小时缓存
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索Wiki知识
        """
        cache_key = f"{query}_{limit}"
        
        # 检查缓存
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cache_data
        
        # 搜索Wiki
        pages = self.wiki_service.search_articles(query, limit)
        
        # 转换为标准格式
        results = []
        for page in pages:
            results.append({
                'title': page.title,
                'content': page.summary,  # 使用摘要作为主要内容
                'full_content': page.content,
                'url': page.url,
                'categories': page.categories,
                'score': getattr(page, 'score', 1.0),
                'source': 'wikipedia_online' if self.wiki_service.mode == "online" else 'wikipedia_offline'
            })
        
        # 缓存结果
        self.cache[cache_key] = (time.time(), results)
        
        return results
    
    def get_enhanced_context(self, query: str, existing_context: str = "") -> str:
        """
        获取增强的上下文信息
        """
        wiki_results = self.search_knowledge(query, limit=3)
        
        if not wiki_results:
            return existing_context
        
        mode_text = "在线维基百科" if self.wiki_service.mode == "online" else "离线维基百科"
        enhanced_context = existing_context + "\n\n" if existing_context else ""
        enhanced_context += f"=== {mode_text}补充信息 ===\n"
        
        for i, result in enumerate(wiki_results, 1):
            enhanced_context += f"\n{i}. {result['title']}\n"
            enhanced_context += f"   摘要: {result['content'][:200]}...\n"
            enhanced_context += f"   来源: {result['url']}\n"
        
        return enhanced_context 