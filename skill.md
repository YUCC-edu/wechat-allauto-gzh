# OpenClaw 微信公众号技能使用指南 (Skill Instructions for OpenClaw)

这份文档是专门写给 OpenClaw (AI 助手) 的操作指南。当你需要协助用户运营、管理微信公众号或进行文章排版时，请严格参考以下技能说明和工作流。

## 🌟 核心工作流 (Standard Workflow)

当你接到类似“帮我写一篇关于XXX的文章并发布到公众号”的端到端任务时，请遵循以下标准工作流：

1. **内容创作**：根据用户需求，生成高质量的 Markdown 格式文章初稿。
2. **事实核查 (强烈建议)**：调用 `tavily_search` 技能，对文章中的关键数据、事实、时效性新闻进行联网检索验证，并据此修正 Markdown 内容，防止 AI 幻觉。
3. **排版转换**：调用 `convert_markdown_to_wechat_html` 技能，将核查无误的 Markdown 文本转换为微信公众号支持的内联样式 HTML 格式。
4. **发布/存草稿**：调用 `wechat_manage_capability` 技能，将生成的 HTML 内容保存到公众号草稿箱 (`draft`) 或直接提交发布 (`publish`)。

---

## 🛠️ 技能列表与使用说明

### 1. 微信排版技能 (WeChat Formatter)
**函数入口**: `convert_markdown_to_wechat_html(markdown_content, theme_name="default", themes_dir="./themes")`
**所在文件**: `src/skills/wechat_formatter_skill.py`
**功能**: 将 Markdown 文本转换为带有内联 CSS 样式的 HTML，专为微信公众号图文消息优化，解决了微信编辑器不支持外部样式表的问题。
**使用场景**: 
- 用户要求“排版文章”、“美化文章”。
- 用户需要“预览公众号效果”。
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

## ⚠️ 交互准则 (Interaction Guidelines)

1. **凭证安全**：调用 `wechat_manage_capability` 必须提供 `app_id` 和 `app_secret`。如果当前对话上下文中没有这两个信息，**必须先向用户询问**，切勿自行编造或使用占位符发起真实请求。
2. **错误处理**：如果 API 调用返回错误（例如 `errcode != 0`），请解析错误信息，并用人类易懂的语言向用户解释原因（如：AppSecret 错误、IP 未在白名单、接口调用频次超限等），并提供修复建议。
3. **确认机制**：在执行破坏性操作（如删除菜单、删除已发布文章）或正式发布操作（`publish` -> `submit`）前，建议先向用户进行二次确认。
4. **所见即所得**：在完成 Markdown 到 HTML 的排版转换后，可以向用户展示部分 HTML 代码或告知转换已成功，等待用户确认后再执行推送到草稿箱的操作。
