#!/usr/bin/env python3
"""
创建数据库表的脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_tables():
    """创建数据库表"""
    try:
        from app.database import engine
        from app.models import Base
        
        print("🔍 创建数据库表...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables() 