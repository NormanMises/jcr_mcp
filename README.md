# JCR分区表MCP服务器

基于ShowJCR仓库数据的Model Context Protocol (MCP) 服务器，为大语言模型提供最新的期刊分区表查询功能。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 💡 **新版本**: 现已支持通过 `uvx` 一键部署！无需手动安装依赖，开箱即用。
>
> 🚀 **快速开始**: 查看 [QUICKSTART.md](QUICKSTART.md) 快速部署指南
>
> 📖 **升级指南**: 如果你是从旧版本升级，请查看 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
>
> 🌐 **托管部署**: 支持作为远程服务部署，详见 [DEPLOYMENT.md](DEPLOYMENT.md)

## 功能特性

### 🔧 工具 (Tools)
- **search_journal** - 搜索期刊信息，包括影响因子、分区、预警状态等
- **get_partition_trends** - 获取期刊分区变化趋势分析
- **check_warning_journals** - 查询国际期刊预警名单
- **compare_journals** - 对比多个期刊的综合信息

### 📋 资源 (Resources)
- **jcr://database-info** - 数据库基本信息和统计
- **jcr://health** - 健康检查端点（用于监控）

### 💡 提示词 (Prompts)
- **journal_analysis_prompt** - 期刊分析专用提示词模板

## 数据来源

本项目基于 [ShowJCR](https://github.com/hitfyd/ShowJCR) 仓库的数据，包括：

- **中科院分区表升级版** (2025、2023、2022年)
- **JCR期刊影响因子** (2024、2023、2022年)
- **国际期刊预警名单** (2025、2024、2023、2021、2020年)
- **CCF推荐国际学术期刊目录** (2022年)
- **计算领域高质量科技期刊分级目录** (2022年)

## 安装部署

### 方法一：使用 uvx 部署（推荐）

`uvx` 是一个快速、可靠的 Python 应用运行工具，无需手动安装依赖。

#### 1. 首次使用需要同步数据
```bash
uvx --from jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git jcr-mcp-sync
```

选择"1"同步所有数据，等待下载和导入完成。

#### 2. 启动服务器
```bash
uvx jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git
```

或者直接使用包名（如果已发布到 PyPI）：
```bash
uvx jcr-mcp-server
```

#### 3. 在 Claude Desktop 中配置
编辑 Claude Desktop 配置文件，添加：
```json
{
  "mcpServers": {
    "jcr-partition": {
      "command": "uvx",
      "args": ["jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git"],
      "env": {}
    }
  }
}
```

### 方法二：从源码安装

#### 1. 克隆仓库
```bash
git clone https://github.com/NormanMises/jcr_mcp.git
cd jcr_mcp
```

#### 2. 安装包
```bash
pip install -e .
```

#### 3. 数据同步
```bash
jcr-mcp-sync
```

选择"1"同步所有数据，等待下载和导入完成。

#### 4. 启动服务器
```bash
jcr-mcp-server
```

### 方法三：传统方式（兼容旧版本）

#### 1. 环境要求
- Python 3.8+
- SQLite3

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 数据同步
```bash
python data_sync.py
```

#### 4. 启动服务器
```bash
python jcr_mcp_server.py
```

## 快速测试

安装后，可以快速验证安装是否成功：

### 1. 测试服务器启动
```bash
# 使用 uvx
uvx jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git

# 或使用已安装的命令
jcr-mcp-server

# 或使用 python -m
python -m jcr_mcp
```

看到启动信息即表示安装成功，按 `Ctrl+C` 停止服务器。

### 2. 测试数据同步
```bash
# 使用已安装的命令
jcr-mcp-sync

# 选择"4"退出测试界面
```

## 客户端测试

### 独立测试
```bash
python test_client.py
```

选择模式：
- 模式1：自动测试所有功能
- 模式2：交互式查询模式

### Claude Desktop集成

#### 使用 uvx（推荐）
在Claude Desktop配置文件中添加：
```json
{
  "mcpServers": {
    "jcr-partition": {
      "command": "uvx",
      "args": ["jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git"],
      "env": {}
    }
  }
}
```

#### 使用已安装的包
```json
{
  "mcpServers": {
    "jcr-partition": {
      "command": "jcr-mcp-server",
      "args": [],
      "env": {}
    }
  }
}
```

#### 使用 Python 脚本（传统方式）
```json
{
  "mcpServers": {
    "jcr-partition": {
      "command": "python",
      "args": ["path/to/jcr_mcp_server.py"],
      "cwd": "path/to/project"
    }
  }
}
```

## 使用示例

### 1. 期刊搜索
```python
# 搜索Nature期刊
result = await session.call_tool("search_journal", {
    "journal_name": "Nature"
})
```

### 2. 分区趋势分析
```python
# 获取Science期刊分区变化趋势
result = await session.call_tool("get_partition_trends", {
    "journal_name": "Science"
})
```

### 3. 期刊对比
```python
# 对比三个顶级期刊
result = await session.call_tool("compare_journals", {
    "journal_list": "Nature,Science,Cell"
})
```

### 4. 预警期刊查询
```python
# 查询预警期刊
result = await session.call_tool("check_warning_journals", {
    "keywords": "MDPI"
})
```

## 输出示例

### 期刊搜索结果
```
📚 期刊名称: NATURE

【2024年】
  📊 影响因子: 64.8
  🏆 分区: Q1
  📖 学科类别: Multidisciplinary Sciences

【2025年】
  🏆 分区: 1区
  📖 学科类别: 综合性期刊
```

### 期刊对比结果
```
📊 期刊对比分析结果

期刊名称                    最新影响因子      最新分区        预警状态       
----------------------------------------
Nature                    64.8           Q1             正常          
Science                   56.9           Q1             正常          
Cell                      64.5           Q1             正常          

💡 投稿建议:
  ⭐ Nature: 顶级期刊，强烈推荐
  ⭐ Science: 顶级期刊，强烈推荐  
  ⭐ Cell: 顶级期刊，强烈推荐
```

## 技术架构

### 数据层
- SQLite数据库存储所有分区表数据
- 支持多个年份的历史数据
- 自动数据同步和验证机制
- 数据存储在用户目录 `~/.jcr_mcp/` 下，确保持久性

### 服务层  
- FastMCP框架构建MCP服务器
- 异步处理提高性能
- 完善的错误处理和日志记录
- 支持多种运行方式（uvx、pip install、直接运行）

### 接口层
- 标准MCP协议接口
- 支持工具、资源、提示词三种类型
- 兼容各种MCP客户端

## 扩展说明

### 添加新数据源
1. 在`data_sync.py`中的`data_sources`字典添加新数据源
2. 运行数据同步更新数据库
3. 在`jcr_mcp_server.py`中更新解析逻辑

### 添加新工具
1. 在`jcr_mcp_server.py`中使用`@app.tool()`装饰器
2. 实现具体的查询逻辑
3. 添加合适的文档字符串

### 数据存储位置

使用 uvx 或已安装的包运行时，数据库会自动存储在用户主目录下：
- Linux/Mac: `~/.jcr_mcp/jcr.db`
- Windows: `%USERPROFILE%\.jcr_mcp\jcr.db`

这样可以确保数据在不同运行环境下都能保持一致，且不会被意外删除。

## 托管部署（远程服务）

本项目支持作为远程服务部署，可以通过 HTTP/SSE 协议访问。详细部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)。

### 快速开始

#### Docker 部署（推荐）
```bash
# 克隆仓库
git clone https://github.com/NormanMises/jcr_mcp.git
cd jcr_mcp

# 使用 Docker Compose 启动
docker-compose up -d

# 服务将在 http://localhost:8080 运行
```

#### 直接部署
```bash
# 安装并同步数据
pip install -e .
jcr-mcp-sync

# 启动 SSE 服务器
jcr-mcp-server sse

# 或使用环境变量配置
JCR_MCP_HOST=0.0.0.0 JCR_MCP_PORT=8080 jcr-mcp-server sse
```

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `JCR_MCP_TRANSPORT` | 传输协议：stdio/sse/streamable-http | `stdio` |
| `JCR_MCP_HOST` | 监听地址 | `0.0.0.0` |
| `JCR_MCP_PORT` | 监听端口 | `8080` |

### 支持的部署平台

- ✅ Docker / Docker Compose
- ✅ Railway
- ✅ Fly.io
- ✅ Heroku
- ✅ 阿里云/腾讯云/AWS ECS
- ✅ 任何支持 Python 的云平台

### 客户端连接

远程服务可通过 HTTP/SSE 协议连接：

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://your-server:8080") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("search_journal", {
            "journal_name": "Nature"
        })
```

完整的部署指南、云平台配置、监控维护等信息，请查看 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 相关链接

- [ShowJCR原项目](https://github.com/hitfyd/ShowJCR)
- [MCP官方文档](https://modelcontextprotocol.io/)
- [Claude Desktop MCP集成指南](https://claude.ai/docs/mcp)

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！ 