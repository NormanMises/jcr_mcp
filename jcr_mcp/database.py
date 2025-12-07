"""
JCR数据库管理模块
"""
import sqlite3
import os
from typing import Optional, Dict, List
from dataclasses import dataclass

from .config import get_database_path


@dataclass
class JournalInfo:
    """期刊信息数据类"""
    journal_name: str
    impact_factor: Optional[float] = None
    partition: Optional[str] = None
    category: Optional[str] = None
    warning_status: Optional[str] = None
    ccf_level: Optional[str] = None
    year: Optional[str] = None


class JCRDatabase:
    """JCR数据库管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            db_path = get_database_path()
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        if not os.path.exists(self.db_path):
            # 如果数据库不存在，创建基本表结构
            conn = sqlite3.connect(self.db_path)
            conn.close()
    
    def search_journal(self, journal_name: str, year: Optional[str] = None) -> List[JournalInfo]:
        """搜索期刊信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        try:
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            
            # 在各个表中搜索期刊
            for table in tables:
                try:
                    # 检查表结构
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if 'Journal' not in columns:
                        continue
                    
                    # 构建查询语句
                    query = f"SELECT * FROM {table} WHERE Journal LIKE ? COLLATE NOCASE"
                    cursor.execute(query, (f"%{journal_name}%",))
                    
                    rows = cursor.fetchall()
                    column_names = [description[0] for description in cursor.description]
                    
                    for row in rows:
                        row_dict = dict(zip(column_names, row))
                        journal_info = self._parse_journal_info(row_dict, table)
                        if journal_info:
                            results.append(journal_info)
                
                except sqlite3.Error:
                    continue
        
        finally:
            conn.close()
        
        return results
    
    def _parse_journal_info(self, row_dict: Dict, table_name: str) -> Optional[JournalInfo]:
        """解析数据库行为期刊信息对象"""
        try:
            journal_name = row_dict.get('Journal', '')
            
            # 根据表名判断数据类型和年份
            impact_factor = None
            partition = None
            category = None
            warning_status = None
            ccf_level = None
            year = None
            
            # 解析年份
            if 'JCR' in table_name:
                year = table_name.replace('JCR', '')
                impact_factor = row_dict.get('IF', row_dict.get('Impact Factor'))
                partition = row_dict.get('Quartile', row_dict.get('分区'))
                category = row_dict.get('Category', row_dict.get('类别'))
            
            elif 'FQBJCR' in table_name:
                year = table_name.replace('FQBJCR', '')
                partition = row_dict.get('大类分区', row_dict.get('Partition'))
                category = row_dict.get('学科', row_dict.get('Subject'))
            
            elif 'GJQKYJMD' in table_name:
                year = table_name.replace('GJQKYJMD', '')
                warning_status = row_dict.get('预警等级', row_dict.get('Warning Level'))
            
            elif 'CCF' in table_name:
                year = table_name.replace('CCF', '')
                ccf_level = row_dict.get('CCF推荐类型', row_dict.get('CCF Level'))
                category = row_dict.get('领域', row_dict.get('Field'))
            
            return JournalInfo(
                journal_name=journal_name,
                impact_factor=impact_factor,
                partition=partition,
                category=category,
                warning_status=warning_status,
                ccf_level=ccf_level,
                year=year
            )
        
        except Exception:
            return None
