"""
OpenClaw Skill 兼容层

提供 OpenClaw Skill 标准接口的兼容实现，包括：
- skill_info 装饰器
- SkillException 异常基类
- Input 类型注解
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union


class SkillException(Exception):
    """
    OpenClaw Skill 异常基类
    
    所有 Skill 相关的异常都应该继承此类，
    以便 OpenClaw 框架进行统一的错误处理和日志记录。
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "SKILL_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典格式，便于序列化"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class Input:
    """
    OpenClaw Skill 输入参数注解
    
    用于声明 Skill 方法的输入参数类型和描述，
    便于 OpenClaw 框架进行参数验证和文档生成。
    
    示例:
        @skill_info(name="my_skill")
        class MySkill:
            def execute(self, text: Input(str, "输入文本")) -> str:
                return text.upper()
    """
    
    def __init__(
        self, 
        type_: Type, 
        description: str = "",
        required: bool = True,
        default: Any = None,
        enum: Optional[List[Any]] = None,
        example: Any = None
    ):
        self.type = type_
        self.description = description
        self.required = required
        self.default = default
        self.enum = enum
        self.example = example
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "type": self.type.__name__ if hasattr(self.type, "__name__") else str(self.type),
            "description": self.description,
            "required": self.required
        }
        if self.default is not None:
            result["default"] = self.default
        if self.enum is not None:
            result["enum"] = self.enum
        if self.example is not None:
            result["example"] = self.example
        return result


def skill_info(
    name: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "1.0.0",
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    icon: Optional[str] = None,
    inputs: Optional[Dict[str, Input]] = None,
    outputs: Optional[Dict[str, Input]] = None
):
    """
    OpenClaw Skill 信息装饰器
    
    用于声明 Skill 的元数据信息，便于 OpenClaw 框架进行：
    - 技能发现和注册
    - 文档自动生成
    - 参数验证
    - 版本管理
    
    示例:
        @skill_info(
            name="wechat_publisher",
            description="发布文章到微信公众号",
            version="2.0.0",
            author="Your Name",
            tags=["wechat", "publish", "article"]
        )
        class WeChatPublisher:
            pass
    """
    
    def decorator(obj):
        # 构建 Skill 元数据
        skill_metadata = {
            "name": name or (obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__),
            "description": description or obj.__doc__ or "",
            "version": version,
            "author": author,
            "tags": tags or [],
            "icon": icon,
            "inputs": {k: v.to_dict() for k, v in (inputs or {}).items()},
            "outputs": {k: v.to_dict() for k, v in (outputs or {}).items()},
            "obj_name": obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__,
            "module": obj.__module__ if hasattr(obj, '__module__') else obj.__class__.__module__
        }
        
        # 根据对象类型存储元数据
        if isinstance(obj, type):
            # 类装饰器
            obj._skill_info = skill_metadata
            obj.get_skill_info = classmethod(lambda cls: cls._skill_info)
            obj.__doc__ = description or obj.__doc__
        elif callable(obj):
            # 函数装饰器
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                return obj(*args, **kwargs)
            wrapper._skill_info = skill_metadata
            wrapper.get_skill_info = lambda: skill_metadata
            wrapper.__doc__ = description or obj.__doc__
            return wrapper
        
        return obj
    
    return decorator


# ==========================================
# 辅助函数
# ==========================================

def validate_skill_method(func: Callable) -> Callable:
    """
    装饰器：验证 Skill 方法的输入参数
    
    检查方法的类型注解，验证输入参数类型是否匹配。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取方法签名
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        # 验证类型注解
        for name, value in bound.arguments.items():
            param = sig.parameters.get(name)
            if param and param.annotation != inspect.Parameter.empty:
                annotation = param.annotation
                # 处理 Input 类型注解
                if isinstance(annotation, Input):
                    if not isinstance(value, annotation.type):
                        raise SkillException(
                            f"参数 '{name}' 类型错误: 期望 {annotation.type.__name__}, 实际 {type(value).__name__}",
                            error_code="VALIDATION_ERROR"
                        )
                # 处理常规类型注解
                elif not isinstance(value, annotation):
                    raise SkillException(
                        f"参数 '{name}' 类型错误: 期望 {annotation.__name__}, 实际 {type(value).__name__}",
                        error_code="VALIDATION_ERROR"
                    )
        
        return func(*args, **kwargs)
    
    return wrapper


def get_registered_skills(module) -> Dict[str, Type]:
    """
    从模块中获取所有已注册的 Skill 类
    
    扫描模块中的所有类，返回带有 `_skill_info` 属性的类。
    """
    skills = {}
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and hasattr(obj, '_skill_info'):
            info = obj._skill_info
            skills[info.get('name', name)] = obj
    return skills


# ==========================================
# 向后兼容
# ==========================================

# 别名，便于迁移
SkillInfo = skill_info
ExceptionBase = SkillException