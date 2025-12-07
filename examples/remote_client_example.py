"""
远程MCP客户端示例
演示如何连接到托管的JCR MCP服务器
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def example_sse_connection():
    """
    SSE远程连接示例（需要服务器以SSE模式运行）
    """
    print("📡 SSE远程连接示例代码")
    print("="*50)
    
    example_code = '''
# 使用SSE连接远程服务器
# 服务器需要以 SSE 模式运行: jcr-mcp-server sse

from mcp import ClientSession
from mcp.client.sse import sse_client

async def connect_to_remote_server():
    """连接到远程MCP服务器"""
    server_url = "http://your-server:8080"
    
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            # 调用工具
            result = await session.call_tool("search_journal", {
                "journal_name": "Nature"
            })
            
            print(result.content[0].text)

# 运行
asyncio.run(connect_to_remote_server())
'''
    print(example_code)


def main():
    """主函数"""
    print("="*60)
    print("JCR MCP 远程客户端示例")
    print("="*60)
    
    try:
        # 显示SSE远程连接代码
        asyncio.run(example_sse_connection())
        
        print("\n✨ 示例代码显示完成！")
        print("\n💡 使用说明:")
        print("1. 启动远程服务器: jcr-mcp-server sse")
        print("2. 将示例代码中的 server_url 改为实际地址")
        print("3. 运行客户端代码连接服务器")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
