#!/usr/bin/env python3
"""
Wiki数据初始化脚本
从JSONL文件初始化wiki数据库
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any
import argparse
from tqdm import tqdm

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.wiki_service import WikiService
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class WikiDataInitializer:
    def __init__(self):
        self.wiki_service = WikiService(mode="offline")
        self.vector_db_path = "wiki_data/wiki_vectors"
        
    def init_with_jsonl_data(self, jsonl_path: str):
        """从JSONL文件初始化Wiki数据"""
        logger.info(f"🚀 开始Wiki数据初始化...")
        logger.info(f"📁 数据源: {jsonl_path}")
        
        # 检查文件是否存在
        if not os.path.exists(jsonl_path):
            logger.error(f"❌ JSONL文件不存在: {jsonl_path}")
            return
            
        # 读取文章
        articles = self._read_jsonl_articles(jsonl_path)
        if not articles:
            logger.error("❌ 没有读取到有效的文章数据")
            return
            
        # 处理文章
        self._process_articles(articles)
        
        logger.info("🎉 Wiki数据初始化完成！")
        
    def _read_jsonl_articles(self, jsonl_path: str) -> List[Dict[str, Any]]:
        """从JSONL文件读取文章"""
        try:
            articles = []
            line_num = 0
            
            # 首先计算总行数
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                total_lines = sum(1 for _ in f)
            
            logger.info(f"📊 开始读取JSONL文件: {jsonl_path}")
            logger.info(f"📈 文件总行数: {total_lines}")
            
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                # 使用tqdm创建进度条
                for line in tqdm(f, total=total_lines, desc="📖 读取JSONL文件", unit="行"):
                    line_num += 1
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        item = json.loads(line)
                        if "title" in item and "contents" in item:
                            title_clean = item["title"].strip('"').replace(' ', '_')
                            articles.append({
                                "title": item["title"].strip('"'),  # 移除引号
                                "content": item["contents"],
                                "summary": item["contents"][:500] + "..." if len(item["contents"]) > 500 else item["contents"],
                                "url": f"https://zh.wikipedia.org/wiki/{title_clean}",
                                "categories": [],
                                "links": []
                            })
                            
                        if line_num % 5000 == 0:
                            logger.info(f"📊 已读取 {line_num}/{total_lines} 行，提取了 {len(articles)} 篇文章")
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ 第 {line_num} 行JSON解析失败: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"⚠️ 处理第 {line_num} 行时出错: {e}")
                        continue
                        
            logger.info(f"✅ 从JSONL文件读取了 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"❌ 读取JSONL文件时出错: {e}")
            return []
            
    def _process_articles(self, articles: List[Dict[str, Any]]):
        """处理文章并添加到向量数据库"""
        try:
            logger.info(f"🔧 开始处理 {len(articles)} 篇文章...")
            
            # 初始化向量数据库
            logger.info("🔗 初始化Chroma向量数据库...")
            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            vectorstore = Chroma(
                collection_name="wiki_articles",
                embedding_function=embeddings,
                persist_directory=self.vector_db_path
            )
            
            # 初始化文本分割器
            logger.info("✂️ 初始化文本分割器...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
            )
            
            # 批处理大小限制
            BATCH_SIZE = 5000  # 设置安全的批处理大小
            
            # 处理文章
            logger.info("📝 开始分割和向量化文章...")
            all_documents = []
            
            # 使用tqdm创建进度条处理文章
            for article in tqdm(articles, desc="📝 处理文章", unit="篇"):
                # 创建文档
                doc = Document(
                    page_content=article["content"],
                    metadata={
                        "title": article["title"],
                        "summary": article["summary"],
                        "url": article["url"],
                        "source": "zhwiki"
                    }
                )
                
                # 分割文档
                chunks = text_splitter.split_documents([doc])
                all_documents.extend(chunks)
            
            logger.info(f"✅ 文章处理完成，共生成 {len(all_documents)} 个文档块")
            
            # 分批添加到向量数据库
            logger.info(f"💾 开始分批添加到向量数据库 (批大小: {BATCH_SIZE})...")
            total_added = 0
            
            # 使用tqdm创建进度条添加文档
            for i in tqdm(range(0, len(all_documents), BATCH_SIZE), 
                         desc="💾 添加到向量数据库", 
                         unit="批"):
                batch = all_documents[i:i + BATCH_SIZE]
                vectorstore.add_documents(batch)
                total_added += len(batch)
                
                # 每5批显示一次详细进度
                if (i // BATCH_SIZE + 1) % 5 == 0:
                    logger.info(f"📊 已添加 {total_added}/{len(all_documents)} 个文档块 ({total_added/len(all_documents)*100:.1f}%)")
                
            logger.info(f"✅ 向量数据库初始化完成！共添加 {total_added} 个文档块")
                
        except Exception as e:
            logger.error(f"❌ 处理文章时出错: {e}")
            raise
            
    def get_stats(self):
        """获取数据库统计信息"""
        try:
            stats = self.wiki_service.get_database_stats()
            print(f"服务类型: {stats['mode']}")
            print(f"文章总数: {stats['total_articles']}")
            print(f"数据库大小: {stats['database_size']}")
            return stats
        except Exception as e:
            logger.error(f"获取统计信息时出错: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Wiki数据初始化工具")
    parser.add_argument("--jsonl-path", type=str, default="wiki_data/clean_corpus.jsonl",
                       help="JSONL文件路径")
    parser.add_argument("--stats", action="store_true",
                       help="显示数据库统计信息")
    
    args = parser.parse_args()
    
    initializer = WikiDataInitializer()
    
    if args.stats:
        initializer.get_stats()
        return
        
    # 从JSONL文件初始化
    initializer.init_with_jsonl_data(args.jsonl_path)
        
    print("✅ Wiki数据初始化完成！")
    print("现在可以运行测试了")

if __name__ == "__main__":
    main() 