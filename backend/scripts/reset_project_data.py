#!/usr/bin/env python3
"""
重置项目数据脚本
清理ChromaDB知识库和数据库中的所有数据
"""

import os
import sys
import json
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base
from app.services.database_service import DatabaseService

def reset_project_data():
    """重置项目数据"""
    
    print("🧹 开始重置项目数据...")
    
    # 1. 清理ChromaDB目录
    print("\n1. 清理ChromaDB目录")
    chroma_db_path = "./chroma_db"
    if os.path.exists(chroma_db_path):
        try:
            shutil.rmtree(chroma_db_path)
            print(f"✅ 已删除ChromaDB目录: {chroma_db_path}")
        except Exception as e:
            print(f"❌ 删除ChromaDB目录失败: {e}")
    else:
        print(f"✅ ChromaDB目录不存在: {chroma_db_path}")
    
    # 2. 清理上传文件目录
    print("\n2. 清理上传文件目录")
    uploaded_files_path = "./uploaded_files"
    if os.path.exists(uploaded_files_path):
        try:
            shutil.rmtree(uploaded_files_path)
            print(f"✅ 已删除上传文件目录: {uploaded_files_path}")
        except Exception as e:
            print(f"❌ 删除上传文件目录失败: {e}")
    else:
        print(f"✅ 上传文件目录不存在: {uploaded_files_path}")
    
    # 3. 重置数据库
    print("\n3. 重置数据库")
    try:
        # 删除所有表
        print("   删除所有表...")
        Base.metadata.drop_all(bind=engine)
        print("   ✅ 已删除所有表")
        
        # 重新创建所有表
        print("   重新创建所有表...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ 已重新创建所有表")
        
    except Exception as e:
        print(f"   ❌ 重置数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 验证重置结果
    print("\n4. 验证重置结果")
    db = SessionLocal()
    try:
        # 直接查询数据库表
        from sqlalchemy import text
        
        # 检查各表的记录数量
        tables = ['users', 'knowledge_bases', 'knowledge_files', 'conversations', 'messages', 'user_api_keys']
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   {table} 表记录数量: {count}")
            except Exception as e:
                print(f"   {table} 表查询失败: {e}")
        
        print("   ✅ 数据库重置验证完成")
        
    except Exception as e:
        print(f"   ❌ 验证重置结果失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    # 5. 检查目录状态
    print("\n5. 检查目录状态")
    print(f"   ChromaDB目录: {'存在' if os.path.exists(chroma_db_path) else '不存在'}")
    print(f"   上传文件目录: {'存在' if os.path.exists(uploaded_files_path) else '不存在'}")
    
    print("\n✅ 项目数据重置完成！")
    print("\n📝 重置内容:")
    print("   - 删除了所有ChromaDB向量数据")
    print("   - 删除了所有上传的文件")
    print("   - 清空了所有数据库表")
    print("   - 重新创建了数据库表结构")
    print("\n🚀 现在可以重新开始使用项目了！")

if __name__ == "__main__":
    # 确认操作
    print("⚠️  警告：此操作将删除所有项目数据！")
    print("   包括：")
    print("   - 所有ChromaDB向量数据")
    print("   - 所有上传的文件")
    print("   - 所有数据库记录")
    print("   - 所有用户、知识库、对话等数据")
    print()
    
    confirm = input("确认要重置所有数据吗？(输入 'yes' 确认): ")
    if confirm.lower() == 'yes':
        reset_project_data()
    else:
        print("❌ 操作已取消") 