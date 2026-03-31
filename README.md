# 微信公众号排版编辑器 & 自动化运营平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg)](https://github.com/YUCC-edu/wechat-allauto-gzh)

一个功能完备的微信公众号 Markdown 编辑器与自动化运营工具集，支持前端实时预览排版效果与后端一键推送草稿到微信公众号草稿箱。

---

## 📖 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [目录结构](#-目录结构)
- [快速开始](#-快速开始)
- [前端编辑器使用指南](#-前端编辑器使用指南)
- [Python 技能使用指南](#-python-技能使用指南)
- [微信官方 API 规范](#-微信官方-api-规范)
- [主题系统](#-主题系统)
- [API 参考](#-api-参考)
- [常见问题](#-常见问题)

---

## 🎯 项目简介

本项目是一套完整的微信公众号运营解决方案，包含两个核心组件：

### 1. 前端排版编辑器

基于 React + TypeScript + Vite 构建的 Markdown 编辑器，提供实时预览效果。编辑器将 Markdown 转换为带内联样式的 HTML，兼容微信公众号平台的所有排版需求。

### 2. Python 自动化技能

封装微信公众号官方 API 的 Python 模块，支持草稿箱管理、自定义菜单、素材管理、用户管理、留言管理等运营功能。可作为独立 Python 库使用，也支持集成到 OpenClaw 等 AI 助手框架中。

---

## ✨ 功能特性

### 前端编辑器

| 特性 | 说明 |
|------|------|
| 实时预览 | 左右分栏，左侧编辑 Markdown，右侧即时预览排版效果 |
| 多主题支持 | 6 大主题系列，23 个精美主题供选择 |
| 实时主题切换 | 选择主题后实时更新预览效果 |
| 内联样式 | 生成所有样式内联的 HTML，兼容微信公众号平台 |
| 图片防盗链 | 自动添加 `referrerPolicy="no-referrer"` 规避防盗链 |
| 代码高亮 | 支持语法高亮的代码块展示 |
| 模板预设 | 内置 4 种常用文章模板 |
| 移动端预览 | 模拟手机微信界面的预览效果 |

### Python 技能

| 特性 | 说明 |
|------|------|
| Markdown 自动转换 | 推送到草稿时自动将 Markdown 转换为 HTML |
| 自动图片处理 | 自动识别并上传本地图片到微信素材库 |
| 内容验证 | 自动检查字符数、内容大小等限制 |
| HTML 清理 | 自动移除危险标签和属性 |
| Access Token 管理 | 自动获取、缓存、过期重试 |
| 指数退避重试 | 网络请求失败时自动重试 |

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.x | UI 框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 6.x | 构建工具 |
| TailwindCSS | 4.x | 样式框架 |
| motion | 11.x | 动画库 |
| lucide-react | 0.4.x | 图标库 |
| js-yaml | 4.x | YAML 主题解析 |

### Python 技术

| 技术 | 版本 | 用途 |
|------|------|------|
| requests | 2.x | HTTP 请求 |
| pyyaml | 6.x | YAML 解析 |
| beautifulsoup4 | 4.x | HTML 解析（可选）|

---

## 📁 目录结构

```
wechat-allauto-gzh/
├── src/
│   ├── App.tsx                      # 主界面组件
│   ├── main.tsx                     # 应用入口
│   ├── index.css                    # 全局样式
│   ├── utils/
│   │   ├── WeChatHTMLConverter.ts  # Markdown → HTML 转换引擎
│   │   └── themeLoader.ts          # 主题加载器
│   ├── themes/                      # YAML 主题配置
│   │   ├── macaron/                # 马卡龙系列（12个主题）
│   │   │   ├── blue.yaml
│   │   │   ├── coral.yaml
│   │   │   ├── cream.yaml
│   │   │   └── ... (12个主题)
│   │   ├── wenyan/                 # 文颜系列（8个主题）
│   │   ├── shuimo/                 # 水墨系列（1个主题）
│   │   ├── geek/                   # 极客系列（1个主题）
│   │   ├── magazine/               # 杂志系列（1个主题）
│   │   └── product/                # 产品系列（1个主题）
│   └── skills/                     # Python 自动化技能
│       ├── wechat_capability_skill.py    # 微信 API 封装 + 草稿推送
│       ├── markdown_to_wechat_converter.py # Markdown → HTML 转换器
│       ├── wechat_formatter_skill.py      # 主题加载器
│       ├── content_optimizer.py           # 内容优化（去 AI 痕迹）
│       ├── html_optimizer.py              # HTML 压缩与检查
│       └── openclaw_compat.py            # OpenClaw 框架兼容层
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── pyproject.toml                     # Python 项目配置
├── metadata.json                     # 项目元数据
├── .env.example                      # 环境变量示例
└── .gitignore

23 个主题配置文件
```

---

## 🚀 快速开始

### 前端编辑器

```bash
# 克隆项目
git clone https://github.com/YUCC-edu/wechat-allauto-gzh.git
cd wechat-allauto-gzh

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### Python 技能

```bash
# 安装 Python 依赖
pip install requests pyyaml

# 可选依赖（用于 HTML 解析增强）
pip install beautifulsoup4
```

---

## 📝 前端编辑器使用指南

### 界面布局

编辑器采用左右分栏设计：
- **左侧**：主题选择器 + Markdown 编辑器 + 模板选择
- **右侧**：实时预览窗口 + HTML 代码查看

### 操作流程

1. **选择主题**：在左侧顶部选择主题分类（如"马卡龙"），再选择具体主题（如"蓝色"）
2. **编辑内容**：在 Markdown 编辑器中输入或粘贴内容
3. **预览效果**：右侧实时显示排版预览
4. **查看代码**：点击「HTML」按钮查看生成的代码
5. **复制使用**：复制 HTML 代码到微信公众号后台使用

### Markdown 支持

编辑器支持标准 Markdown 语法以及扩展语法：

| 语法 | 示例 | 说明 |
|------|------|------|
| 标题 | `# 一级标题` | 支持 1-6 级标题 |
| 粗体 | `**粗体文字**` | 加粗显示 |
| 斜体 | `*斜体文字*` | 斜体显示 |
| 代码块 | ```` ```python ```` | 支持语法高亮 |
| 链接 | `[文字](URL)` | 自动添加样式 |
| 图片 | `![alt](URL)` | 自动处理防盗链 |
| 列表 | `- 项目` / `1. 项目` | 有序/无序列表 |
| 引用 | `> 引用内容` | 优雅的引用样式 |
| 表格 | `\| col1 \| col2 \|` | 完整表格支持 |
| 分割线 | `---` | 分隔线样式 |

### 高级组件

部分主题支持高级排版组件：

```markdown
::: release
# 标题
**加粗文字**
:::

::: grid
PART 1
内容1
---
PART 2
内容2
:::
```

### 模板预设

编辑器内置 4 种模板：
- **功能介绍**：默认示例，展示各种排版元素
- **技术教程**：适合代码较多的技术文章
- **生活随笔**：适合散文、随感类文章
- **高级排版**：展示 `:::release` 和 `:::grid` 高级组件

---

## 🐍 Python 技能使用指南

### 概述

Python 技能模块封装了微信公众号官方 API，支持：
- 草稿箱管理（新建、获取、修改、删除）
- 自定义菜单管理
- 永久素材管理
- 用户管理
- 留言管理
- 发布能力
- 数据统计

### 核心函数

#### 1. 草稿箱管理 `wechat_manage_capability`

```python
from src.skills.wechat_capability_skill import wechat_manage_capability

# 推送 Markdown 内容到草稿箱（自动转换）
result = wechat_manage_capability(
    app_id="wx1234567890abcdef",
    app_secret="your_app_secret_here",
    capability="draft",
    action="add",
    articles=[{
        "title": "文章标题",
        "content": "# Markdown 内容\n\n**加粗文字**",
        "theme": "macaron/blue"  # 可选，指定主题
    }],
    theme="macaron/blue"  # 默认主题
)
```

**自动处理流程**：
1. 检测 `content` 是否为 Markdown 格式
2. 如果是 Markdown，自动转换为带内联样式的 HTML
3. 清理 HTML，移除危险标签（script, iframe 等）
4. 验证内容是否符合微信限制（字符数、大小）
5. 自动上传本地/外部图片到微信素材库
6. 推送到草稿箱

#### 2. 独立 Markdown 转换 `format_markdown_to_wechat_html`

```python
from src.skills.wechat_capability_skill import format_markdown_to_wechat_html

result = format_markdown_to_wechat_html(
    markdown_content="# 标题\n\n**加粗**",
    theme_name="macaron/blue",
    themes_dir="./src/themes"
)

print(result["html"])  # 转换后的 HTML
print(result["success"])  # 是否成功
```

#### 3. 内容验证 `validate_article_content_skill`

```python
from src.skills.wechat_capability_skill import validate_article_content_skill

result = validate_article_content_skill("<p>HTML内容</p>")

print(result["valid"])  # 是否有效
print(result["char_count"])  # 字符数
print(result["warnings"])  # 警告信息
print(result["errors"])  # 错误信息
```

#### 4. HTML 清理 `sanitize_html_skill`

```python
from src.skills.wechat_capability_skill import sanitize_html_skill

# 移除危险标签和属性
result = sanitize_html_skill('<script>alert(1)</script><p onclick="evil()">text</p>')
print(result["html"])  # <p>text</p>
```

### 主题加载

```python
from src.skills.wechat_formatter_skill import ThemeLoader

# 加载主题配置
config = ThemeLoader.load_theme("macaron/blue", "./src/themes")

# 主题配置结构
# {
#     "name": "马卡龙蓝",
#     "category": "macaron",
#     "colors": {"primary": "#3b82f6"},
#     "body": {...},
#     "h1": {...},
#     ...
# }
```

---

## 📋 微信官方 API 规范

> 重要：以下规范基于微信公众平台官方文档，调用 API 时请确保遵守。

### 草稿箱 API 限制

| 项目 | 限制 |
|------|------|
| content 字符数 | 必须少于 20,000 字符 |
| content 大小 | 小于 1MB |
| content 格式 | 支持 HTML 标签 |
| JavaScript | 会被移除 |
| 图片 URL | **必须来自微信素材接口**，外部 URL 会被过滤 |
| 外部图片 | 必须先上传到微信素材库 |

### content 字段支持的 HTML 标签

| 标签 | 说明 |
|------|------|
| `p`, `br`, `span` | 段落与换行 |
| `h1`-`h6` | 标题 |
| `strong`, `b`, `em`, `i`, `u` | 文本样式 |
| `a` | 链接（仅支持微信支付公众号） |
| `img` | 图片 |
| `ul`, `ol`, `li` | 列表 |
| `blockquote` | 引用 |
| `pre`, `code` | 代码块 |
| `table`, `thead`, `tbody`, `tr`, `th`, `td` | 表格 |
| `section`, `div` | 分区容器 |

### content 字段不支持的标签

| 标签 | 说明 |
|------|------|
| `script` | 脚本（会被移除）|
| `style` | 样式（会被移除）|
| `iframe` | 框架 |
| `object`, `embed` | 嵌入对象 |
| `form`, `input`, `textarea` | 表单元素 |
| `video`, `audio`, `canvas`, `svg` | 多媒体/图形 |
| `button`, `select` | 交互元素 |

### 推荐的 HTML 结构

```html
<h1 style="...">标题</h1>
<p style="...">段落内容，<strong style="...">加粗</strong>和<em style="...">斜体</em></p>
<img src="https://mmbiz.qpic.cn/..." style="..." referrerpolicy="no-referrer">
<pre style="..."><code>代码内容</code></pre>
<blockquote style="...">引用内容</blockquote>
<table style="..."><tr><th>表头</th></tr><tr><td>内容</td></tr></table>
```

---

## 🎨 主题系统

### 主题分类

| 分类 | 主题数 | 风格特点 | 适用场景 |
|------|--------|----------|----------|
| **macaron** | 12 | 清新明亮，低饱和度配色 | 科技、商务、教育、知识分享 |
| **wenyan** | 8 | 古风雅致，传统色彩搭配 | 文学、历史、艺术、散文 |
| **shuimo** | 1 | 中国传统水墨风 | 文化、美学类内容 |
| **geek** | 1 | 终端命令行风格 | 技术文档、编程教程 |
| **magazine** | 1 | 黑白极简，大字号 | 深度阅读、图文内容 |
| **product** | 1 | 支持高级排版组件 | 产品发布、精选内容 |

### 马卡龙系列主题

| 主题名 | 颜色主调 |
|--------|----------|
| `blue` | 马卡龙蓝 `#3b82f6` |
| `coral` | 珊瑚红 |
| `cream` | 奶油色 |
| `lavender` | 薰衣草紫 |
| `lemon` | 柠檬黄 |
| `lilac` | 丁香紫 |
| `mint` | 薄荷绿 |
| `peach` | 蜜桃粉 |
| `pink` | 马卡龙粉 |
| `rose` | 玫瑰红 |
| `sage` | 鼠尾草绿 |
| `sky` | 天空蓝 |

### 主题配置格式

主题使用 YAML 格式存储在 `src/themes/` 目录下：

```yaml
# 主题元数据
name: 主题名称
description: 主题描述
keywords: [关键词1, 关键词2]
category: 分类名

# 颜色配置
colors:
  primary: "#3b82f6"      # 主色调
  accent: "#dbeafe"         # 强调色
  text: "#0f172a"          # 主文字色
  text_light: "#64748b"     # 次要文字
  background: "#ffffff"    # 背景色

# 样式配置
styles:
  body:
    font_size: "16px"
    line_height: "1.75"
    color: "#0f172a"
  
  h1:
    font_size: "24px"
    font_weight: "normal"
    text_align: "center"
    color: "#3b82f6"
  
  # ... 其他样式
```

---

## 🔌 API 参考

### `wechat_manage_capability`

微信公众号能力管理统一接口。

```python
wechat_manage_capability(
    app_id: str,
    app_secret: str,
    capability: str,  # menu, draft, publish, material, user, comment, message, kf, analysis
    action: str,
    **kwargs
) -> dict
```

### Capability 与 Action 映射

| Capability | 支持的 Action |
|------------|--------------|
| `menu` | `create`, `get`, `delete` |
| `draft` | `add`, `get`, `delete`, `update`, `count`, `batchget` |
| `publish` | `submit`, `get_status`, `delete`, `get_article`, `batchget` |
| `material` | `get`, `delete`, `count`, `batchget` |
| `user` | `get_list`, `get_info`, `update_remark` |
| `comment` | `open`, `close`, `list`, `markelect`, `unmarkelect`, `delete`, `reply`, `delete_reply` |
| `message` | `send_custom`, `send_mass` |
| `kf` | `add`, `get_list` |
| `analysis` | `get_article_summary`, `get_user_summary` |

### 返回值格式

```python
{
    "errcode": 0,           # 0 表示成功，非 0 表示失败
    "errmsg": "ok",         # 错误信息
    # ... 其他响应字段
}
```

### 常见错误码

| errcode | 说明 | 解决方案 |
|----------|------|----------|
| 0 | 成功 | - |
| 40001 | access_token 无效或过期 | 重新获取 access_token |
| 40013 | AppID 不合法 | 检查 app_id 是否正确 |
| 40125 | AppSecret 错误 | 检查 app_secret 是否正确 |
| 48001 | API 未授权 | 需要认证或权限不足 |
| 40029 | oauth_code 无效 | 重新获取授权码 |

---

## ❓ 常见问题

### Q: 推送到草稿箱的内容显示乱码？

**A**: 常见原因及解决方案：

1. **Markdown 未转换**：确保 `content` 字段是 HTML 格式，不是 Markdown
2. **图片 URL 问题**：外部图片 URL 会被微信过滤，需要先上传到微信素材库
3. **字符编码问题**：确保文件保存为 UTF-8 编码

### Q: 代码块中的 `#` 被错误处理成标题？

**A**: 这是一个历史 bug，已在最新版本中修复。代码块现在会被正确保护，`#` 等 Markdown 语法不会被二次处理。

### Q: 如何添加自定义主题？

**A**: 在 `src/themes/` 下创建新的 YAML 主题文件：

```yaml
# src/themes/my_theme.yaml
name: 我的主题
category: custom
colors:
  primary: "#ff6b6b"
styles:
  body:
    font_size: "16px"
    color: "#333"
  # ... 其他样式
```

然后在编辑器或代码中使用 `theme_name="my_theme"` 加载。

### Q: 草稿推送失败，错误码 48001？

**A**: 错误码 48001 表示 API 未授权。检查：
1. 公众号是否完成了认证
2. 是否开通了相关接口权限
3. access_token 是否有效

### Q: 图片上传失败？

**A**: 检查：
1. 图片大小是否超过 2MB
2. 图片格式是否为 JPG/PNG/GIF
3. 网络连接是否正常
4. access_token 是否在有效期内

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
