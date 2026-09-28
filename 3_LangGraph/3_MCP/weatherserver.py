import os #读取环境变量
# 创建 Weather MCP Server
from mcp.server.fastmcp import FastMCP
# 在 127.0.0.1:8000 启动 HTTP Server等待 MCP Client 通过 HTTP 连接
# 创建 Weather MCP Server, 这个 server 只能通过当前这台电脑本地访问
mcp = FastMCP("Weather", host="127.0.0.1", port=int(os.getenv("WEATHER_PORT", "8000")))

# 注册 get_weather tool
@mcp.tool()
async def get_weather(city: str) -> str:
    """Return demo weather for a city; this is not a live weather forecast."""
    return "Demo weather (not a live forecast): It's always sunny in " + city


if __name__ == "__main__":
    # Client 调用 get_weather(city)
    mcp.run(transport="streamable-http")
