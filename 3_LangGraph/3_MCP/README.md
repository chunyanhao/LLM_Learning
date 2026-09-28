# MCP 示例

数学服务由客户端通过 stdio 自动启动；天气服务通过 HTTP 连接，需要先启动。
天气工具只返回演示数据，不查询实时天气。

在项目根目录执行 `uv sync`，并在根目录 `.env` 配置 `OPENAI_API_KEY`。
客户端默认使用 `gpt-4o`，可通过 `OPENAI_MODEL` 环境变量修改。

## 运行

以下命令都在项目根目录执行。

终端 1（保持运行）：

```sh
uv run 3_LangGraph/3_MCP/weatherserver.py
```

终端 2：

```sh
uv run 3_LangGraph/3_MCP/client.py
```

预期：数学回答为 96，天气回答明确说明是演示数据。
数学服务无需手动启动，单独运行时等待 stdin 输入属于正常行为。

## 8000 端口被占用

可以更换端口，服务端和客户端必须匹配。

终端 1：

```sh
WEATHER_PORT=18000 uv run 3_LangGraph/3_MCP/weatherserver.py
```

终端 2：

```sh
WEATHER_MCP_URL=http://127.0.0.1:18000/mcp uv run 3_LangGraph/3_MCP/client.py
```

连接失败时确认天气服务正在运行，且 URL 路径为 `/mcp`。
