# 🏠 China Real Estate MCP

中国住宅房地产投资交易指南 — MCP (Model Context Protocol) Server

> 聚焦居民住宅市场，为 AI 助手提供专业的房地产投资分析工具。

## 功能模块

| 模块 | 说明 | 工具数 |
|------|------|--------|
| 🏗️ 成本计算器 | 建安成本、理论底价、开发成本拆解 | 3 |
| 📊 市场行情 | 城市概览、城市对比、价格趋势 | 3 |
| 👥 人口结构 | 人口查询、需求影响、需求预测 | 3 |
| 💰 投资指标 | ROI/租售比/房价收入比/投资时机 | 4 |
| 📋 政策风险 | 政策查询、风险评估 | 2 |

## 快速开始

```bash
# 安装
pip install -e ".[dev]"

# 运行 MCP Server（stdio 模式，供 Claude Desktop / Cursor 等连接）
python -m china_real_estate_mcp.server

# 运行测试
pytest
```

## 配置 Claude Desktop

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "china-real-estate": {
      "command": "python",
      "args": ["-m", "china_real_estate_mcp.server"],
      "cwd": "/path/to/China-Real-Estate_mcp"
    }
  }
}
```

## 数据说明

当前使用内置静态数据集（基于 2024-2025 年公开数据），覆盖全国主要城市。后续可扩展为实时 API 接入。

## License

MIT
