# JCR MCP服务器 Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    JCR_MCP_TRANSPORT=sse \
    JCR_MCP_HOST=0.0.0.0 \
    JCR_MCP_PORT=8080

# 复制项目文件
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .
COPY MANIFEST.in* ./ 
COPY jcr_mcp ./jcr_mcp

# 安装依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# 创建数据目录
RUN mkdir -p /root/.jcr_mcp

# 暴露端口
EXPOSE 8080

# 复制健康检查脚本
COPY healthcheck.py .

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python healthcheck.py || exit 1

# 启动命令
CMD ["jcr-mcp-server", "sse"]
