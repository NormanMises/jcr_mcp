"""
JCR分区表MCP服务器主模块
"""
import os
import sqlite3
from typing import Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .database import JCRDatabase


# 从环境变量获取配置
DEFAULT_HOST = os.getenv("JCR_MCP_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("JCR_MCP_PORT", "8080"))
DEFAULT_TRANSPORT = os.getenv("JCR_MCP_TRANSPORT", "stdio")

# 初始化FastMCP服务器
app = FastMCP("jcr-partition-server", port=DEFAULT_PORT)

# 全局数据库实例
db = None


def get_db() -> JCRDatabase:
    """获取数据库实例（延迟初始化）"""
    global db
    if db is None:
        db = JCRDatabase()
    return db


@app.tool()
async def search_journal(journal_name: str, year: Optional[str] = None) -> str:
    """
    搜索期刊信息，包括影响因子、分区、预警状态等
    
    Args:
        journal_name: 期刊名称（支持模糊搜索）
        year: 指定年份（可选，如2025、2024、2023等）
    
    Returns:
        期刊的详细信息，包括各年份的分区、影响因子等数据
    """
    try:
        database = get_db()
        results = database.search_journal(journal_name, year)
        
        if not results:
            return f"未找到期刊 '{journal_name}' 的相关信息"
        
        # 按期刊名称和年份分组整理结果
        grouped_results = {}
        for result in results:
            key = result.journal_name
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)
        
        output = []
        for journal, infos in grouped_results.items():
            output.append(f"\n📚 期刊名称: {journal}")
            output.append("=" * 50)
            
            # 按年份排序
            infos.sort(key=lambda x: x.year or "0000", reverse=True)
            
            for info in infos:
                year_str = f"【{info.year}年】" if info.year else "【未知年份】"
                output.append(f"\n{year_str}")
                
                if info.impact_factor:
                    output.append(f"  📊 影响因子: {info.impact_factor}")
                
                if info.partition:
                    output.append(f"  🏆 分区: {info.partition}")
                
                if info.category:
                    output.append(f"  📖 学科类别: {info.category}")
                
                if info.warning_status:
                    output.append(f"  ⚠️ 预警状态: {info.warning_status}")
                
                if info.ccf_level:
                    output.append(f"  🏅 CCF推荐等级: {info.ccf_level}")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"查询出错: {str(e)}"


@app.tool()
async def get_partition_trends(journal_name: str) -> str:
    """
    获取期刊分区变化趋势
    
    Args:
        journal_name: 期刊名称
    
    Returns:
        期刊历年分区变化趋势分析
    """
    try:
        database = get_db()
        results = database.search_journal(journal_name)
        
        if not results:
            return f"未找到期刊 '{journal_name}' 的相关信息"
        
        # 提取分区信息
        partition_data = []
        for result in results:
            if result.partition and result.year:
                partition_data.append((result.year, result.partition, result.journal_name))
        
        if not partition_data:
            return f"未找到期刊 '{journal_name}' 的分区信息"
        
        # 按年份排序
        partition_data.sort(key=lambda x: x[0])
        
        output = [f"📈 期刊分区变化趋势分析"]
        output.append("=" * 40)
        
        for year, partition, journal in partition_data:
            output.append(f"{year}年: {partition}")
        
        # 简单趋势分析
        if len(partition_data) > 1:
            output.append("\n📊 趋势分析:")
            first_partition = partition_data[0][1]
            last_partition = partition_data[-1][1]
            
            if "1区" in last_partition or "Q1" in last_partition:
                output.append("✅ 该期刊保持在顶级分区")
            elif "4区" in last_partition or "Q4" in last_partition:
                output.append("⚠️ 该期刊分区较低，发表需谨慎")
            else:
                output.append("📊 该期刊分区稳定，属于中等水平")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"分析出错: {str(e)}"


@app.tool()
async def check_warning_journals(keywords: Optional[str] = None) -> str:
    """
    查询国际期刊预警名单
    
    Args:
        keywords: 关键词（可选，用于筛选特定期刊）
    
    Returns:
        预警期刊列表及其预警原因
    """
    try:
        database = get_db()
        conn = sqlite3.connect(database.db_path)
        cursor = conn.cursor()
        
        # 获取预警表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'GJQKYJMD%'")
        warning_tables = [table[0] for table in cursor.fetchall()]
        
        if not warning_tables:
            return "未找到预警期刊数据表"
        
        output = ["🚨 国际期刊预警名单查询结果"]
        output.append("=" * 40)
        
        for table in sorted(warning_tables, reverse=True):
            year = table.replace('GJQKYJMD', '')
            output.append(f"\n📅 {year}年预警名单:")
            
            query = f"SELECT * FROM {table}"
            params = []
            
            if keywords:
                query += " WHERE Journal LIKE ? COLLATE NOCASE"
                params.append(f"%{keywords}%")
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            
            if rows:
                for row in rows:
                    row_dict = dict(zip(column_names, row))
                    journal_name = row_dict.get('Journal', '未知期刊')
                    warning_reason = row_dict.get('预警原因', row_dict.get('预警等级', '未知原因'))
                    output.append(f"  • {journal_name}: {warning_reason}")
            else:
                if keywords:
                    output.append(f"  无匹配 '{keywords}' 的预警期刊")
                else:
                    output.append("  该年度无预警期刊数据")
        
        conn.close()
        return "\n".join(output)
    
    except Exception as e:
        return f"查询预警期刊出错: {str(e)}"


@app.tool()
async def compare_journals(journal_list: str) -> str:
    """
    比较多个期刊的综合信息
    
    Args:
        journal_list: 期刊名称列表，用逗号分隔，如"Nature,Science,Cell"
    
    Returns:
        多个期刊的对比分析结果
    """
    try:
        journals = [j.strip() for j in journal_list.split(',')]
        
        if len(journals) < 2:
            return "请至少提供2个期刊名称进行比较"
        
        output = ["📊 期刊对比分析结果"]
        output.append("=" * 50)
        
        database = get_db()
        all_results = {}
        for journal in journals:
            results = database.search_journal(journal)
            all_results[journal] = results
        
        # 生成对比表格
        output.append(f"\n{'期刊名称':<30} {'最新影响因子':<15} {'最新分区':<15} {'预警状态':<15}")
        output.append("-" * 80)
        
        for journal, results in all_results.items():
            if not results:
                output.append(f"{journal:<30} {'无数据':<15} {'无数据':<15} {'无数据':<15}")
                continue
            
            # 获取最新数据
            latest_if = "无数据"
            latest_partition = "无数据"
            warning_status = "正常"
            
            for result in results:
                if result.impact_factor:
                    latest_if = str(result.impact_factor)
                if result.partition:
                    latest_partition = result.partition
                if result.warning_status:
                    warning_status = "⚠️预警"
                    break
            
            output.append(f"{journal:<30} {latest_if:<15} {latest_partition:<15} {warning_status:<15}")
        
        # 推荐建议
        output.append("\n💡 投稿建议:")
        for journal, results in all_results.items():
            if results:
                has_warning = any(r.warning_status for r in results)
                if has_warning:
                    output.append(f"  ❌ {journal}: 该期刊在预警名单中，不建议投稿")
                else:
                    latest_partition = None
                    for result in results:
                        if result.partition:
                            latest_partition = result.partition
                            break
                    
                    if latest_partition and ("1区" in latest_partition or "Q1" in latest_partition):
                        output.append(f"  ⭐ {journal}: 顶级期刊，强烈推荐")
                    elif latest_partition and ("2区" in latest_partition or "Q2" in latest_partition):
                        output.append(f"  ✅ {journal}: 优质期刊，推荐投稿")
                    else:
                        output.append(f"  📝 {journal}: 可考虑投稿")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"比较分析出错: {str(e)}"


@app.resource("jcr://database-info")
async def get_database_info() -> str:
    """获取数据库基本信息"""
    try:
        database = get_db()
        conn = sqlite3.connect(database.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        info = ["📊 JCR分区表数据库信息"]
        info.append("=" * 30)
        info.append(f"数据库路径: {database.db_path}")
        info.append(f"数据表数量: {len(tables)}")
        info.append("\n📋 可用数据表:")
        
        for table in sorted(tables):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            info.append(f"  • {table}: {count} 条记录")
        
        conn.close()
        return "\n".join(info)
    
    except Exception as e:
        return f"获取数据库信息出错: {str(e)}"


@app.prompt()
async def journal_analysis_prompt(journal_name: str) -> str:
    """期刊分析专用提示词模板"""
    return f"""
你是一个专业的学术期刊分析专家。请基于提供的期刊数据，对期刊 {journal_name} 进行全面分析，包括：

1. 期刊基本信息分析
2. 影响因子变化趋势
3. 分区变化情况
4. 预警状态评估
5. 投稿建议

请用专业、客观的语言进行分析，并给出具体的投稿建议。
"""


@app.resource("jcr://health")
async def health_check() -> str:
    """健康检查端点"""
    try:
        database = get_db()
        # 简单检查数据库是否可访问，使用 context manager
        with sqlite3.connect(database.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            cursor.fetchone()
        
        return "OK"
    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    """主函数 - 作为命令行入口点"""
    import sys
    
    # 初始化数据库
    database = get_db()
    
    # 从命令行参数或环境变量获取传输方式
    transport = DEFAULT_TRANSPORT
    if len(sys.argv) > 1 and sys.argv[1] in ["stdio", "sse", "streamable-http"]:
        transport = sys.argv[1]
    
    print("🚀 启动JCR分区表MCP服务器...")
    print(f"📊 数据库路径: {database.db_path}")
    print(f"🌐 传输方式: {transport}")
    
    if transport in ["sse", "streamable-http"]:
        print(f"🔌 监听地址: {DEFAULT_HOST}:{DEFAULT_PORT}")
        print(f"📍 访问地址: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    
    print("🔧 可用工具:")
    print("  • search_journal - 搜索期刊信息")
    print("  • get_partition_trends - 获取分区趋势")
    print("  • check_warning_journals - 查询预警期刊")
    print("  • compare_journals - 对比期刊")
    print("💡 提示词模板: journal_analysis_prompt")
    print("📋 资源: jcr://database-info")
    print("\n⚡ 服务器启动中...")
    
    # 运行MCP服务器
    app.run(transport=transport)


if __name__ == "__main__":
    main()
