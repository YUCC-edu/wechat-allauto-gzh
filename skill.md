# 微信公众号自动化技能说明书

本文档介绍项目中可用的 Python 自动化技能模块。

## 📚 技能列表

| 模块 | 入口函数 | 功能 |
|------|---------|------|
| 微信公众号管理 | `wechat_manage_capability()` | API 统一封装 |
| 内容优化 | `humanize_text()` | 去除 AI 痕迹 |
| HTML 优化 | `compress_html()` / `check_html_for_wechat()` | 压缩与检查 |
| 主题加载 | `ThemeLoader.load_theme()` | 加载 YAML 主题 |

---

## 1. 微信公众号管理技能

**文件**: `src/skills/wechat_capability_skill.py`

### 函数签名
```python
wechat_manage_capability(app_id: str, app_secret: str, capability: str, action: str, **kwargs) -> dict
```

### 功能
统一调用微信公众号的各项官方 API，内置 Access Token 自动获取、缓存和过期重试机制。

### Capability 与 Action 映射表

| Capability | Action | 说明 |
|------------|--------|------|
| `menu` | `create`, `get`, `delete` | 自定义菜单 |
| `draft` | `add`, `get`, `delete`, `update`, `count`, `batchget` | 草稿箱 |
| `publish` | `submit`, `get_status`, `delete`, `get_article`, `batchget` | 发布能力 |
| `material` | `get`, `delete`, `count`, `batchget` | 永久素材 |
| `user` | `get_list`, `get_info`, `update_remark` | 用户管理 |
| `comment` | `open`, `close`, `list`, `markelect`, `unmarkelect`, `delete`, `reply`, `delete_reply` | 留言管理 |
| `message` | `send_custom`, `send_mass` | 消息与群发 |
| `kf` | `add`, `get_list` | 客服管理 |
| `analysis` | `get_article_summary`, `get_user_summary` | 数据统计 |

### 调用示例

```python
from src.skills.wechat_capability_skill import wechat_manage_capability

# 保存草稿
result = wechat_manage_capability(
    app_id="wx1234567890abcdef",
    app_secret="your_app_secret_here",
    capability="draft",
    action="add",
    articles=[{
        "title": "文章标题",
        "content": "<p>HTML内容...</p>",
        "thumb_media_id": "media_id"
    }]
)

# 获取用户列表
result = wechat_manage_capability(
    app_id="wx1234567890abcdef",
    app_secret="your_app_secret_here",
    capability="user",
    action="get_list",
    next_openid=""
)

# 创建菜单
result = wechat_manage_capability(
    app_id="wx1234567890abcdef",
    app_secret="your_app_secret_here",
    capability="menu",
    action="create",
    menu_data={"button": [...]}
)
```

### 错误处理

函数返回字典包含 `errcode` 和 `errmsg`：
- `errcode == 0`: 请求成功
- `errcode != 0`: 请求失败，查看 `errmsg` 了解原因

常见错误码：
- `40001`: access_token 无效或已过期
- `40013`: AppID 不合法
- `40125`: AppSecret 错误
- `48001`: API 未授权（需要认证）

---

## 2. 内容优化技能

**文件**: `src/skills/content_optimizer.py`

### 函数签名
```python
humanize_text(text: str, intensity: float = 0.7) -> str
```

### 功能
去除 AI 生成内容的常见痕迹，使文本更自然、更有的人文气息。

### 参数
- `text`: 原始文本
- `intensity`: 优化强度 (0.0-1.0)，默认 0.7

### 优化策略
1. **词汇替换**：首先→一开始、然而→但是、因此→所以
2. **情感增强**：添加"说实话"、"其实"、"没想到"等情感词
3. **个人视角**：添加"我觉得"、"以我的经验"等个人化表达
4. **打破完美**：添加口语化停顿（——、…、"那个，"）

### 调用示例

```python
from src.skills.content_optimizer import humanize_text

original = """
首先，我们需要理解这个概念。其次，我们要分析其应用场景。
综上所述，这项技术具有非常重要的意义。
"""

optimized = humanize_text(original, intensity=0.8)
# 输出更自然的文本
```

---

## 3. HTML 优化技能

**文件**: `src/skills/html_optimizer.py`

### 函数签名

```python
# 压缩 HTML
compress_html(html_content: str, remove_comments: bool = True) -> str

# 检查 HTML 兼容性
check_html_for_wechat(html_content: str) -> dict
```

### 功能
- `compress_html`: 压缩 HTML 内容，移除注释、空格，优化内联样式
- `check_html_for_wechat`: 检查 HTML 是否适合微信公众号，报告潜在问题

### check_html_for_wechat 返回值
```python
{
    "is_valid": bool,           # 是否有效
    "compression_ratio": float, # 压缩率
    "size_original": int,       # 原始大小
    "size_compressed": int,     # 压缩后大小
    "warnings": {               # 警告统计
        "info": int,
        "warning": int,
        "error": int,
        "critical": int
    },
    "has_errors": bool          # 是否有错误
}
```

### 调用示例

```python
from src.skills.html_optimizer import compress_html, check_html_for_wechat

html = """
<!-- 注释 -->
<p style="color: red; ">Hello</p>
"""

# 压缩
compressed = compress_html(html)
# 输出: <p style="color:red">Hello</p>

# 检查
result = check_html_for_wechat(html)
print(result["is_valid"])  # True/False
print(result["warnings"])   # 警告统计
```

### 微信公众号不支持的标签
`script`, `iframe`, `embed`, `object`, `form`, `input`, `textarea`, `select`, `button`, `canvas`, `svg`, `video`, `audio`

---

## 4. 主题加载技能

**文件**: `src/skills/wechat_formatter_skill.py`

### 类和方法
```python
from src.skills.wechat_formatter_skill import ThemeLoader

# 加载主题
config = ThemeLoader.load_theme("macaron/blue")
# 或
config = ThemeLoader.load_theme("blue")  # 会在所有分类中查找

# 清除缓存
ThemeLoader.clear_cache()

# 查看缓存状态
cache_info = ThemeLoader.get_cache_info()
```

### 主题路径格式
- `'default'` → `themes/default.yaml` (category: default)
- `'macaron/blue'` → `themes/macaron/blue.yaml` (category: macaron)
- `'wenyan'` → 查找 `themes/wenyan/*.yaml`

### 返回的 ThemeConfig 结构
```python
{
    "name": "马卡龙蓝",
    "category": "macaron",
    "colors": {"primary": "#..."},
    "body": {...},
    "h1": {...},
    "h2": {...},
    # ... 其他样式
}
```

---

## ⚠️ 使用注意事项

### 1. 凭证安全
调用 `wechat_manage_capability` 必须提供真实的 `app_id` 和 `app_secret`。切勿使用占位符发起真实请求。

### 2. 认证权限
许多高级功能需要已认证的公众号才能使用：
- **需要认证**：用户管理、发布能力、客服管理、高级群发、数据统计、留言管理
- **无需认证**：草稿箱、永久素材（上传/获取）

### 3. 确认机制
执行以下操作前建议先向用户确认：
- 删除菜单、删除已发布文章
- 正式发布操作 (`publish` -> `submit`)

### 4. 错误处理
如果 API 返回错误（例如 `errcode != 0`），请解析错误信息并向用户解释原因。

---

## 🔧 依赖安装

```bash
pip install requests pyyaml
```
