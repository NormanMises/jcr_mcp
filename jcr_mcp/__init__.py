"""
JCR分区表MCP服务器

基于ShowJCR仓库数据的Model Context Protocol (MCP) 服务器，
为大语言模型提供最新的期刊分区表查询功能。
"""

__version__ = "0.1.0"
__author__ = "JCR MCP Contributors"
__license__ = "MIT"

from .database import JCRDatabase, JournalInfo

__all__ = ["JCRDatabase", "JournalInfo", "__version__"]
