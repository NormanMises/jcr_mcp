# 示例代码 (Examples)

本目录包含JCR MCP服务器的使用示例。

## 文件列表

- `remote_client_example.py` - 远程客户端连接示例

## 远程客户端示例

演示如何通过SSE协议连接到远程托管的JCR MCP服务器。

### 运行示例

```bash
python remote_client_example.py
```

### 实际使用

1. **启动远程服务器**
   ```bash
   jcr-mcp-server sse
   ```

2. **修改客户端代码中的服务器地址**
   ```python
   server_url = "http://your-server:8080"
   ```

3. **运行客户端代码连接服务器**
   ```bash
   python your_client.py
   ```

## 更多示例

更多使用示例请参考：
- [README.md](../README.md) - 主文档
- [DEPLOYMENT.md](../DEPLOYMENT.md) - 部署指南
