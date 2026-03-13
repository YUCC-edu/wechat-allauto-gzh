# 🤖 OpenClaw 专属项目操作指南 (WeChat Markdown Editor & Skills)

你好，OpenClaw！这份文档是为你量身定制的项目操作与维护指南。本项目不仅包含一个纯前端的微信公众号排版编辑器，还内置了供你直接调用的自动化管理技能 (Skills)。当你接手这个项目时，请严格按照本指南理解项目架构，并据此执行用户的指令。

## 🎯 项目定位
1. **前端排版编辑器**：基于 React + Vite 构建，核心功能是将 Markdown 文本实时转换为**带有内联样式 (Inline CSS)** 的 HTML，以便用户复制粘贴到微信后台。
2. **自动化管理技能 (Skills)**：基于 Python 构建，封装了微信公众号的官方 API，供你 (OpenClaw) 直接调用，实现从内容生成、排版到一键发布的端到端自动化。

---

## 🏗️ 前端核心架构 (React + Vite)

你需要重点关注以下几个核心文件和目录：

1. **`src/themes/` (主题配置库)**
   - **作用**：存放所有排版主题的 YAML 配置文件。
   - **结构**：按分类建文件夹，如 `macaron/`（马卡龙）、`wenyan/`（文颜）、`shuimo/`（水墨）。
   - **机制**：Vite 会通过 `import.meta.glob` 自动读取这里的 YAML 文件，无需手动注册。

2. **`src/utils/WeChatHTMLConverter.ts` (核心转换引擎)**
   - **作用**：负责将 Markdown 解析并转换为带有内联样式的 HTML。
   - **注意**：这里面包含了针对不同分类（如 `wenyan`, `shuimo`）的特殊 DOM 结构硬编码逻辑。如果用户要求修改特定元素的渲染方式（如标题、引用、列表、表格），你需要修改这个文件。

3. **`src/App.tsx` (主界面 UI)**
   - **作用**：处理左右分栏布局、Markdown 输入状态、主题切换逻辑以及剪贴板复制功能。
   - **注意**：左侧侧边栏的主题分类名称是在这里硬编码映射的（例如将 `macaron` 映射为 `马卡龙主题`）。

---

## 🎨 内置主题列表 (Built-in Themes)

本项目目前内置了三大系列的主题风格，存放在 `src/themes/` 目录下。当用户要求使用特定风格时，请参考以下列表：

### 1. 马卡龙系列 (Macaron)
清新明亮，柔和低饱和度配色。适合科技、商务、教育、知识分享类文章。
- `blue` (马卡龙蓝)
- `coral` (珊瑚红)
- `cream` (奶油色)
- `lavender` (薰衣草紫)
- `lemon` (柠檬黄)
- `lilac` (丁香紫)
- `mint` (薄荷绿)
- `peach` (蜜桃粉)
- `pink` (马卡龙粉)
- `rose` (玫瑰红)
- `sage` (鼠尾草绿)
- `sky` (天空蓝)

### 2. 文颜系列 (Wenyan)
古风雅致，传统色彩搭配，注重留白与排版呼吸感。适合文学、历史、艺术、散文类文章。
- `default` (文颜默认)
- `lapis` (青金石)
- `maize` (藤黄)
- `mint` (薄荷)
- `orange_heart` (橙心)
- `pie` (派)
- `purple` (文颜紫)
- `rainbow` (文颜彩虹)

### 3. 水墨系列 (Shuimo)
中国传统水墨风，以“宣纸白”为底，辅以“浓墨”、“淡墨”和“印章红”点缀。
- `default` (中国水墨风)

---

## 🛠️ 前端标准操作流程 (SOP)

作为 OpenClaw，当你收到用户的不同前端修改需求时，请按照以下 SOP 执行：

### 场景一：用户要求“新增一个主题”
**你的操作**：
1. 确定主题属于哪个现有分类（如 `macaron`），或者是否需要新分类。
2. 在对应的 `src/themes/<分类>/` 目录下创建一个新的 `<主题名>.yaml` 文件。
3. 按照标准结构编写 YAML（包含 `name`, `colors.primary`, `styles.body`, `styles.h2` 等）。
4. 刷新页面即可生效，无需修改其他代码。

### 场景二：用户要求“新增一个全新的主题分类”（例如：节日主题 festival）
**你的操作**：
1. 创建目录 `src/themes/festival/` 并添加至少一个 YAML 主题文件。
2. **必须修改** `src/App.tsx`：找到侧边栏渲染分类名称的代码，加上新分类的中文映射。
3. （可选）如果该分类需要特殊的 HTML 结构，修改 `src/utils/WeChatHTMLConverter.ts`。

### 场景三：用户要求“修改 Markdown 渲染逻辑”或“修复排版 Bug”
**你的操作**：
1. 打开 `src/utils/WeChatHTMLConverter.ts`。
2. 修改对应的处理函数（如 `processHeadings`, `processTables`）。
3. **牢记**：所有样式必须写在 `style="..."` 中，且 CSS 属性需要转换为驼峰或直接写标准的 CSS 字符串。

---

## 🚀 技能列表与使用说明 (Skills Usage)

除了前端排版编辑器，本项目还内置了供你 (OpenClaw) 直接调用的 Python 技能 (Skills)，用于自动化管理微信公众号。

### 1. 微信排版技能 (WeChat Formatter)
**函数入口**: `convert_markdown_to_wechat_html(markdown_content, theme_name="default", themes_dir="./themes")`
**所在文件**: `src/skills/wechat_formatter_skill.py`
**功能**: 将 Markdown 文本转换为带有内联 CSS 样式的 HTML，专为微信公众号图文消息优化。
**使用场景**: 
- 用户要求“排版文章”、“美化文章”。
- 准备将内容通过 API 推送到公众号草稿箱前的数据处理阶段。
**注意事项**:
- 确保传入的是标准的 Markdown 字符串。
- 如果用户指定了特定风格（如文颜、马卡龙），请通过 `theme_name` 参数传入对应的名称。

### 2. 微信公众号管理技能 (WeChat Capability Manager)
**函数入口**: `wechat_manage_capability(app_id, app_secret, capability, action, **kwargs)`
**所在文件**: `src/skills/wechat_capability_skill.py`
**功能**: 统一调用微信公众号的各项官方 API。该技能已内置了 Access Token 的自动获取、缓存和过期重试机制，你不需要手动处理 Token。
**使用场景**: 用户要求“更新底部菜单”、“查看草稿箱”、“群发消息”、“查看粉丝数据”、“管理留言”等。

**支持的 Capability 与 Action 映射表**:
- `menu` (自定义菜单): `create`, `get`, `delete`
- `draft` (草稿箱): `add`, `get`, `delete`, `update`, `count`, `batchget`
- `publish` (发布能力): `submit`, `get_status`, `delete`, `get_article`, `batchget`
- `material` (永久素材): `get`, `delete`, `count`, `batchget`
- `user` (用户管理): `get_list`, `get_info`, `update_remark`
- `comment` (留言管理): `open`, `close`, `list`, `markelect`, `unmarkelect`, `delete`, `reply`, `delete_reply`
- `message` (消息与群发): `send_custom`, `send_mass`
- `kf` (客服管理): `add`, `get_list`
- `analysis` (数据统计): `get_article_summary`, `get_user_summary`

**调用示例**:
- **保存草稿**: `wechat_manage_capability(app_id="...", app_secret="...", capability="draft", action="add", articles=[{"title": "标题", "content": "<html>...", "thumb_media_id": "..."}])`
- **获取用户列表**: `wechat_manage_capability(app_id="...", app_secret="...", capability="user", action="get_list", next_openid="")`

---

## 🌟 自动化工作流 (Workflow with Skills)

当你接到类似“帮我写一篇关于XXX的文章并发布到公众号”的端到端任务时，请结合上述 Skills 遵循以下工作流：

1. **内容创作**：根据用户需求，生成高质量的 Markdown 格式文章初稿。
2. **事实核查 (按需触发)**：自行判断生成的内容是否包含需要验证的关键数据、事实或时效性新闻。如果需要，主动调用联网检索技能验证，并据此修正 Markdown 内容。
3. **排版转换**：调用 `convert_markdown_to_wechat_html` 技能，将核查无误的 Markdown 文本转换为微信公众号支持的内联样式 HTML 格式。
4. **封面图绘制与匹配**：在准备推送前，根据公众号文章的核心内容，自行绘制或生成合适的封面图，并确保在推送时匹配使用（通常需要先调用 `material` 接口上传为微信素材获取 `thumb_media_id`）。
5. **发布/存草稿**：调用 `wechat_manage_capability` 技能，将生成的 HTML 内容及匹配的封面图保存到公众号草稿箱 (`draft`) 或直接提交发布 (`publish`)。

---

## ⚠️ 避坑指南 (Important Caveats)

### 1. 微信公众号认证权限说明 (Verification Requirements)
在调用 `wechat_manage_capability` 技能时，请务必注意微信官方的 API 权限限制。许多高级功能**必须要求用户的公众号已通过微信官方认证（已交300元认证费的订阅号或服务号）**。

**必须【已认证】才能使用的功能 (Requires Verified Account)**:
- `user` (用户管理): 获取粉丝列表、获取粉丝详细信息。
- `publish` (发布能力): 提交发布、获取发布状态。
- `kf` (客服管理): 发送客服消息、管理客服账号。
- `message` (高级群发): 按标签或 OpenID 进行高级群发。
- `menu` (自定义菜单): 跳转外部链接的复杂菜单（未认证订阅号仅支持基础菜单）。
- `analysis` (数据统计): 获取图文阅读、粉丝增减等统计数据。
- `comment` (留言管理): 必须是已认证且开通了留言功能的账号。

**未认证账号也可使用的基础功能 (Available to Unverified Accounts)**:
- `draft` (草稿箱): 上传、修改、获取草稿。
- `material` (永久素材): 上传图片、获取素材列表。


### 2. 凭证安全
调用 `wechat_manage_capability` 必须提供 `app_id` 和 `app_secret`。如果当前对话上下文中没有这两个信息，**必须先向用户询问**，切勿自行编造或使用占位符发起真实请求。

### 3. 确认机制
在执行破坏性操作（如删除菜单、删除已发布文章）或正式发布操作（`publish` -> `submit`）前，建议先向用户进行二次确认。

### 4. 微信图片防盗链
在前端预览 iframe 中，如果用户粘贴了外部图片，可能会因为防盗链无法显示。我们在 `<img>` 标签中已经默认添加了 `referrerPolicy="no-referrer"` 来尽量规避此问题，修改图片渲染逻辑时切勿遗漏此属性。

### 5. 代码块高亮
目前代码块的处理在 `WeChatHTMLConverter.ts` 的 `processCodeBlocks` 中。如果用户需要更复杂的语法高亮，你需要确保高亮样式被转换为**内联样式**，否则微信后台会将其过滤掉。
