# 微信公众号排版编辑器 & 自动化工具

一个纯前端的微信公众号 Markdown 编辑器，配合 Python 自动化技能实现公众号运营全流程管理。

## 🎯 项目简介

本项目包含两个核心部分：

### 1. 前端排版编辑器
基于 React + Vite 构建的 Markdown 转微信 HTML 编辑器，特点：
- **实时预览**：左侧输入 Markdown，右侧即时查看微信公众号排版效果
- **内联样式**：生成所有样式内联的 HTML，兼容微信公众号平台
- **多主题支持**：内置 6 大系列 20+ 精美主题

### 2. Python 自动化技能
封装微信公众号官方 API 的 Python 模块，支持：
- 草稿箱管理（上传、修改、获取、删除）
- 自定义菜单管理
- 永久素材管理
- 用户管理
- 留言管理
- 数据统计
- 内容优化（去除 AI 痕迹）
- HTML 优化与检查

---

## 🛠️ 技术栈

### 前端
| 技术 | 用途 |
|------|------|
| React 19 | UI 框架 |
| TypeScript | 类型安全 |
| Vite 6 | 构建工具 |
| TailwindCSS 4 | 样式框架 |
| motion | 动画库 |
| lucide-react | 图标库 |
| js-yaml | YAML 主题解析 |

### Python 技能
| 依赖 | 用途 |
|------|------|
| requests | HTTP 请求 |
| pyyaml | YAML 解析 |

---

## 🎨 内置主题（6 大系列）

### 1. 马卡龙系列 (macaron)
清新明亮，柔和低饱和度配色。适合科技、商务、教育、知识分享类文章。
- `blue` (马卡龙蓝)、`coral` (珊瑚红)、`cream` (奶油色)、`lavender` (薰衣草紫)
- `lemon` (柠檬黄)、`lilac` (丁香紫)、`mint` (薄荷绿)、`peach` (蜜桃粉)
- `pink` (马卡龙粉)、`rose` (玫瑰红)、`sage` (鼠尾草绿)、`sky` (天空蓝)

### 2. 文颜系列 (wenyan)
古风雅致，传统色彩搭配，注重留白与排版呼吸感。适合文学、历史、艺术、散文类文章。
- `default` (文颜默认)、`lapis` (青金石)、`maize` (藤黄)、`mint` (薄荷)
- `orange_heart` (橙心)、`pie` (派)、`purple` (文颜紫)、`rainbow` (文颜彩虹)

### 3. 水墨系列 (shuimo)
中国传统水墨风，以"宣纸白"为底，辅以"浓墨"、"淡墨"和"印章红"点缀。
- `default` (中国水墨风)

### 4. 极客系列 (geek)
终端命令行风格，适合硬核技术文章。
- `default` (矩阵绿)

### 5. 杂志系列 (magazine)
黑白极简，大字号，适合图文并茂的深度阅读。
- `default` (经典画报)

### 6. 产品系列 (product)
支持高级组件（`:::release` 和 `:::grid` 语法），适合产品发布、精选内容。
- `default` (产品发布卡片)

---

## 🏗️ 核心架构

### 前端目录结构
```
src/
├── App.tsx                      # 主界面 UI（左右分栏布局）
├── main.tsx                     # 应用入口
├── index.css                    # 全局样式
├── utils/
│   ├── WeChatHTMLConverter.ts  # 核心 Markdown→HTML 转换引擎
│   └── themeLoader.ts          # 主题加载器
├── themes/                      # YAML 主题配置目录
│   ├── macaron/                 # 马卡龙主题（12个）
│   ├── wenyan/                  # 文颜主题（8个）
│   ├── shuimo/                  # 水墨主题（1个）
│   ├── geek/                    # 极客主题（1个）
│   ├── magazine/                # 杂志主题（1个）
│   └── product/                 # 产品主题（1个）
└── skills/                      # Python 自动化技能
```

### Python 技能模块
| 文件 | 功能 |
|------|------|
| `wechat_capability_skill.py` | 微信公众号 API 统一封装 |
| `content_optimizer.py` | 内容优化（去除 AI 痕迹）|
| `html_optimizer.py` | HTML 压缩与兼容性检查 |
| `openclaw_compat.py` | OpenClaw 框架兼容层 |
| `wechat_formatter_skill.py` | 主题加载器（ThemeLoader）|

---

## 🚀 快速开始

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```
访问 http://localhost:3000

### 构建生产版本
```bash
npm run build
```

---

## 📝 使用说明

### 前端编辑器
1. 左侧选择主题分类和具体主题
2. 在左侧 Markdown 编辑器中输入内容
3. 右侧实时预览微信公众号排版效果
4. 点击「HTML」按钮查看生成的代码
5. 复制 HTML 到微信公众号后台

### 模板示例
编辑器内置 4 个模板：
- **功能介绍**：默认示例，展示各种排版元素
- **技术教程**：适合代码较多的技术文章
- **生活随笔**：适合散文、随感类文章
- **高级排版**：展示 `:::release` 和 `:::grid` 高级组件

### Python 技能
详见 `skill.md` 技能使用说明书。

---

## ⚠️ 注意事项

1. **图片防盗链**：编辑器已默认添加 `referrerPolicy="no-referrer"` 规避防盗链问题
2. **内联样式**：微信公众号不支持外部 CSS，所有样式必须内联
3. **代码块高亮**：在 `WeChatHTMLConverter.ts` 的 `processCodeBlocks` 中处理
4. **认证权限**：许多高级 API 功能需要已认证的公众号才能使用
