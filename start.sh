#!/bin/bash
# JCR MCP服务器启动脚本

set -e

# 默认配置
TRANSPORT=${JCR_MCP_TRANSPORT:-stdio}
HOST=${JCR_MCP_HOST:-0.0.0.0}
PORT=${JCR_MCP_PORT:-8080}

# 显示使用说明
show_usage() {
    echo "JCR MCP服务器启动脚本"
    echo ""
    echo "用法: $0 [transport]"
    echo ""
    echo "参数:"
    echo "  transport    传输协议 (stdio|sse|streamable-http)，默认: stdio"
    echo ""
    echo "环境变量:"
    echo "  JCR_MCP_TRANSPORT    传输协议"
    echo "  JCR_MCP_HOST         监听地址 (仅sse/streamable-http)"
    echo "  JCR_MCP_PORT         监听端口 (仅sse/streamable-http)"
    echo ""
    echo "示例:"
    echo "  $0 stdio                      # 本地模式"
    echo "  $0 sse                        # SSE模式"
    echo "  JCR_MCP_PORT=9000 $0 sse      # 指定端口"
    echo ""
}

# 检查帮助参数
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

# 获取传输协议参数
if [ -n "$1" ]; then
    TRANSPORT=$1
fi

# 验证传输协议
if [[ ! "$TRANSPORT" =~ ^(stdio|sse|streamable-http)$ ]]; then
    echo "❌ 错误: 不支持的传输协议 '$TRANSPORT'"
    echo ""
    show_usage
    exit 1
fi

# 设置环境变量
export JCR_MCP_TRANSPORT=$TRANSPORT
export JCR_MCP_HOST=$HOST
export JCR_MCP_PORT=$PORT

# 启动服务器
echo "🚀 启动JCR MCP服务器..."
echo "📡 传输协议: $TRANSPORT"

if [ "$TRANSPORT" != "stdio" ]; then
    echo "🔌 监听地址: $HOST:$PORT"
fi

exec jcr-mcp-server $TRANSPORT
