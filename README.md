# 微信公众号 AI 助手技能 (WeChat Official Account AI Skills)

本项目包含一系列为大模型（如基于 OpenClaw 的 AI 助手）设计的微信公众号管理与排版技能（Skills）。旨在帮助 AI 助手无缝对接微信公众号的各项能力，实现自动化排版、内容发布、用户管理、数据统计等全方位功能。

## 包含的技能模块

### 1. 微信公众号排版转换器 (`wechat_formatter_skill.py`)

将标准的 Markdown 文本一键转换为微信公众号兼容的精美 HTML 格式。

**核心特性：**
- **多主题支持**：内置多种排版主题（如“默认”、“文颜”、“马卡龙”等），支持通过 YAML 文件自定义主题样式。
- **全元素覆盖**：支持标题、粗体、斜体、代码块、行内代码、列表、引用块、表格、分割线等 Markdown 元素的深度定制与美化。
- **微信兼容性**：自动将 CSS 样式内联，确保在微信公众号图文消息中的完美呈现。

**接口调用示例：**
```python
from skills.wechat_formatter_skill import convert_markdown_to_wechat_html

html_content = convert_markdown_to_wechat_html(
    markdown_content="## 欢迎关注\n这是一篇测试文章。",
    theme_name="wenyan" # 使用文颜主题
)
```

### 2. 微信公众号能力管理 (`wechat_capability_skill.py`)

微信公众号各项核心能力管理的统一 API 接口，参考微信官方《公众号开发指南》实现。

**核心特性：**
- **自动 Token 管理**：内置 `access_token` 的自动获取、缓存与过期重试机制，无需手动维护。
- **九大能力模块支持**：
  1. **自定义菜单 (`menu`)**：创建、查询、删除菜单。
  2. **草稿箱管理 (`draft`)**：新建、获取、删除、修改草稿及批量获取。
  3. **发布能力 (`publish`)**：提交发布、轮询状态、删除发布、获取已发布文章。
  4. **素材管理 (`material`)**：获取、删除永久素材及批量获取。
  5. **用户管理 (`user`)**：获取用户列表、基本信息及设置备注名。
  6. **留言管理 (`comment`)**：打开/关闭留言、查看列表、精选/取消精选、回复及删除。
  7. **基础消息与群发 (`message`)**：发送客服消息及根据标签群发。
  8. **客服管理 (`kf`)**：添加客服账号及获取客服列表。
  9. **数据统计 (`analysis`)**：获取图文群发每日数据及用户增减数据。

**接口调用示例：**
```python
from skills.wechat_capability_skill import wechat_manage_capability

APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"

# 示例 1：获取草稿箱列表
drafts = wechat_manage_capability(
    app_id=APP_ID, 
    app_secret=APP_SECRET, 
    capability="draft", 
    action="batchget", 
    offset=0, 
    count=10
)

# 示例 2：创建自定义菜单
menu_response = wechat_manage_capability(
    app_id=APP_ID, 
    app_secret=APP_SECRET, 
    capability="menu", 
    action="create", 
    menu_data={
        "button": [
            {"type": "click", "name": "今日歌曲", "key": "V1001_TODAY_MUSIC"}
        ]
    }
)
```

## 进阶功能：AI 内容搜索验证 (推荐)

在将 AI 生成的 Markdown 内容转换为微信公众号图文并发布之前，强烈建议对内容中的事实、数据和时效性信息进行搜索验证，以避免 AI 幻觉导致发布错误信息。

**如何实现？**
推荐安装并结合使用 **Tavily Search** 技能（`tavily_search_skill`）来进行自动化事实核查。

**推荐工作流：**
1. **内容生成**：AI 助手生成初始 Markdown 文章。
2. **事实核查 (Tavily Search)**：提取文章中的关键事实、数据或新闻，调用 Tavily Search 技能进行联网检索对比，修正 Markdown 内容。
3. **排版转换**：调用 `wechat_formatter_skill` 将核查后的 Markdown 转换为微信 HTML。
4. **一键发布**：调用 `wechat_capability_skill` 将 HTML 保存至草稿箱或直接发布。

**Tavily Search 技能安装引导：**
请确保您的 OpenClaw 环境中已安装 Tavily 搜索技能。通常可以通过配置 Tavily API Key 并引入相应的 search skill 来实现：

```python
# 概念示例：结合 Tavily 搜索进行验证
from skills.tavily_search_skill import tavily_search

# 1. 验证文章中的某个事实
search_result = tavily_search(query="2024年微信公众号活跃用户数")

# 2. 根据搜索结果修正 markdown_content 后再进行转换...
```

## 目录结构

```text
/src/skills/
├── wechat_formatter_skill.py   # Markdown 转微信 HTML 排版技能
└── wechat_capability_skill.py  # 微信公众号能力管理统一接口
```

## 依赖说明

- `requests`: 用于发送 HTTP 请求调用微信 API。
- `PyYAML`: 用于解析排版主题的 YAML 配置文件。
