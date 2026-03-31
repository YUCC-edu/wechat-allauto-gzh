import re
import html as html_module
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from functools import lru_cache

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 自定义异常类
# ==========================================
class ThemeError(Exception):
    """主题相关错误"""
    pass

class ThemeNotFoundError(ThemeError):
    """主题未找到"""
    pass

class YAMLParseError(ThemeError):
    """YAML 解析错误"""
    pass

class FileIOError(ThemeError):
    """文件 IO 错误"""
    pass

# ==========================================
# 默认主题配置（内置 fallback）
# ==========================================
DEFAULT_THEME_CONFIG = {
    "name": "默认主题",
    "category": "default",
    "colors": {"primary": "#ec4899"},
    "body": {"font_size": "15px", "color": "#3f3f46", "line_height": "1.75"},
    "h1": {"font_size": "22px", "font_weight": "bold", "text_align": "center", "margin": "20px 0"},
    "h2": {"font_size": "18px", "text_align": "left"},
    "h3": {"font_size": "16px", "font_weight": "bold", "margin": "16px 0"},
    "strong": {"font_weight": "bold", "color": "#ec4899"},
    "code_block": {"background_color": "#f4f4f5", "padding": "16px", "border_radius": "8px"},
    "code_inline": {"background_color": "#f4f4f5", "color": "#ec4899", "padding": "2px 4px", "border_radius": "4px"},
    "link": {"color": "#ec4899", "text_decoration": "none"},
    "blockquote": {"border_left": "4px solid #ec4899", "padding_left": "12px", "color": "#71717a", "background_color": "#fdf2f8", "padding": "12px", "border_radius": "4px"}
}

class ThemeLoader:
    """从 YAML 文件加载主题（鲁棒性增强版）"""
    _cache: Dict[str, dict] = {}
    
    @classmethod
    def load_theme(cls, theme_name: str, themes_dir: str = "./themes") -> dict:
        """
        加载指定主题，如果不存在则返回默认配置
        
        鲁棒性特性：
        - 自动从文件路径提取 category
        - YAML 解析错误处理
        - 文件 IO 错误处理
        - 缓存机制
        """
        if theme_name in cls._cache:
            logger.debug(f"从缓存加载主题: {theme_name}")
            return cls._cache[theme_name]
        
        try:
            return cls._load_theme_internal(theme_name, themes_dir)
        except (ThemeNotFoundError, YAMLParseError, FileIOError) as e:
            logger.warning(f"加载主题 '{theme_name}' 失败: {e}，使用默认主题")
            return DEFAULT_THEME_CONFIG.copy()
    
    @classmethod
    def _load_theme_internal(cls, theme_name: str, themes_dir: str) -> dict:
        """内部主题加载逻辑"""
        themes_dir_path = Path(themes_dir)
        
        # 如果传入的 themes_dir 不存在，尝试使用相对于当前文件的路径
        if not themes_dir_path.exists():
            themes_dir_path = Path(__file__).parent.parent / "themes"
            if not themes_dir_path.exists():
                raise FileIOError(f"主题目录不存在: {themes_dir}")
        
        # 解析主题文件路径
        theme_file, category = cls._resolve_theme_file(themes_dir_path, theme_name)
        
        if not theme_file or not theme_file.exists():
            raise ThemeNotFoundError(f"主题文件不存在: {theme_name}")
        
        # 读取并解析 YAML
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                yaml_content = f.read()
        except UnicodeDecodeError as e:
            raise FileIOError(f"文件编码错误: {theme_file}")
        except IOError as e:
            raise FileIOError(f"读取文件失败: {theme_file} - {e}")
        
        # 解析 YAML
        try:
            theme_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise YAMLParseError(f"YAML 解析错误: {theme_file} - {e}")
        
        if not isinstance(theme_data, dict):
            raise YAMLParseError(f"YAML 内容不是有效的字典: {theme_file}")
        
        # 构建结果
        result = {
            'name': theme_data.get('name', '未命名主题'),
            'category': category,
            'colors': theme_data.get('colors', {}),
        }
        result.update(theme_data.get('styles', {}))
        
        # 缓存结果
        cls._cache[theme_name] = result
        logger.info(f"成功加载主题: {theme_name} (category: {category})")
        
        return result
    
    @classmethod
    def _resolve_theme_file(cls, themes_dir: Path, theme_name: str) -> tuple:
        """
        解析主题文件路径并提取 category
        
        支持以下格式：
        - 'default' -> themes/default.yaml (category: 'default')
        - 'wenyan/default' -> themes/wenyan/default.yaml (category: 'wenyan')
        - 'wenyan/lapis' -> themes/wenyan/lapis.yaml (category: 'wenyan')
        
        Returns: (theme_file_path, category)
        """
        parts = theme_name.split('/')
        
        if len(parts) == 1:
            # 格式: 'theme_name' -> themes/theme_name.yaml
            theme_file = themes_dir / f"{theme_name}.yaml"
            category = "default"
        elif len(parts) >= 2:
            # 格式: 'category/theme_name' -> themes/category/theme_name.yaml
            category = parts[0]
            sub_theme = parts[1] if len(parts) > 1 else "default"
            
            # 优先尝试 themes/category/sub_theme.yaml
            theme_file = themes_dir / category / f"{sub_theme}.yaml"
            
            # 如果不存在，尝试 themes/category/default.yaml
            if not theme_file.exists():
                fallback_file = themes_dir / category / "default.yaml"
                if fallback_file.exists():
                    theme_file = fallback_file
        else:
            theme_file = None
            category = "default"
        
        return (theme_file, category)
    
    @classmethod
    def clear_cache(cls):
        """清除主题缓存"""
        cls._cache.clear()
        logger.info("主题缓存已清除")
    
    @classmethod
    def get_cache_info(cls) -> dict:
        """获取缓存信息"""
        return {
            'cache_size': len(cls._cache),
            'cached_themes': list(cls._cache.keys())
        }