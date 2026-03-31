import requests
import json
import time
import random
import re
import os
from typing import Dict, List, Optional, Any, Union
from functools import wraps

# 可选的 HTML 解析库
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# 导入 OpenClaw 兼容模块
try:
    from .openclaw_compat import skill_info, SkillException, Input
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from openclaw_compat import skill_info, SkillException, Input

# 导入 Markdown 转换模块
try:
    from .markdown_to_wechat_converter import convert_markdown_to_wechat_html, is_markdown
except ImportError:
    try:
        from markdown_to_wechat_converter import convert_markdown_to_wechat_html, is_markdown
    except ImportError:
        convert_markdown_to_wechat_html = None
        is_markdown = None

# ==========================================
# 微信文章内容验证与清理工具函数
# ==========================================

# 微信支持的 HTML 标签白名单
ALLOWED_TAGS = {
    'p', 'br', 'span', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u',
    'ul', 'ol', 'li',
    'blockquote',
    'pre', 'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'section', 'div',
    'mp-common-miniprogram',  # 微信小程序卡片
}

# 需要移除的危险标签和属性
FORBIDDEN_TAGS = {'script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select', 'button', 'canvas', 'svg', 'video', 'audio'}
FORBIDDEN_ATTRS = {'onerror', 'onclick', 'onload', 'onmouseover', 'onfocus', 'onblur', 'onchange', 'onsubmit', 'javascript:', 'vbscript:', 'data:'}

# 微信图文消息限制
MAX_CONTENT_LENGTH = 20000  # 2万字符
MAX_CONTENT_SIZE = 1024 * 1024  # 1MB


def sanitize_html_for_wechat(html_content: str) -> str:
    """
    清理 HTML 内容，移除微信不支持的标签和属性
    
    Args:
        html_content: 原始 HTML 内容
        
    Returns:
        清理后的 HTML 内容
    """
    from bs4 import BeautifulSoup
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除危险标签
        for tag in soup.find_all(FORBIDDEN_TAGS):
            tag.decompose()
        
        # 移除危险属性
        for tag in soup.find_all(True):
            attrs = list(tag.attrs.keys())
            for attr in attrs:
                # 检查属性名是否危险
                attr_lower = attr.lower()
                if any(dangerous in attr_lower for dangerous in FORBIDDEN_ATTRS):
                    del tag[attr]
                # 检查属性值是否危险
                attr_value = str(tag.get(attr, '')).lower()
                if any(dangerous in attr_value for dangerous in FORBIDDEN_ATTRS):
                    del tag[attr]
        
        # 移除空的 style 属性
        for tag in soup.find_all(True):
            if tag.get('style') and not tag['style'].strip():
                del tag['style']
        
        return str(soup)
    except Exception:
        # 如果解析失败，做简单的正则清理
        result = html_content
        for tag in FORBIDDEN_TAGS:
            result = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', result, flags=re.DOTALL | re.IGNORECASE)
            result = re.sub(f'<{tag}[^>]*/?>', '', result, flags=re.IGNORECASE)
        return result


def validate_article_content(content: str) -> dict:
    """
    验证图文消息内容是否符合微信限制
    
    Args:
        content: HTML 内容
        
    Returns:
        验证结果字典:
        - valid: bool, 是否有效
        - char_count: int, 字符数
        - byte_size: int, 字节大小
        - warnings: list, 警告信息
        - errors: list, 错误信息
    """
    warnings = []
    errors = []
    
    # 统计字符数（不含 HTML 标签）
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text()
    except Exception:
        # 如果解析失败，简单去除标签
        text_content = re.sub(r'<[^>]+>', '', content)
    
    char_count = len(text_content)
    byte_size = len(content.encode('utf-8'))
    
    # 检查字符数
    if char_count > MAX_CONTENT_LENGTH:
        errors.append(f"内容字符数超限: {char_count} > {MAX_CONTENT_LENGTH}")
    elif char_count > MAX_CONTENT_LENGTH * 0.9:
        warnings.append(f"内容字符数接近上限: {char_count}/{MAX_CONTENT_LENGTH}")
    
    # 检查大小
    if byte_size > MAX_CONTENT_SIZE:
        errors.append(f"内容大小超限: {byte_size} > {MAX_CONTENT_SIZE}")
    
    # 检查是否有本地图片路径
    local_image_pattern = r'src=["\']?(?!https?://)(?!data:)(?!/)["\'  ]*(\.jpg|\.jpeg|\.png|\.gif|\.webp)'
    if re.search(local_image_pattern, content, re.IGNORECASE):
        warnings.append("发现本地图片路径，上传前需要替换为微信素材 URL")
    
    # 检查是否有外部图片（非微信域名）
    external_image_pattern = r'src=["\'](https?://(?!mmbiz\.qpic\.cn)[^"\']+)["\']'
    external_matches = re.findall(external_image_pattern, content)
    if external_matches:
        warnings.append(f"发现 {len(external_matches)} 个外部图片 URL，会被微信过滤，需要先上传到微信素材库")
    
    return {
        "valid": len(errors) == 0,
        "char_count": char_count,
        "byte_size": byte_size,
        "warnings": warnings,
        "errors": errors,
        "max_chars": MAX_CONTENT_LENGTH,
        "max_size": MAX_CONTENT_SIZE
    }


def replace_image_urls_with_wechat(
    html_content: str,
    image_uploader,  # WeChatCapabilityManager 实例
    upload_local: bool = True
) -> dict:
    """
    替换 HTML 中的图片 URL 为微信素材 URL
    
    Args:
        html_content: HTML 内容
        image_uploader: WeChatCapabilityManager 实例，用于上传图片
        upload_local: 是否上传本地图片，默认 True
        
    Returns:
        dict: {
            "html": 替换后的 HTML,
            "replaced": list, 替换记录 [{"original": ..., "new": ..., "success": bool}],
            "errors": list, 错误信息
        }
    """
    from bs4 import BeautifulSoup
    
    replaced = []
    errors = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        return {
            "html": html_content,
            "replaced": [],
            "errors": [f"HTML 解析失败: {str(e)}"]
        }
    
    for img in soup.find_all('img'):
        original_url = img.get('src', '')
        if not original_url:
            continue
        
        # 跳过已经是微信图片的 URL
        if 'mmbiz.qpic.cn' in original_url:
            continue
        
        # 跳过 data URI
        if original_url.startswith('data:'):
            continue
        
        # 跳过空 URL
        if not original_url.strip():
            continue
        
        # 上传图片
        upload_result = image_uploader.upload_article_image(original_url)
        
        if upload_result.get('errcode') == 0 or 'url' in upload_result:
            new_url = upload_result.get('url', '')
            img['src'] = new_url
            replaced.append({
                "original": original_url,
                "new": new_url,
                "success": True
            })
        else:
            errors.append(f"上传图片失败 [{original_url}]: {upload_result.get('errmsg', '未知错误')}")
            replaced.append({
                "original": original_url,
                "new": original_url,
                "success": False,
                "error": upload_result.get('errmsg', '未知错误')
            })
    
    return {
        "html": str(soup),
        "replaced": replaced,
        "errors": errors
    }


# ==========================================
# 自定义异常类（继承自 OpenClaw 基类）
# ==========================================
class WeChatAPIError(SkillException):
    """微信公众号 API 错误"""
    def __init__(self, errcode: int, errmsg: str, endpoint: str = ""):
        self.errcode = errcode
        self.errmsg = errmsg
        self.endpoint = endpoint
        message = f"微信 API 错误 [{errcode}]: {errmsg} (endpoint: {endpoint})"
        super().__init__(message, error_code=f"WECHAT_{errcode}", details={"errmsg": errmsg, "endpoint": endpoint})

class NetworkError(SkillException):
    """网络请求错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="NETWORK_ERROR", details=details)

class ValidationError(SkillException):
    """参数验证错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)

class TokenExpiredError(SkillException):
    """Access Token 过期"""
    def __init__(self, message: str = "Access token 已过期"):
        super().__init__(message, error_code="TOKEN_EXPIRED")

# ==========================================
# 装饰器：指数退避重试
# ==========================================
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
    """指数退避重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, NetworkError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # 计算指数退避延迟（添加随机抖动）
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        time.sleep(delay)
            raise NetworkError(f"在 {max_retries} 次重试后仍然失败: {last_exception}")
        return wrapper
    return decorator

# ==========================================
# 输入验证工具函数
# ==========================================
def validate_string(value: Any, field_name: str, min_length: int = 1, max_length: int = None) -> str:
    """验证字符串参数"""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} 必须是字符串类型，当前类型: {type(value).__name__}")
    if len(value) < min_length:
        raise ValidationError(f"{field_name} 长度不能小于 {min_length}")
    if max_length and len(value) > max_length:
        raise ValidationError(f"{field_name} 长度不能超过 {max_length}")
    return value

def validate_not_empty(value: Any, field_name: str) -> Any:
    """验证非空值"""
    if value is None or (isinstance(value, (str, list, dict)) and len(value) == 0):
        raise ValidationError(f"{field_name} 不能为空")
    return value

@skill_info(
    name="wechat_capability_manager",
    description="微信公众号能力管理 API 客户端，支持自定义菜单、草稿箱、发布能力、素材管理、用户管理、留言管理等功能",
    version="2.0.0",
    author="OpenClaw Skill Team",
    tags=["wechat", "api", "management", "official-account"],
    inputs={
        "app_id": Input(str, "微信公众号 AppID", required=True, example="wx1234567890abcdef"),
        "app_secret": Input(str, "微信公众号 AppSecret", required=True, example="1234567890abcdef1234567890abcdef"),
        "max_retries": Input(int, "最大重试次数", required=False, default=3, example=3)
    }
)
@skill_info(
    name="wechat_capability",
    description="微信公众号能力管理 API 客户端，支持自定义菜单、草稿箱、发布能力、素材管理、用户管理、留言管理等功能",
    version="2.0.0",
    author="OpenClaw Team",
    tags=["wechat", "official_account", "api", "management"],
    icon="📱"
)
class WeChatCapabilityManager:
    """微信公众号能力管理 API 客户端（鲁棒性增强版）"""
    
    # Token 过期错误码
    TOKEN_EXPIRED_CODES = {40001, 40014, 42001, 40028}
    
    def __init__(self, app_id: str, app_secret: str, max_retries: int = 3):
        # 输入验证
        self.app_id = validate_string(app_id, "app_id", min_length=1, max_length=128)
        self.app_secret = validate_string(app_secret, "app_secret", min_length=1, max_length=128)
        self.access_token: Optional[str] = None
        self.max_retries = max_retries
        
    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
    def get_access_token(self) -> str:
        """获取 access_token（带重试机制）"""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            raise NetworkError("获取 access_token 超时，请检查网络连接")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"无法连接到微信服务器: {e}")
        except requests.exceptions.HTTPError as e:
            raise WeChatAPIError(-1, f"HTTP 错误: {e}", endpoint="/token")
        except json.JSONDecodeError as e:
            raise WeChatAPIError(-1, f"无效的 JSON 响应: {e}", endpoint="/token")
        
        if "access_token" in data:
            self.access_token = data["access_token"]
            return self.access_token
        
        # 处理微信返回的错误
        errcode = data.get("errcode", -1)
        errmsg = data.get("errmsg", "未知错误")
        raise WeChatAPIError(errcode, errmsg, endpoint="/token")

    # 微信错误码映射表
    WECHAT_ERROR_CODES = {
        -1: "系统繁忙，请稍后再试",
        0: "请求成功",
        40001: "access_token 已过期或无效",
        40002: "不合法的凭证类型",
        40003: "不合法的 OpenID",
        40004: "不合法的媒体文件类型",
        40005: "不合法的文件类型",
        40006: "不合法的文件大小",
        40007: "不合法的媒体文件 id",
        40008: "不合法的消息类型",
        40009: "不合法的图片文件大小",
        40010: "不合法的语音文件大小",
        40011: "不合法的视频文件大小",
        40012: "不合法的缩略图文件大小",
        40013: "不合法的 AppID",
        40014: "不合法的 access_token",
        40015: "不合法的菜单类型",
        40016: "不合法的按钮个数",
        40017: "不合法的按钮类型",
        40018: "不合法的按钮名字长度",
        40019: "不合法的按钮 KEY 长度",
        40020: "不合法的按钮 URL 长度",
        40021: "不合法的菜单版本号",
        40022: "不合法的子菜单级数",
        40023: "不合法的子菜单按钮个数",
        40024: "不合法的子菜单按钮类型",
        40025: "不合法的子菜单按钮名字长度",
        40026: "不合法的子菜单按钮 KEY 长度",
        40027: "不合法的子菜单按钮 URL 长度",
        40028: "不合法的自定义菜单使用用户",
        40029: "不合法的 oauth_code",
        40030: "不合法的 refresh_token",
        40031: "不合法的 openid 列表",
        40032: "不合法的 openid 列表长度",
        40033: "不合法的请求字符",
        40035: "不合法的参数",
        40038: "不合法的请求格式",
        40039: "不合法的 URL 长度",
        40048: "不合法的 url 域名",
        40050: "不合法的 article_tag 标签",
        40051: "不合法的 article_tag 标签长度",
        40060: "不合法的 article_id",
        40061: "不合法的 article_id 数量",
        41001: "缺少 access_token 参数",
        41002: "缺少 appid 参数",
        41003: "缺少 refresh_token 参数",
        41004: "缺少 secret 参数",
        41005: "缺少多媒体文件数据",
        41006: "缺少 media_id 参数",
        41007: "缺少子菜单数据",
        41008: "缺少 oauth code",
        41009: "缺少 openid",
        42001: "access_token 超时",
        42002: "refresh_token 超时",
        43001: "需要 GET 请求",
        43002: "需要 POST 请求",
        43003: "需要 HTTPS 请求",
        43004: "需要接收者关注",
        43005: "需要好友关系",
        44001: "多媒体文件为空",
        44002: "POST 的数据包为空",
        44003: "图文消息内容为空",
        44004: "文本消息内容为空",
        45001: "多媒体文件大小超过限制",
        45002: "消息内容超过限制",
        45003: "标题字段超过限制",
        45004: "描述字段超过限制",
        45005: "链接字段超过限制",
        45006: "图片链接字段超过限制",
        45007: "语音播放时间超过限制",
        45008: "图文消息超过限制",
        45009: "接口调用超过频率限制",
        45010: "创建菜单个数超过限制",
        45015: "回复时间超过限制",
        45016: "系统分组，不允许修改",
        45017: "分组名字过长",
        45018: "分组数量超过上限",
        45047: "客服接口下行条数超过上限",
        45064: "创建菜单包含未关联的小程序",
        45065: "同样错误的请求过于频繁",
        45072: "content 字段超过长度限制",
        45073: "媒体文件大小超过限制",
        45074: "请求地址不是 mp.weixin.qq.com",
        45075: "图片大小超过限制",
        45076: "草稿箱数量超过限制",
        46001: "不存在媒体数据",
        46002: "不存在的菜单版本",
        46003: "不存在的菜单数据",
        46004: "不存在的用户",
        46005: "草稿不存在",
        47001: "解析 JSON/XML 内容错误",
        48001: "api 未授权",
        48002: "api 禁止",
        48003: "接口无权限",
        48004: "api 的传入 json 无效",
        48005: "api 接口需要 post 请求",
        48006: "api 接口需要 get 请求",
        48008: "api 传入参数不正确",
        50001: "用户未授权该 api",
        50002: "用户受限",
        50003: "用户未关注公众号",
        50004: "用户被加入黑名单",
        50005: "用户被限制",
        50006: "用户未绑定微信",
        61000: "请求参数错误",
        61001: "access_token 无效",
        61002: "refresh_token 无效",
        61003: "appid 无效",
        61004: "openid 无效",
        61005: "appsecret 无效",
        61006: "grant_type 无效",
        61007: "code 无效",
        61008: "refresh_token 过期",
        61009: "access_token 过期",
        61010: "access_token 无效",
        61011: "appid 不匹配",
        61012: "refresh_token 无效",
        61013: "openid 无效",
        61014: "appsecret 无效",
        61015: "grant_type 无效",
        61016: "code 无效",
        61017: "refresh_token 过期",
        61018: "access_token 过期",
        61019: "access_token 无效",
        61020: "appid 不匹配",
    }

    def __init__(self, app_id: str, app_secret: str, max_retries: int = 3):
        # 输入验证
        self.app_id = validate_string(app_id, "app_id", min_length=1, max_length=128)
        self.app_secret = validate_string(app_secret, "app_secret", min_length=1, max_length=128)
        self.access_token: Optional[str] = None
        self.max_retries = max_retries
        
    @retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
    def get_access_token(self) -> str:
        """获取 access_token（带重试机制）"""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            raise NetworkError("获取 access_token 超时，请检查网络连接")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"无法连接到微信服务器: {e}")
        except requests.exceptions.HTTPError as e:
            raise WeChatAPIError(-1, f"HTTP 错误: {e}", endpoint="/token")
        except json.JSONDecodeError as e:
            raise WeChatAPIError(-1, f"无效的 JSON 响应: {e}", endpoint="/token")
        
        if "access_token" in data:
            self.access_token = data["access_token"]
            return self.access_token
        
        # 处理微信返回的错误
        errcode = data.get("errcode", -1)
        errmsg = data.get("errmsg", "未知错误")
        raise WeChatAPIError(errcode, errmsg, endpoint="/token")

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None, retry_on_token_expired: bool = True) -> dict:
        """通用请求方法（鲁棒性增强版）
        
        支持自动 Token 刷新、指数退避重试、错误码映射
        """
        # 确保有 access_token
        if not self.access_token:
            self.get_access_token()
        
        # 构建 URL 和参数
        url = f"https://api.weixin.qq.com{endpoint}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        # 执行请求（带重试）
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, timeout=10)
                else:
                    payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
                    response = requests.post(
                        url, 
                        params=params, 
                        data=payload, 
                        headers={'Content-Type': 'application/json'}, 
                        timeout=10
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # 检查微信错误码
                errcode = result.get('errcode', 0)
                if errcode != 0:
                    # Token 过期，尝试刷新并重试
                    if errcode in self.TOKEN_EXPIRED_CODES and retry_on_token_expired and attempt < self.max_retries - 1:
                        self.get_access_token()
                        params['access_token'] = self.access_token
                        continue
                    
                    # 其他错误，抛出异常
                    errmsg = result.get('errmsg', self.WECHAT_ERROR_CODES.get(errcode, '未知错误'))
                    raise WeChatAPIError(errcode, errmsg, endpoint=endpoint)
                
                return result
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = min(2 ** attempt + random.uniform(0, 1), 10)
                    time.sleep(delay)
                continue
            except WeChatAPIError:
                raise
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    continue
                break
        
        # 所有重试都失败了
        if isinstance(last_exception, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
            raise NetworkError(f"在 {self.max_retries} 次重试后仍然无法连接到微信服务器: {last_exception}")
        raise WeChatAPIError(-1, f"请求失败: {last_exception}", endpoint=endpoint)

    # ==========================================
    # 1. 自定义菜单管理 (Custom Menu)
    # ==========================================
    def create_menu(self, menu_data: dict) -> dict:
        """创建自定义菜单"""
        return self._request('POST', '/cgi-bin/menu/create', data=menu_data)
        
    def get_menu(self) -> dict:
        """查询自定义菜单"""
        return self._request('GET', '/cgi-bin/menu/get')
        
    def delete_menu(self) -> dict:
        """删除自定义菜单"""
        return self._request('GET', '/cgi-bin/menu/delete')

    # ==========================================
    # 2. 草稿箱管理 (Draft Management)
    # ==========================================
    def add_draft(self, articles: List[dict]) -> dict:
        """新建草稿"""
        return self._request('POST', '/cgi-bin/draft/add', data={"articles": articles})
        
    def get_draft(self, media_id: str) -> dict:
        """获取草稿"""
        return self._request('POST', '/cgi-bin/draft/get', data={"media_id": media_id})
        
    def delete_draft(self, media_id: str) -> dict:
        """删除草稿"""
        return self._request('POST', '/cgi-bin/draft/delete', data={"media_id": media_id})
        
    def update_draft(self, media_id: str, index: int, article: dict) -> dict:
        """修改草稿"""
        data = {
            "media_id": media_id,
            "index": index,
            "articles": article
        }
        return self._request('POST', '/cgi-bin/draft/update', data=data)
        
    def get_draft_count(self) -> dict:
        """获取草稿总数"""
        return self._request('GET', '/cgi-bin/draft/count')
        
    def batch_get_draft(self, offset: int = 0, count: int = 20, no_content: int = 0) -> dict:
        """获取草稿列表"""
        data = {
            "offset": offset,
            "count": count,
            "no_content": no_content
        }
        return self._request('POST', '/cgi-bin/draft/batchget', data=data)

    # ==========================================
    # 3. 发布能力 (Publish Management)
    # ==========================================
    def submit_publish(self, media_id: str) -> dict:
        """发布接口"""
        return self._request('POST', '/cgi-bin/freepublish/submit', data={"media_id": media_id})
        
    def get_publish_status(self, publish_id: str) -> dict:
        """发布状态轮询接口"""
        return self._request('POST', '/cgi-bin/freepublish/get', data={"publish_id": publish_id})
        
    def delete_publish(self, article_id: str, index: int = 0) -> dict:
        """删除发布"""
        data = {
            "article_id": article_id,
            "index": index
        }
        return self._request('POST', '/cgi-bin/freepublish/delete', data=data)
        
    def get_publish_article(self, article_id: str) -> dict:
        """通过 article_id 获取已发布文章"""
        return self._request('POST', '/cgi-bin/freepublish/getarticle', data={"article_id": article_id})
        
    def batch_get_publish(self, offset: int = 0, count: int = 20, no_content: int = 0) -> dict:
        """获取成功发布列表"""
        data = {
            "offset": offset,
            "count": count,
            "no_content": no_content
        }
        return self._request('POST', '/cgi-bin/freepublish/batchget', data=data)

    # ==========================================
    # 4. 素材管理 (Asset Management)
    # ==========================================
    def get_material(self, media_id: str) -> dict:
        """获取永久素材"""
        return self._request('POST', '/cgi-bin/material/get_material', data={"media_id": media_id})
        
    def delete_material(self, media_id: str) -> dict:
        """删除永久素材"""
        return self._request('POST', '/cgi-bin/material/del_material', data={"media_id": media_id})
        
    def get_material_count(self) -> dict:
        """获取素材总数"""
        return self._request('GET', '/cgi-bin/material/get_materialcount')
        
    def batch_get_material(self, type: str, offset: int = 0, count: int = 20) -> dict:
        """获取素材列表 (type: image, video, voice, news)"""
        data = {
            "type": type,
            "offset": offset,
            "count": count
        }
        return self._request('POST', '/cgi-bin/material/batchget_material', data=data)
    
    # ==========================================
    # 4.5 图文消息内的图片上传 (Image Upload for Article Content)
    # ==========================================
    def upload_article_image(self, image_path: str) -> dict:
        """
        上传图文消息内的图片获取 URL
        
        重要：微信要求文章内容中的图片必须通过此接口上传，
        外部图片 URL 会被微信过滤导致显示异常。
        
        Args:
            image_path: 图片文件路径（本地路径或 URL）
            
        Returns:
            dict: 包含 url 字段，如 {"url": "https://mmbiz.qpic.cn/..."}
        """
        import os
        import re
        
        # 检查是否是 URL
        if re.match(r'^https?://', image_path):
            # 是 URL，检查是否是微信域名
            if 'mmbiz.qpic.cn' in image_path:
                # 已经是微信图片，直接返回
                return {"url": image_path, "media_id": None}
            else:
                # 外部 URL，需要下载后上传
                try:
                    import requests as req
                    response = req.get(image_path, timeout=10)
                    if response.status_code == 200:
                        # 创建临时文件
                        import tempfile
                        suffix = os.path.splitext(image_path)[1] or '.jpg'
                        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                            f.write(response.content)
                            temp_path = f.name
                        try:
                            return self._upload_local_image(temp_path)
                        finally:
                            os.unlink(temp_path)
                    else:
                        return {"errcode": -1, "errmsg": f"下载外部图片失败: {response.status_code}"}
                except Exception as e:
                    return {"errcode": -1, "errmsg": f"处理外部图片失败: {str(e)}"}
        else:
            # 本地文件
            return self._upload_local_image(image_path)
    
    def _upload_local_image(self, image_path: str) -> dict:
        """上传本地图片到微信素材库"""
        import os
        
        if not os.path.exists(image_path):
            return {"errcode": -1, "errmsg": f"图片文件不存在: {image_path}"}
        
        # 检查文件大小（不超过 2MB）
        file_size = os.path.getsize(image_path)
        if file_size > 2 * 1024 * 1024:
            return {"errcode": -1, "errmsg": f"图片文件过大: {file_size} bytes，最大 2MB"}
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                url = f"https://api.weixin.qq.com/cgi-bin/media/upload"
                params = {'access_token': self.access_token, 'type': 'image'}
                
                response = requests.post(url, params=params, files=files, timeout=30)
                result = response.json()
                
                if result.get('errcode') == 0:
                    # 成功，返回 url
                    return {
                        "url": result.get('url', ''),
                        "media_id": result.get('media_id', '')
                    }
                else:
                    return result
        except Exception as e:
            return {"errcode": -1, "errmsg": f"上传图片失败: {str(e)}"}
    
    def upload_article_image_from_data(self, image_data: bytes, filename: str = "image.jpg") -> dict:
        """
        从二进制数据上传图片
        
        Args:
            image_data: 图片的二进制数据
            filename: 文件名
            
        Returns:
            dict: 包含 url 字段
        """
        try:
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                f.write(image_data)
                temp_path = f.name
            try:
                return self._upload_local_image(temp_path)
            finally:
                os.unlink(temp_path)
        except Exception as e:
            return {"errcode": -1, "errmsg": f"上传图片失败: {str(e)}"}

    # ==========================================
    # 5. 用户管理 (User Management)
    # ==========================================
    def get_user_list(self, next_openid: str = "") -> dict:
        """获取用户列表"""
        params = {"next_openid": next_openid} if next_openid else {}
        return self._request('GET', '/cgi-bin/user/get', params=params)
        
    def get_user_info(self, openid: str, lang: str = "zh_CN") -> dict:
        """获取用户基本信息"""
        params = {"openid": openid, "lang": lang}
        return self._request('GET', '/cgi-bin/user/info', params=params)
        
    def update_user_remark(self, openid: str, remark: str) -> dict:
        """设置用户备注名"""
        data = {"openid": openid, "remark": remark}
        return self._request('POST', '/cgi-bin/user/info/updateremark', data=data)

    # ==========================================
    # 6. 留言管理 (Comments Management)
    # ==========================================
    def open_comment(self, msg_data_id: int, index: int = 0) -> dict:
        """打开已群发文章留言"""
        data = {"msg_data_id": msg_data_id, "index": index}
        return self._request('POST', '/cgi-bin/comment/open', data=data)
        
    def close_comment(self, msg_data_id: int, index: int = 0) -> dict:
        """关闭已群发文章留言"""
        data = {"msg_data_id": msg_data_id, "index": index}
        return self._request('POST', '/cgi-bin/comment/close', data=data)
        
    def get_comment_list(self, msg_data_id: int, index: int = 0, begin: int = 0, count: int = 50, type: int = 0) -> dict:
        """查看指定文章的留言数据 (type: 0普通, 1精选)"""
        data = {
            "msg_data_id": msg_data_id,
            "index": index,
            "begin": begin,
            "count": count,
            "type": type
        }
        return self._request('POST', '/cgi-bin/comment/list', data=data)
        
    def mark_elect_comment(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """将留言标记精选"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/markelect', data=data)
        
    def unmark_elect_comment(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """将留言取消精选"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/unmarkelect', data=data)
        
    def delete_comment(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """删除留言"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/delete', data=data)
        
    def reply_comment(self, msg_data_id: int, index: int, user_comment_id: int, content: str) -> dict:
        """回复留言"""
        data = {
            "msg_data_id": msg_data_id,
            "index": index,
            "user_comment_id": user_comment_id,
            "content": content
        }
        return self._request('POST', '/cgi-bin/comment/reply/add', data=data)
        
    def delete_reply(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """删除回复"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/reply/delete', data=data)

    # ==========================================
    # 7. 基础消息与群发 (Basic Messages & Batch Sends)
    # ==========================================
    def send_custom_message(self, touser: str, msgtype: str, **kwargs) -> dict:
        """发送客服消息 (被动回复之外的普通消息)"""
        data = {"touser": touser, "msgtype": msgtype}
        data.update(kwargs)
        return self._request('POST', '/cgi-bin/message/custom/send', data=data)
        
    def send_mass_message(self, filter_is_to_all: bool, filter_tag_id: int, msgtype: str, **kwargs) -> dict:
        """根据标签进行群发"""
        data = {
            "filter": {"is_to_all": filter_is_to_all, "tag_id": filter_tag_id},
            "msgtype": msgtype
        }
        data.update(kwargs)
        return self._request('POST', '/cgi-bin/message/mass/sendall', data=data)

    # ==========================================
    # 8. 客服管理 (Customer Service)
    # ==========================================
    def add_kf_account(self, kf_account: str, nickname: str, password: str) -> dict:
        """添加客服账号"""
        data = {"kf_account": kf_account, "nickname": nickname, "password": password}
        return self._request('POST', '/customservice/kfaccount/add', data=data)
        
    def get_kf_list(self) -> dict:
        """获取所有客服账号"""
        return self._request('GET', '/cgi-bin/customservice/getkflist')

    # ==========================================
    # 9. 数据统计 (Data Statistics)
    # ==========================================
    def get_article_summary(self, begin_date: str, end_date: str) -> dict:
        """获取图文群发每日数据"""
        data = {"begin_date": begin_date, "end_date": end_date}
        return self._request('POST', '/datacube/getarticlesummary', data=data)
        
    def get_user_summary(self, begin_date: str, end_date: str) -> dict:
        """获取用户增减数据"""
        data = {"begin_date": begin_date, "end_date": end_date}
        return self._request('POST', '/datacube/getusersummary', data=data)

# ==========================================
# 草稿箱 Markdown 自动转换辅助函数
# ==========================================

def _process_draft_articles(
    articles: List[dict],
    theme_name: str = "default",
    themes_dir: str = "./themes",
    auto_upload_images: bool = True,
    manager = None  # WeChatCapabilityManager instance for image upload
) -> List[dict]:
    """
    处理草稿文章列表，自动将 Markdown 内容转换为 HTML，并验证内容
    
    Args:
        articles: 文章列表，每篇文章包含 title, content 等字段
        theme_name: 主题名称，用于 Markdown 转换
        themes_dir: 主题文件目录
        auto_upload_images: 是否自动上传图片（默认 True）
        manager: WeChatCapabilityManager 实例，用于上传图片
        
    Returns:
        处理后的文章列表，包含以下增强字段:
        - content: HTML 内容（已转换）
        - _validation: 验证结果
        - _image_replacement: 图片替换记录
    """
    if not articles:
        return articles
    
    processed_articles = []
    
    for idx, article in enumerate(articles):
        processed_article = article.copy()
        
        # 1. Markdown 转 HTML
        if "content" in processed_article and isinstance(processed_article["content"], str):
            content = processed_article["content"].strip()
            
            # 如果内容是 Markdown 且不是 HTML 标签，则进行转换
            if convert_markdown_to_wechat_html and is_markdown and is_markdown(content) and not content.startswith("<"):
                try:
                    article_theme = processed_article.get("theme", theme_name)
                    html_content = convert_markdown_to_wechat_html(
                        markdown_content=content,
                        theme_name=article_theme,
                        themes_dir=themes_dir
                    )
                    processed_article["content"] = html_content
                    processed_article["_converted_from_markdown"] = True
                    processed_article["_theme_used"] = article_theme
                except Exception as e:
                    processed_article["_conversion_error"] = str(e)
                    continue
            
            # 2. HTML 清理（移除危险标签和属性）
            if processed_article["content"].startswith("<"):
                try:
                    processed_article["content"] = sanitize_html_for_wechat(processed_article["content"])
                except Exception as e:
                    processed_article["_sanitization_error"] = str(e)
            
            # 3. 内容验证
            validation_result = validate_article_content(processed_article["content"])
            processed_article["_validation"] = validation_result
            
            if not validation_result["valid"]:
                processed_article["_validation_errors"] = validation_result["errors"]
            
            # 4. 图片 URL 替换（如果提供 manager）
            if auto_upload_images and manager and '<img' in processed_article["content"]:
                try:
                    # 检查是否有需要替换的图片
                    has_external_images = bool(re.search(
                        r'src=["\'](https?://(?!mmbiz\.qpic\.cn)[^"\']+)["\']',
                        processed_article["content"]
                    ))
                    has_local_images = bool(re.search(
                        r'src=["\']?(?!https?://)(?!data:)(?!/)["\'  ]*(\.jpg|\.jpeg|\.png|\.gif|\.webp)',
                        processed_article["content"],
                        re.IGNORECASE
                    ))
                    
                    if has_external_images or has_local_images:
                        replacement_result = replace_image_urls_with_wechat(
                            processed_article["content"],
                            manager,
                            upload_local=True
                        )
                        processed_article["content"] = replacement_result["html"]
                        processed_article["_image_replacement"] = replacement_result["replaced"]
                        if replacement_result["errors"]:
                            processed_article["_image_errors"] = replacement_result["errors"]
                except Exception as e:
                    processed_article["_image_replacement_error"] = str(e)
        
        processed_articles.append(processed_article)
    
    return processed_articles


# ==========================================
# 独立的 Markdown 转 HTML 技能函数
# ==========================================

@skill_info(
    name="format_markdown_to_wechat_html",
    description="将 Markdown 文本转换为微信公众号兼容的带内联样式 HTML，支持多主题定制",
    version="1.0.0",
    author="WeChat Skill Team",
    tags=["wechat", "markdown", "html", "排版", "转换"],
    inputs={
        "markdown_content": Input(str, "要转换的 Markdown 文本", required=True, example="# 标题\\n\\n这是一段**加粗**文字。"),
        "theme_name": Input(str, "主题名称", required=False, default="macaron/blue", example="macaron/blue"),
        "themes_dir": Input(str, "主题文件目录", required=False, default="./themes", example="./themes")
    },
    outputs={
        "html": Input(str, "转换后的 HTML", example="<h1 style=\"...\">标题</h1>")
    }
)
def format_markdown_to_wechat_html(markdown_content: str, theme_name: str = "macaron/blue", themes_dir: str = "./themes") -> dict:
    """
    [OpenClaw Skill] 将 Markdown 转换为微信兼容 HTML。
    
    支持的 Markdown 元素：
    - 标题（# 到 ######）
    - 粗体 **text** 和斜体 *text*
    - 行内代码 `code` 和代码块 ```
    - 链接 [text](url)
    - 图片 ![alt](src)
    - 无序列表 - item 和有序列表 1. item
    - 引用块 > quote
    - 表格 | col1 | col2 |
    - 分割线 ---
    - 自定义容器 :::release 和 :::grid
    
    Args:
        markdown_content (str): 要转换的 Markdown 文本
        theme_name (str): 主题名称，如 "macaron/blue"、"wenyan/default"、"shuimo/default" 等
        themes_dir (str): 主题文件所在目录
        
    Returns:
        dict: 包含转换结果的字典
            - success (bool): 是否转换成功
            - html (str): 转换后的 HTML 字符串
            - theme_used (str): 使用的主题名称
            - is_markdown (bool): 原文是否被识别为 Markdown
            - error (str): 如果失败，错误信息
        
    Example:
        >>> result = format_markdown_to_wechat_html("# Hello\\n\\n**World**", "macaron/blue")
        >>> print(result["html"])
        <h1 style="...">Hello</h1><p style="..."><strong style="...">World</strong></p>
    """
    # 检查模块是否可用
    if not convert_markdown_to_wechat_html:
        return {
            "success": False,
            "error": "Markdown 转换模块未安装，请确保 markdown_to_wechat_converter.py 可用",
            "html": markdown_content,
            "theme_used": None,
            "is_markdown": False
        }
    
    try:
        # 检测是否为 Markdown
        is_md = is_markdown(markdown_content) if is_markdown else False
        
        # 如果不是 Markdown，直接返回原文
        if not is_md:
            return {
                "success": True,
                "html": markdown_content,
                "theme_used": None,
                "is_markdown": False,
                "message": "内容不是 Markdown 格式，保持原样"
            }
        
        # 执行转换
        html = convert_markdown_to_wechat_html(
            markdown_content=markdown_content,
            theme_name=theme_name,
            themes_dir=themes_dir
        )
        
        return {
            "success": True,
            "html": html,
            "theme_used": theme_name,
            "is_markdown": True,
            "message": "Markdown 转换成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"转换失败: {str(e)}",
            "html": markdown_content,
            "theme_used": None,
            "is_markdown": is_md if is_markdown else False
        }


@skill_info(
    name="validate_article_content",
    description="验证图文消息内容是否符合微信规范，检查字符数、内容大小、图片URL等",
    version="1.0.0",
    author="WeChat Skill Team",
    tags=["wechat", "article", "validation", "验证"],
    inputs={
        "content": Input(str, "HTML 内容", required=True, example="<p>文章内容...</p>")
    },
    outputs={
        "result": Input(dict, "验证结果", example={"valid": True, "char_count": 1000})
    }
)
def validate_article_content_skill(content: str) -> dict:
    """
    [OpenClaw Skill] 验证图文消息内容是否符合微信规范。
    
    检查项目：
    - 字符数是否超过 2 万限制
    - 内容大小是否超过 1MB
    - 是否有外部图片 URL（会被微信过滤）
    - 是否有本地图片路径（需要先上传）
    
    Args:
        content (str): HTML 内容
        
    Returns:
        dict: 验证结果
            - valid: bool, 是否有效
            - char_count: int, 字符数
            - byte_size: int, 字节大小
            - warnings: list, 警告信息
            - errors: list, 错误信息
            - recommendations: list, 建议
    """
    result = validate_article_content(content)
    
    # 添加建议
    recommendations = []
    
    if not result["valid"]:
        recommendations.append("请修复上述错误后再提交")
    
    if result["warnings"]:
        if any("外部图片" in w for w in result["warnings"]):
            recommendations.append("建议：上传外部图片到微信素材库，或使用本地图片路径后自动上传")
        if any("接近上限" in w for w in result["warnings"]):
            recommendations.append("建议：考虑精简内容或拆分为多篇文章")
    
    if result["valid"] and not result["warnings"]:
        recommendations.append("内容验证通过，可以直接提交到草稿箱")
    
    result["recommendations"] = recommendations
    
    return result


@skill_info(
    name="sanitize_html_for_wechat",
    description="清理 HTML 内容，移除微信不支持的标签和属性（危险标签、事件属性等）",
    version="1.0.0",
    author="WeChat Skill Team",
    tags=["wechat", "html", "sanitize", "清理"],
    inputs={
        "html_content": Input(str, "原始 HTML 内容", required=True)
    },
    outputs={
        "result": Input(dict, "清理结果", example={"success": True, "html": "<p>清理后的内容</p>"})
    }
)
def sanitize_html_skill(html_content: str) -> dict:
    """
    [OpenClaw Skill] 清理 HTML 内容，移除微信不支持的标签和属性。
    
    移除内容包括：
    - 危险标签：script, style, iframe, object, embed, form 等
    - 危险属性：onclick, onerror, javascript: 等
    
    Args:
        html_content (str): 原始 HTML 内容
        
    Returns:
        dict: 清理结果
    """
    try:
        cleaned = sanitize_html_for_wechat(html_content)
        return {
            "success": True,
            "html": cleaned,
            "message": "HTML 清理完成"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "html": html_content
        }


# ==========================================
# OpenClaw Skill 接口定义
# ==========================================

@skill_info(
    name="wechat_manage_capability",
    description="微信公众号能力管理统一接口，支持自定义菜单、草稿箱、发布、素材、用户、留言等能力",
    version="2.0.0",
    author="WeChat Skill Team",
    tags=["wechat", "公众号", "草稿箱", "发布", "素材管理", "用户管理"],
    inputs={
        "app_id": Input(str, "微信公众号 AppID", required=True, example="wx1234567890abcdef"),
        "app_secret": Input(str, "微信公众号 AppSecret", required=True, example="your_app_secret_here"),
        "capability": Input(str, "能力模块", required=True, enum=["menu", "draft", "publish", "material", "user", "comment", "message", "kf", "analysis"], example="draft"),
        "action": Input(str, "执行动作", required=True, example="add")
    },
    outputs={
        "result": Input(dict, "API 响应结果", example={"errcode": 0, "errmsg": "ok"})
    }
)
def wechat_manage_capability(app_id: str, app_secret: str, capability: str, action: str, **kwargs) -> dict:
    """
    [OpenClaw Skill] 微信公众号能力管理统一接口。
    支持：自定义菜单(menu)、草稿箱(draft)、发布能力(publish)、素材管理(material)、用户管理(user)、留言管理(comment)、基础消息(message)、客服(kf)、数据统计(analysis)。
    
    Args:
        app_id (str): 微信公众号 AppID
        app_secret (str): 微信公众号 AppSecret
        capability (str): 能力模块，可选值：'menu', 'draft', 'publish', 'material', 'user', 'comment', 'message', 'kf', 'analysis'
        action (str): 执行的动作，例如 'create', 'get', 'delete', 'add', 'update', 'list', 'reply' 等
        **kwargs: 其他动作所需的参数
        
    Returns:
        dict: 微信 API 的响应结果
    """
    manager = WeChatCapabilityManager(app_id, app_secret)
    
    try:
        if capability == 'menu':
            if action == 'create': return manager.create_menu(kwargs.get('menu_data', {}))
            elif action == 'get': return manager.get_menu()
            elif action == 'delete': return manager.delete_menu()
            
        elif capability == 'draft':
            if action == 'add':
                # 自动处理 Markdown 内容转换、HTML 清理和图片上传
                articles = kwargs.get('articles', [])
                theme_name = kwargs.get('theme', 'default')
                themes_dir = kwargs.get('themes_dir', './themes')
                auto_upload_images = kwargs.get('auto_upload_images', True)
                
                # 传递 manager 以支持图片自动上传
                processed_articles = _process_draft_articles(
                    articles, theme_name, themes_dir,
                    auto_upload_images=auto_upload_images,
                    manager=manager if auto_upload_images else None
                )
                return manager.add_draft(processed_articles)
            elif action == 'get': return manager.get_draft(kwargs.get('media_id'))
            elif action == 'delete': return manager.delete_draft(kwargs.get('media_id'))
            elif action == 'update': return manager.update_draft(kwargs.get('media_id'), kwargs.get('index', 0), kwargs.get('article', {}))
            elif action == 'count': return manager.get_draft_count()
            elif action == 'batchget': return manager.batch_get_draft(kwargs.get('offset', 0), kwargs.get('count', 20), kwargs.get('no_content', 0))
            
        elif capability == 'publish':
            if action == 'submit': return manager.submit_publish(kwargs.get('media_id'))
            elif action == 'get_status': return manager.get_publish_status(kwargs.get('publish_id'))
            elif action == 'delete': return manager.delete_publish(kwargs.get('article_id'), kwargs.get('index', 0))
            elif action == 'get_article': return manager.get_publish_article(kwargs.get('article_id'))
            elif action == 'batchget': return manager.batch_get_publish(kwargs.get('offset', 0), kwargs.get('count', 20), kwargs.get('no_content', 0))
            
        elif capability == 'material':
            if action == 'get': return manager.get_material(kwargs.get('media_id'))
            elif action == 'delete': return manager.delete_material(kwargs.get('media_id'))
            elif action == 'count': return manager.get_material_count()
            elif action == 'batchget': return manager.batch_get_material(kwargs.get('type', 'image'), kwargs.get('offset', 0), kwargs.get('count', 20))
            
        elif capability == 'user':
            if action == 'get_list': return manager.get_user_list(kwargs.get('next_openid', ''))
            elif action == 'get_info': return manager.get_user_info(kwargs.get('openid'), kwargs.get('lang', 'zh_CN'))
            elif action == 'update_remark': return manager.update_user_remark(kwargs.get('openid'), kwargs.get('remark'))
            
        elif capability == 'comment':
            msg_data_id = kwargs.get('msg_data_id')
            index = kwargs.get('index', 0)
            user_comment_id = kwargs.get('user_comment_id')
            
            if action == 'open': return manager.open_comment(msg_data_id, index)
            elif action == 'close': return manager.close_comment(msg_data_id, index)
            elif action == 'list': return manager.get_comment_list(msg_data_id, index, kwargs.get('begin', 0), kwargs.get('count', 50), kwargs.get('type', 0))
            elif action == 'markelect': return manager.mark_elect_comment(msg_data_id, index, user_comment_id)
            elif action == 'unmarkelect': return manager.unmark_elect_comment(msg_data_id, index, user_comment_id)
            elif action == 'delete': return manager.delete_comment(msg_data_id, index, user_comment_id)
            elif action == 'reply': return manager.reply_comment(msg_data_id, index, user_comment_id, kwargs.get('content'))
            elif action == 'delete_reply': return manager.delete_reply(msg_data_id, index, user_comment_id)
            
        elif capability == 'message':
            if action == 'send_custom': return manager.send_custom_message(kwargs.get('touser'), kwargs.get('msgtype'), **kwargs.get('msg_data', {}))
            elif action == 'send_mass': return manager.send_mass_message(kwargs.get('filter_is_to_all', True), kwargs.get('filter_tag_id', 0), kwargs.get('msgtype'), **kwargs.get('msg_data', {}))
            
        elif capability == 'kf':
            if action == 'add': return manager.add_kf_account(kwargs.get('kf_account'), kwargs.get('nickname'), kwargs.get('password'))
            elif action == 'get_list': return manager.get_kf_list()
            
        elif capability == 'analysis':
            if action == 'get_article_summary': return manager.get_article_summary(kwargs.get('begin_date'), kwargs.get('end_date'))
            elif action == 'get_user_summary': return manager.get_user_summary(kwargs.get('begin_date'), kwargs.get('end_date'))
            
        return {"errcode": -1, "errmsg": f"不支持的能力或动作: {capability} -> {action}"}
        
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}
