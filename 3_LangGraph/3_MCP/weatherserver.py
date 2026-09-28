import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather", host="127.0.0.1", port=int(os.getenv("WEATHER_PORT", "8000")))


@mcp.tool()
async def get_weather(city: str) -> str:
    """Return demo weather for a city; this is not a live weather forecast."""
    return "Demo weather (not a live forecast): It's always sunny in " + city


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
