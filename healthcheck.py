#!/usr/bin/env python3
"""
JCR MCP服务器健康检查脚本
用于Docker健康检查和监控
"""
import sys
import sqlite3
from pathlib import Path


def check_database():
    """检查数据库是否可访问"""
    try:
        # 获取数据库路径
        db_path = Path.home() / ".jcr_mcp" / "jcr.db"
        
        if not db_path.exists():
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        # 尝试连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print(f"✅ 数据库健康检查通过 (包含数据表)")
            return True
        else:
            # 数据库存在但无表，可能是首次启动未同步数据
            print(f"⚠️ 数据库无数据表 (可能需要运行 jcr-mcp-sync)")
            # 仍然返回True，因为数据库本身可访问
            return True
            
    except Exception as e:
        print(f"❌ 数据库健康检查失败: {e}")
        return False


def main():
    """主函数"""
    print("🏥 JCR MCP服务器健康检查")
    
    # 检查数据库
    db_ok = check_database()
    
    if db_ok:
        print("\n✅ 服务器健康")
        sys.exit(0)
    else:
        print("\n❌ 服务器异常")
        sys.exit(1)


if __name__ == "__main__":
    main()
