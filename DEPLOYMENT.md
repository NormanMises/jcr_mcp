# 部署指南 (Deployment Guide)

本指南介绍如何将JCR MCP服务器部署为可托管的远程服务。

## 部署方式

### 方式一：Docker 部署（推荐）

#### 1. 使用 Docker Compose（最简单）

```bash
# 1. 克隆仓库
git clone https://github.com/NormanMises/jcr_mcp.git
cd jcr_mcp

# 2. 首次运行前，同步数据（可选，也可在容器内运行）
pip install -e .
jcr-mcp-sync  # 选择 1 同步所有数据

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

服务将在 `http://localhost:8080` 上运行。

#### 2. 使用 Docker 命令

```bash
# 构建镜像
docker build -t jcr-mcp-server .

# 运行容器
docker run -d \
  --name jcr-mcp-server \
  -p 8080:8080 \
  -v jcr-data:/root/.jcr_mcp \
  -e JCR_MCP_TRANSPORT=sse \
  jcr-mcp-server

# 在容器内同步数据（首次运行）
docker exec -it jcr-mcp-server jcr-mcp-sync

# 查看日志
docker logs -f jcr-mcp-server

# 停止容器
docker stop jcr-mcp-server
```

### 方式二：直接部署

#### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/NormanMises/jcr_mcp.git
cd jcr_mcp

# 安装
pip install -e .

# 同步数据
jcr-mcp-sync  # 选择 1 同步所有数据
```

#### 2. 启动服务

**使用 SSE 传输（推荐）：**
```bash
# 默认在 0.0.0.0:8080 启动
jcr-mcp-server sse

# 或使用环境变量配置
JCR_MCP_HOST=0.0.0.0 JCR_MCP_PORT=8080 jcr-mcp-server sse
```

**使用 streamable-http 传输：**
```bash
jcr-mcp-server streamable-http
```

### 方式三：使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/jcr-mcp.service`：

```ini
[Unit]
Description=JCR MCP Server
After=network.target

[Service]
Type=simple
User=jcr-mcp
WorkingDirectory=/opt/jcr_mcp
Environment="JCR_MCP_TRANSPORT=sse"
Environment="JCR_MCP_HOST=0.0.0.0"
Environment="JCR_MCP_PORT=8080"
ExecStart=/usr/local/bin/jcr-mcp-server sse
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable jcr-mcp
sudo systemctl start jcr-mcp
sudo systemctl status jcr-mcp
```

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `JCR_MCP_TRANSPORT` | 传输协议：stdio/sse/streamable-http | `stdio` |
| `JCR_MCP_HOST` | 监听地址 | `0.0.0.0` |
| `JCR_MCP_PORT` | 监听端口 | `8080` |

## 客户端连接

### ModelScope 客户端

在 ModelScope 平台配置：

```json
{
  "mcpServers": {
    "jcr-partition": {
      "url": "http://your-server:8080",
      "transport": "sse"
    }
  }
}
```

### Claude Desktop（远程模式）

对于远程部署的服务器，需要使用支持 HTTP/SSE 的 MCP 客户端。

### 自定义客户端

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://your-server:8080") as (read, write):
    async with ClientSession(read, write) as session:
        # 初始化
        await session.initialize()
        
        # 调用工具
        result = await session.call_tool("search_journal", {
            "journal_name": "Nature"
        })
        print(result)
```

## 云平台部署

### Railway

1. Fork 本仓库
2. 在 Railway 创建新项目
3. 连接 GitHub 仓库
4. 设置环境变量：
   - `JCR_MCP_TRANSPORT=sse`
5. 部署

### Fly.io

创建 `fly.toml`：

```toml
app = "jcr-mcp-server"
primary_region = "hkg"

[build]
  dockerfile = "Dockerfile"

[env]
  JCR_MCP_TRANSPORT = "sse"
  JCR_MCP_HOST = "0.0.0.0"
  JCR_MCP_PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[mounts]
  source = "jcr_data"
  destination = "/root/.jcr_mcp"
```

部署：
```bash
fly deploy
```

### Heroku

创建 `Procfile`：

```
web: jcr-mcp-server sse
```

部署：
```bash
heroku create jcr-mcp-server
heroku config:set JCR_MCP_TRANSPORT=sse
git push heroku main
```

### 阿里云/腾讯云/AWS

1. 创建 ECS/EC2 实例
2. 安装 Docker
3. 使用 Docker Compose 部署
4. 配置防火墙开放 8080 端口
5. （可选）配置 Nginx 反向代理和 SSL

## 数据管理

### 数据同步

容器内或服务器上运行：
```bash
jcr-mcp-sync
```

### 数据备份

```bash
# 备份数据库
cp ~/.jcr_mcp/jcr.db ~/jcr.db.backup

# Docker 环境
docker cp jcr-mcp-server:/root/.jcr_mcp/jcr.db ./jcr.db.backup
```

### 数据恢复

```bash
# 恢复数据库
cp ~/jcr.db.backup ~/.jcr_mcp/jcr.db

# Docker 环境
docker cp ./jcr.db.backup jcr-mcp-server:/root/.jcr_mcp/jcr.db
docker restart jcr-mcp-server
```

## 监控和维护

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/health

# 或使用 MCP 资源
# 访问 jcr://health 资源
```

### 日志查看

```bash
# Docker
docker logs -f jcr-mcp-server

# systemd
sudo journalctl -u jcr-mcp -f

# 直接运行
# 日志输出到标准输出
```

## 安全建议

1. **使用反向代理**：在生产环境中使用 Nginx/Caddy 等反向代理
2. **启用 HTTPS**：使用 Let's Encrypt 获取免费 SSL 证书
3. **限制访问**：配置防火墙规则限制访问来源
4. **定期备份**：定期备份数据库文件
5. **监控资源**：监控 CPU、内存、磁盘使用情况

## 性能优化

1. **数据库优化**：
   - 定期执行 `VACUUM` 清理数据库
   - 为常用查询字段添加索引

2. **并发连接**：
   - 服务器支持多个并发连接
   - 根据负载调整系统资源

3. **缓存**：
   - 考虑使用 Redis 缓存热门查询结果

## 故障排查

### 服务无法启动

```bash
# 检查端口是否被占用
netstat -tlnp | grep 8080

# 检查数据库文件权限
ls -la ~/.jcr_mcp/

# 查看详细日志
jcr-mcp-server sse --verbose  # 如果支持详细模式
```

### 数据库错误

```bash
# 检查数据库完整性
sqlite3 ~/.jcr_mcp/jcr.db "PRAGMA integrity_check;"

# 重新同步数据
jcr-mcp-sync
```

### 连接超时

- 检查防火墙设置
- 确认服务器地址和端口正确
- 检查网络连接

## 更新升级

```bash
# Git 方式
cd jcr_mcp
git pull
pip install -e .

# Docker 方式
docker-compose pull
docker-compose up -d

# 手动构建
docker build -t jcr-mcp-server .
docker-compose up -d
```

## 获取帮助

- [GitHub Issues](https://github.com/NormanMises/jcr_mcp/issues)
- [README.md](README.md)
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
