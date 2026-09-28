# FastMCP是一个帮助你快速创建 MCP Server 的高级封装
from mcp.server.fastmcp import FastMCP

# 这是一个“工具服务程序”，注册两个工具       ↓
# 等待 MCP Client 来连接
# Client 发送 tool call
# Server 执行 Python function
# 把结果返回给 Client

# Agent并不知道每个server和function会干什么，而是MCP Server会把这些能力以标准化 metadata 暴露出来，Client 先发现它们 即 tool list，再交给 Agent

mcp = FastMCP("Math") #创建一个名叫 "Math" 的 MCP server


@mcp.tool()
# 把下面这个普通 Python function 注册成 MCP tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def multiple(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


# The client launches this server and communicates through stdin/stdout.
if __name__ == "__main__":
    # 只有当你直接运行这个 .py 文件时，才执行下面的代码
    # stdio standard input, standard output
    mcp.run(transport="stdio")
