# 迁移指南 (Migration Guide)

本指南帮助现有用户从旧版本迁移到新的 uvx 部署版本。

## 主要变化

### 1. 包结构变化

**旧版本:**
```
jcr_mcp/
  ├── jcr_mcp_server.py
  ├── data_sync.py
  ├── test_client.py
  └── requirements.txt
```

**新版本:**
```
jcr_mcp/
  ├── jcr_mcp/              # Python 包
  │   ├── __init__.py
  │   ├── server.py
  │   ├── database.py
  │   ├── sync.py
  │   ├── config.py
  │   └── __main__.py
  ├── pyproject.toml        # 现代包配置
  ├── test_client.py
  └── requirements.txt      # 仍保留用于兼容性
```

### 2. 数据库位置变化

**旧版本:** 数据库存储在当前工作目录 `./jcr.db`

**新版本:** 数据库存储在用户目录 `~/.jcr_mcp/jcr.db`

**迁移数据:**
如果你已经有旧的数据库文件，可以将其移动到新位置：

```bash
# Linux/Mac
mkdir -p ~/.jcr_mcp
cp jcr.db ~/.jcr_mcp/

# Windows PowerShell
mkdir $env:USERPROFILE\.jcr_mcp -Force
cp jcr.db $env:USERPROFILE\.jcr_mcp\
```

### 3. 运行方式变化

**旧版本:**
```bash
python jcr_mcp_server.py
python data_sync.py
```

**新版本 (推荐):**
```bash
# 使用 uvx (无需安装)
uvx jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git
uvx --from jcr-mcp-server@git+https://github.com/NormanMises/jcr_mcp.git jcr-mcp-sync

# 使用已安装的命令
jcr-mcp-server
jcr-mcp-sync
```

**新版本 (向后兼容):**
```bash
# 旧的运行方式仍然可用
python jcr_mcp_server.py
python data_sync.py
```

### 4. Claude Desktop 配置变化

**旧配置:**
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

**新配置 (推荐):**
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

## 兼容性说明

### 完全兼容
- ✅ 所有 MCP 工具、资源和提示词保持不变
- ✅ API 接口完全兼容
- ✅ 数据格式完全兼容
- ✅ 旧的运行方式仍然可用

### 需要注意
- ⚠️ 数据库位置变化（需要迁移或重新同步）
- ⚠️ 日志文件位置变化（现在在 `~/.jcr_mcp/data_sync.log`）

## 推荐升级步骤

1. **备份现有数据** (可选)
   ```bash
   cp jcr.db jcr.db.backup
   ```

2. **安装新版本**
   ```bash
   # 如果使用 pip 安装
   pip install git+https://github.com/NormanMises/jcr_mcp.git
   
   # 或者使用 uvx (无需安装)
   # 直接运行即可
   ```

3. **迁移数据** (如果已有数据)
   ```bash
   mkdir -p ~/.jcr_mcp
   cp jcr.db ~/.jcr_mcp/
   ```
   
   或者重新同步数据：
   ```bash
   jcr-mcp-sync  # 选择选项 1
   ```

4. **测试新版本**
   ```bash
   jcr-mcp-server
   # 看到启动信息后按 Ctrl+C 停止
   ```

5. **更新 Claude Desktop 配置**
   - 按照上面的"新配置"更新配置文件
   - 重启 Claude Desktop

## 常见问题

### Q: 我必须升级吗？
A: 不必须。旧的运行方式仍然完全支持。但我们推荐使用新的 uvx 方式，因为它更简单、更可靠。

### Q: 升级后旧数据会丢失吗？
A: 不会。你可以将旧数据库文件复制到新位置，或者重新同步数据。

### Q: uvx 是什么？
A: uvx 是一个快速的 Python 应用运行工具，可以直接从 GitHub 运行 Python 应用，无需手动安装依赖。

### Q: 如果我不想使用 uvx 怎么办？
A: 你可以继续使用 `pip install` 安装，然后使用 `jcr-mcp-server` 命令运行。或者继续使用旧的 `python jcr_mcp_server.py` 方式。

### Q: 数据同步速度慢怎么办？
A: 数据同步需要从 GitHub 下载多个 CSV 文件，速度取决于网络连接。第一次同步可能需要几分钟。

## 获取帮助

如果在迁移过程中遇到问题：

1. 查看 [README.md](README.md) 获取详细文档
2. 在 [GitHub Issues](https://github.com/NormanMises/jcr_mcp/issues) 提问
3. 确保查看日志文件 `~/.jcr_mcp/data_sync.log` 了解详细错误信息

## 回滚

如果需要回滚到旧版本：

```bash
# 卸载新版本
pip uninstall jcr-mcp-server

# 继续使用旧的脚本方式
cd /path/to/old/version
python jcr_mcp_server.py
```
