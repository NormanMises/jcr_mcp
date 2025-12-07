# 快速开始指南 (Quick Start Guide)

本指南帮助你在5分钟内快速部署和使用JCR MCP服务器。

## 本地使用（Claude Desktop）

### 1. 使用 uvx（最简单）

```bash
# 同步数据（首次使用）
uvx --from jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git jcr-mcp-sync

# 配置 Claude Desktop
# 编辑配置文件，添加：
{
  "mcpServers": {
    "jcr-partition": {
      "command": "uvx",
      "args": ["jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git"]
    }
  }
}

# 重启 Claude Desktop
```

### 2. 使用 pip install

```bash
# 安装
pip install git+https://github.com/NormanMises/jcr_mcp.git

# 同步数据
jcr-mcp-sync

# 配置 Claude Desktop
{
  "mcpServers": {
    "jcr-partition": {
      "command": "jcr-mcp-server"
    }
  }
}
```

## 远程部署（托管服务）

### 使用 Docker（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/NormanMises/jcr_mcp.git
cd jcr_mcp

# 2. 启动服务
docker-compose up -d

# 3. 在容器内同步数据
docker exec -it jcr-mcp-server jcr-mcp-sync
# 选择 1 同步所有数据

# 4. 查看日志
docker-compose logs -f

# 5. 测试服务
curl http://localhost:8080
```

服务将在 `http://localhost:8080` 上运行。

### 直接部署

```bash
# 1. 安装
pip install git+https://github.com/NormanMises/jcr_mcp.git

# 2. 同步数据
jcr-mcp-sync

# 3. 启动SSE服务器
jcr-mcp-server sse

# 服务将在 http://0.0.0.0:8080 上运行
```

### 自定义配置

使用环境变量配置：

```bash
# 修改端口
JCR_MCP_PORT=9000 jcr-mcp-server sse

# 修改监听地址
JCR_MCP_HOST=127.0.0.1 jcr-mcp-server sse

# 使用 .env 文件
cp .env.example .env
# 编辑 .env 文件
jcr-mcp-server sse
```

## 验证安装

### 本地模式

```bash
# 启动服务器（按 Ctrl+C 停止）
jcr-mcp-server

# 运行测试客户端
python test_client.py
```

### 远程模式

```bash
# 启动SSE服务器
jcr-mcp-server sse &

# 健康检查
python healthcheck.py

# 如果有数据，应该看到：
# ✅ 数据库健康检查通过
```

## 使用示例

### 在 Claude Desktop 中使用

1. 配置好服务器后，重启 Claude Desktop
2. 在对话中询问：
   - "帮我查询Nature期刊的分区信息"
   - "对比Nature、Science和Cell三个期刊"
   - "查询MDPI相关的预警期刊"

### 通过 Python 客户端使用

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8080") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        result = await session.call_tool("search_journal", {
            "journal_name": "Nature"
        })
        print(result.content[0].text)
```

## 常见问题

### 数据库为空？

首次使用需要同步数据：
```bash
jcr-mcp-sync
# 选择 1 同步所有数据
```

### 端口被占用？

修改端口：
```bash
JCR_MCP_PORT=9000 jcr-mcp-server sse
```

### 连接超时？

检查：
1. 服务器是否启动：`ps aux | grep jcr-mcp`
2. 端口是否开放：`netstat -tlnp | grep 8080`
3. 防火墙设置

## 下一步

- 📖 查看完整文档：[README.md](README.md)
- 🚀 部署指南：[DEPLOYMENT.md](DEPLOYMENT.md)
- 🔧 迁移指南：[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- 💬 问题反馈：[GitHub Issues](https://github.com/NormanMises/jcr_mcp/issues)
