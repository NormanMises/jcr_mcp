"""
配置模块 - 提供共享的配置和工具函数
"""
from pathlib import Path


def get_data_dir() -> Path:
    """
    获取数据目录路径
    
    Returns:
        数据目录的 Path 对象
    """
    data_dir = Path.home() / ".jcr_mcp"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_database_path() -> str:
    """
    获取数据库文件路径
    
    Returns:
        数据库文件的完整路径字符串
    """
    return str(get_data_dir() / "jcr.db")
