"""
微信公众号 Markdown 转 HTML 转换器 (AST+DOM 架构)

将 Markdown 文本转换为带内联样式的微信兼容 HTML。
使用 markdown 库进行基础解析，BeautifulSoup4 进行 DOM 操作和样式注入。
"""

import re
from typing import Dict, Optional, Any, List, Tuple
from html import escape as html_escape

try:
    import markdown
    from bs4 import BeautifulSoup, Tag, NavigableString
except ImportError:
    raise ImportError(
        "请安装所需依赖: pip install markdown beautifulsoup4\n"
        "当前未检测到这些库"
    )


class MarkdownToWeChatConverter:
    """Markdown 转微信兼容 HTML 转换器 (AST+DOM 架构)"""

    # 微信不支持的标签
    WECHAT_UNSUPPORTED_TAGS = {
        'script', 'style', 'iframe', 'object', 'embed',
        'form', 'input', 'textarea', 'button', 'select',
        'video', 'audio', 'canvas', 'svg', 'applet',
        'base', 'basefont', 'link', 'meta', 'noscript'
    }

    # 微信不支持的属性
    WECHAT_UNSUPPORTED_ATTRS = {
        'onclick', 'onerror', 'onload', 'onmouseover',
        'onmouseout', 'onfocus', 'onblur', 'onchange',
        'onsubmit', 'onkeydown', 'onkeyup', 'onkeypress',
        'class', 'id', 'name', 'action', 'method'
    }

    def __init__(self, theme: Optional[Dict[str, Any]] = None):
        """
        初始化转换器

        Args:
            theme: 主题配置字典，包含 colors, body, h1-h6, blockquote,
                  code_block, code_inline, list, separator, image, link,
                  strong, table, table_th, table_td 等样式配置
        """
        self.theme = theme or self._default_theme()
        self._md = markdown.Markdown(extensions=['tables', 'fenced_code'])

    def _default_theme(self) -> Dict[str, Any]:
        """返回默认主题配置"""
        return {
            "category": "default",
            "colors": {"primary": "#ec4899"},
            "body": {"font_size": "15px", "color": "#3f3f46", "line_height": "1.75"},
            "h1": {"font_size": "22px", "font_weight": "bold", "text_align": "center", "margin": "20px 0"},
            "h2": {"font_size": "18px", "text_align": "left"},
            "h3": {"font_size": "16px", "font_weight": "bold", "margin": "16px 0"},
            "h4": {"font_size": "15px", "font_weight": "bold"},
            "h5": {"font_size": "14px", "font_weight": "bold"},
            "h6": {"font_size": "13px", "font_weight": "bold"},
            "strong": {"font_weight": "bold", "color": "#ec4899"},
            "code_block": {"background_color": "#1e1e1e", "padding": "16px", "border_radius": "12px"},
            "code_inline": {"background_color": "#f4f4f5", "color": "#ec4899", "padding": "2px 4px", "border_radius": "4px"},
            "link": {"color": "#ec4899", "text_decoration": "none"},
            "blockquote": {"border_left": "4px solid #ec4899", "padding_left": "12px", "color": "#71717a", "background_color": "#fdf2f8", "padding": "12px", "border_radius": "4px"},
            "list": {"font_size": "15px", "line_height": "1.75"},
            "separator": {"border_top": "1px solid #ddd", "margin": "20px auto"},
            "image": {"border_radius": "8px", "box_shadow": "0 2px 8px rgba(0,0,0,0.08)"},
            "table_th": {},
            "table_td": {},
        }

    def _style_to_str(self, style_dict: Optional[Dict[str, str]]) -> str:
        """将样式字典转换为 CSS 字符串"""
        if not style_dict:
            return ""
        parts = []
        for k, v in style_dict.items():
            if v:
                css_key = k.replace("_", "-")
                parts.append(f"{css_key}: {v}")
        return "; ".join(parts)

    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        return html_escape(text)

    def _get_primary_color(self) -> str:
        """获取主题主色调"""
        return self.theme.get("colors", {}).get("primary", "#ec4899")

    def _get_contrast_color(self, hex_color: str) -> str:
        """
        根据背景色返回对比色（黑色或白色），使用 YIQ 亮度公式

        Args:
            hex_color: 十六进制颜色值，如 '#ec4899'

        Returns:
            '#000000' (黑色) 或 '#ffffff' (白色)
        """
        hex_color = hex_color.lstrip('#')

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            return "#000000"

        yiq = (r * 299 + g * 587 + b * 114) / 1000
        return "#000000" if yiq > 128 else "#ffffff"

    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """
        将十六进制颜色转换为 RGBA 字符串

        Args:
            hex_color: 十六进制颜色值
            alpha: 透明度，0.0 - 1.0

        Returns:
            RGBA 字符串，如 'rgba(236, 72, 153, 0.1)'
        """
        hex_color = hex_color.lstrip('#')

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            return f"rgba(0, 0, 0, {alpha})"

        return f"rgba({r}, {g}, {b}, {alpha})"

    def _is_category(self, category: str) -> bool:
        """检查当前主题是否属于指定分类"""
        return self.theme.get("category") == category

    def convert(self, markdown_text: str) -> str:
        """
        将 Markdown 转换为微信兼容 HTML (AST+DOM 架构)

        Args:
            markdown_text: 输入的 Markdown 文本

        Returns:
            带内联样式的 HTML 字符串
        """
        # 第一步：保护 OpenClaw 占位符
        protected_placeholders = []
        def protect_placeholder(match):
            protected_placeholders.append(match.group(0))
            # 使用不包含特殊字符的占位符，避免被 markdown 解析
            return f"\x00OPENCLAWPH{len(protected_placeholders) - 1}\x00"
        text = re.sub(r"—PROTECTED-CONTENT-\d+—", protect_placeholder, markdown_text)

        # 第二步：提取并临时移除自定义容器
        text, container_data = self._extract_custom_containers(text)

        # 第三步：使用 markdown 库解析
        html_content = self._md.convert(text)
        self._md.reset()

        # 第四步：创建 BeautifulSoup DOM
        soup = BeautifulSoup(html_content, 'html.parser')

        # 第五步：DOM 遍历并注入样式
        self._inject_styles(soup)

        # 第六步：处理自定义容器
        self._restore_custom_containers(soup, container_data)

        # 第七步：安全清理
        self._sanitize(soup)

        # 第八步：格式化输出
        result = str(soup)

        # 第九步：恢复 OpenClaw 占位符
        for i, placeholder in enumerate(protected_placeholders):
            result = result.replace(f"\x00OPENCLAWPH{i}\x00", placeholder)

        return result

    def _extract_custom_containers(self, text: str) -> Tuple[str, List[Tuple[str, str, str]]]:
        """
        提取自定义容器 ::: type [params...]\n content \n:::
        返回处理后的文本和容器数据列表
        """
        containers: List[Tuple[str, str, str]] = []

        def replace_container(match):
            container_type = match.group(1)
            params = match.group(2) or ""
            content = match.group(3)
            containers.append((container_type, params, content))
            placeholder_id = len(containers) - 1
            # 使用 HTML 注释包裹，markdown 不会破坏，但 BeautifulSoup 可以找到
            return f'\n<!--CUSTOM_CONTAINER_{placeholder_id}-->\n'

        text = re.sub(
            r"::: (\w+)(?:[ \t]+(.*?))?\n([\s\S]*?)\n:::",
            replace_container,
            text,
            flags=re.MULTILINE
        )

        return text, containers

    def _restore_custom_containers(self, soup: BeautifulSoup, container_data: List[Tuple[str, str, str]]) -> None:
        """恢复自定义容器到 DOM"""
        primary_color = self._get_primary_color()

        for i, (container_type, params, content) in enumerate(container_data):
            # 注意：comment 的 string 值只是 'CUSTOM_CONTAINER_X'，不包含 <!-- -->
            comment = soup.find(string=re.compile(f"^CUSTOM_CONTAINER_{i}$"))
            if comment:
                parent = comment.parent
                if parent and parent.name != '[document]':
                    if container_type == 'release':
                        rendered = self._render_release(content, params, primary_color)
                    elif container_type == 'grid':
                        rendered = self._render_grid(content, params, primary_color)
                    elif container_type == 'timeline':
                        rendered = self._render_timeline(content, params, primary_color)
                    elif container_type == 'steps':
                        rendered = self._render_steps(content, params, primary_color)
                    elif container_type == 'compare':
                        rendered = self._render_compare(content, params, primary_color)
                    elif container_type == 'focus':
                        rendered = self._render_focus(content, params, primary_color)
                    else:
                        rendered = f"<div>{content}</div>"

                    new_soup = BeautifulSoup(rendered, 'html.parser')
                    parent.insert_before(new_soup)
                    comment.extract()
                    if parent.name == 'p' and not parent.get_text(strip=True):
                        parent.extract()
                elif parent and parent.name == '[document]':
                    if container_type == 'release':
                        rendered = self._render_release(content, params, primary_color)
                    elif container_type == 'grid':
                        rendered = self._render_grid(content, params, primary_color)
                    elif container_type == 'timeline':
                        rendered = self._render_timeline(content, params, primary_color)
                    elif container_type == 'steps':
                        rendered = self._render_steps(content, params, primary_color)
                    elif container_type == 'compare':
                        rendered = self._render_compare(content, params, primary_color)
                    elif container_type == 'focus':
                        rendered = self._render_focus(content, params, primary_color)
                    else:
                        rendered = f"<div>{content}</div>"

                    new_soup = BeautifulSoup(rendered, 'html.parser')
                    comment.replace_with(new_soup)

        # 清理未处理的注释
        for comment in soup.find_all(string=re.compile(r"^CUSTOM_CONTAINER_\d+$")):
            comment.extract()

    def _inject_styles(self, soup: BeautifulSoup) -> None:
        """遍历 DOM 并为各标签注入样式"""
        primary_color = self._get_primary_color()
        is_wenyan = self._is_category("wenyan")
        is_shuimo = self._is_category("shuimo")

        # 处理所有标签
        for tag in soup.find_all(True):
            tag_name = tag.name.lower()

            if tag_name == 'p':
                self._inject_body_style(tag)
            elif tag_name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                self._inject_heading_style(tag, tag_name, is_wenyan, is_shuimo, primary_color)
            elif tag_name == 'strong' or tag_name == 'b':
                self._inject_strong_style(tag, is_wenyan, primary_color)
            elif tag_name == 'em' or tag_name == 'i':
                self._inject_em_style(tag)
            elif tag_name == 'code':
                # 行内代码
                if tag.parent and tag.parent.name != 'pre':
                    self._inject_inline_code_style(tag, is_wenyan, primary_color)
            elif tag_name == 'pre':
                self._inject_code_block_style(tag, is_wenyan, primary_color)
            elif tag_name == 'blockquote':
                self._inject_blockquote_style(tag, is_wenyan, primary_color)
            elif tag_name == 'a':
                self._inject_link_style(tag, is_wenyan, primary_color)
            elif tag_name == 'img':
                self._inject_image_style(tag, is_wenyan)
            elif tag_name == 'ul' or tag_name == 'ol':
                self._inject_list_style(tag, is_wenyan, primary_color)
            elif tag_name == 'li':
                self._inject_li_style(tag, is_wenyan)
            elif tag_name == 'table':
                self._inject_table_style(tag, primary_color, is_wenyan)
            elif tag_name == 'hr':
                self._inject_hr_style(tag, is_wenyan, primary_color)

    def _inject_body_style(self, tag: Tag) -> None:
        """注入 body/段落样式"""
        body_config = self.theme.get("body", {})
        style = self._style_to_str({**body_config, "margin": "0", "padding": "0"})
        if style:
            self._set_style(tag, style)

    def _inject_heading_style(self, tag: Tag, tag_name: str, is_wenyan: bool, is_shuimo: bool, primary_color: str) -> None:
        """注入标题样式"""
        level = tag_name[1]  # h1, h2, h3, etc.

        if is_wenyan:
            if level == '1':
                style = f"font-size: 22px; font-weight: bold; text-align: center; margin: 24px 0; color: {primary_color};"
            elif level == '2':
                text_align = self.theme.get("h2", {}).get("text_align", "left")
                style = f"display: inline-block; font-size: 22px; font-weight: bold; color: {primary_color}; border-bottom: 2px solid {primary_color}; padding-bottom: 6px; letter-spacing: 2px; margin: 24px 0;"
            elif level == '3':
                style = f"font-size: 18px; font-weight: bold; color: #333; border-left: 4px solid {primary_color}; padding-left: 10px; margin: 24px 0;"
            else:
                style = self._style_to_str(self.theme.get(tag_name, {}))
        elif is_shuimo:
            style = self._style_to_str(self.theme.get(tag_name, {}))
        else:
            # 普通主题的 H2 样式：圆角色块
            if level == '2':
                h2_theme = self.theme.get("h2", {})
                text_align = h2_theme.get("text_align", "left")
                font_size = h2_theme.get("font_size", "18px")
                # 对于 H2，我们不包装，直接设置样式
                style = f"display: inline-block; background-color: {primary_color}; color: #ffffff; padding: 6px 16px; border-radius: 12px; font-size: {font_size}; font-weight: bold; letter-spacing: 1px; margin: 16px 0;"
            else:
                style = self._style_to_str(self.theme.get(tag_name, {}))

        if style:
            self._set_style(tag, style)

    def _inject_strong_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入粗体样式"""
        if is_wenyan:
            style = f"color: {primary_color}; font-weight: bold;"
        else:
            style = self._style_to_str(self.theme.get("strong", {}))
        if style:
            self._set_style(tag, style)

    def _inject_em_style(self, tag: Tag) -> None:
        """注入斜体样式"""
        text_color = self.theme.get("body", {}).get("color", "#4a4a4a")
        style = f"font-style: italic; color: {text_color};"
        self._set_style(tag, style)

    def _inject_inline_code_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入行内代码样式"""
        if is_wenyan:
            style = f"font-size: 13px; padding: 2px 6px; border-radius: 4px; background: #f1f5f9; color: {primary_color}; font-family: 'Courier New', monospace;"
        else:
            style = self._style_to_str(self.theme.get("code_inline", {}))
        if style:
            self._set_style(tag, style)

    def _inject_code_block_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入代码块样式 - 苹果风格"""
        # 苹果风格代码块
        code_html = str(tag)
        language = ""

        # 尝试从 code 标签获取语言
        code_tag = tag.find('code')
        if code_tag:
            code_text = code_tag.get_text()
            # 保持原有代码
        else:
            code_text = tag.get_text()

        # 苹果风格渲染
        apple_style = f"margin: 16px 0; max-width: 100%; box-sizing: border-box; background: #1e1e1e; border-radius: 12px; overflow: hidden; font-family: 'SF Mono', 'Fira Code', 'Menlo', 'Monaco', monospace;"
        header_style = "padding: 12px 16px; background: #2d2d2d; border-bottom: 1px solid #3d3d3d; display: flex; align-items: center; gap: 8px;"
        dot_style = "width: 12px; height: 12px; border-radius: 50%;"
        code_style = "display: block; padding: 16px; overflow-x: auto; font-size: 13px; line-height: 1.6; color: #d4d4d4;"

        # 查找语言标识（如果有）
        if code_tag and code_tag.get('class'):
            classes = code_tag.get('class', [])
            for cls in classes:
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break

        new_html = f'''<section style="margin: 16px 0; max-width: 100%; box-sizing: border-box;">
  <div style="{apple_style}">
    <div style="{header_style}">
      <div style="{dot_style} background: #ff5f56;"></div>
      <div style="{dot_style} background: #ffbd2e;"></div>
      <div style="{dot_style} background: #27c93f;"></div>
      <span style="margin-left: auto; font-size: 11px; color: #888; text-transform: uppercase;">{language or 'code'}</span>
    </div>
    <pre style="{code_style} margin: 0;"><code>{self._escape_html(code_text)}</code></pre>
  </div>
</section>'''

        tag.replace_with(BeautifulSoup(new_html, 'html.parser'))

    def _inject_blockquote_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入引用块样式"""
        if is_wenyan:
            style = f"background-color: #f9f9f9; border-left: 4px solid {primary_color}; padding: 16px; margin: 20px 0; color: #555; font-size: 15px; line-height: 1.8; font-style: italic; border-radius: 0 8px 8px 0;"
        else:
            style = self._style_to_str(self.theme.get("blockquote", {}))
        if style:
            self._set_style(tag, style)

    def _inject_link_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入链接样式"""
        if is_wenyan:
            style = f"color: {primary_color}; text-decoration: none; border-bottom: 1px solid {primary_color};"
        else:
            style = self._style_to_str(self.theme.get("link", {}))
        if style:
            self._set_style(tag, style)

    def _inject_image_style(self, tag: Tag, is_wenyan: bool) -> None:
        """注入图片样式"""
        img_config = self.theme.get("image", {})
        border_radius = "4px" if is_wenyan else img_config.get("border_radius", "8px")
        box_shadow = "0 4px 12px rgba(0,0,0,0.1)" if is_wenyan else img_config.get("box_shadow", "none")

        style = f"max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: {border_radius};"
        if box_shadow and box_shadow != 'none':
            style += f" box-shadow: {box_shadow};"

        # 添加 referrerpolicy
        tag['referrerpolicy'] = 'no-referrer'

        self._set_style(tag, style)

    def _inject_list_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入列表样式"""
        if is_wenyan:
            style = "margin: 16px 0; padding-left: 24px; color: #333; line-height: 1.8; font-size: 16px;"
        else:
            list_config = self.theme.get("list", {})
            style = self._style_to_str(list_config)

        list_type = "disc" if tag.name == "ul" else "decimal"
        style += f" list-style-type: {list_type}; padding-left: 24px;"

        self._set_style(tag, style)

    def _inject_li_style(self, tag: Tag, is_wenyan: bool) -> None:
        """注入列表项样式"""
        if is_wenyan:
            style = "margin: 8px 0; line-height: 1.8; color: #333;"
        else:
            list_config = self.theme.get("list", {})
            line_height = list_config.get("line_height", "1.75")
            text_color = self.theme.get("body", {}).get("color", "#333")
            style = f"margin: 4px 0; line-height: {line_height}; color: {text_color};"
        self._set_style(tag, style)

    def _inject_table_style(self, tag: Tag, primary_color: str, is_wenyan: bool) -> None:
        """注入表格样式"""
        # 表格基础样式
        table_style = "width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; color: #333;"
        self._set_style(tag, table_style)

        # 表头样式
        for th in tag.find_all('th'):
            if is_wenyan:
                th_style = f"padding: 10px 14px; border: 1px solid {primary_color}; background-color: {primary_color}; color: #ffffff; font-weight: bold; text-align: center;"
            else:
                th_config = self.theme.get("table_th", {})
                if th_config:
                    th_style = self._style_to_str(th_config)
                else:
                    th_style = f"padding: 8px 12px; border: 1px solid #e2e8f0; background-color: {primary_color}15; color: {primary_color}; font-weight: bold;"
            self._set_style(th, th_style)

        # 表格单元格样式
        for td in tag.find_all('td'):
            if is_wenyan:
                td_style = f"padding: 10px 14px; border: 1px solid #e5e7eb; color: #374151; text-align: center;"
            else:
                td_config = self.theme.get("table_td", {})
                if td_config:
                    td_style = self._style_to_str(td_config)
                else:
                    td_style = "padding: 8px 12px; border: 1px solid #e2e8f0;"
            self._set_style(td, td_style)

    def _inject_hr_style(self, tag: Tag, is_wenyan: bool, primary_color: str) -> None:
        """注入分割线样式"""
        if is_wenyan:
            style = f"border: none; border-top: 1px dashed {primary_color}; margin: 32px auto; width: 80%; opacity: 0.6;"
        else:
            style = self._style_to_str(self.theme.get("separator", {}))
        if style:
            self._set_style(tag, style)

    def _set_style(self, tag: Tag, style: str) -> None:
        """设置标签的 style 属性"""
        existing = tag.get('style', '')
        if existing:
            # 合并样式
            tag['style'] = existing + "; " + style
        else:
            tag['style'] = style



    def _render_release(self, content: str, params: str, primary_color: str) -> str:
        """渲染 release 组件"""
        param_parts = params.strip().split() if params.strip() else []
        main_title = param_parts[0] if len(param_parts) >= 1 else "WEEKLY SELECTION"
        sub_title = param_parts[1] if len(param_parts) >= 2 else "不仅仅是文字"
        text_color = self._get_contrast_color(primary_color)

        # 处理内容中的 Markdown 语法
        inner_html = content
        inner_html = re.sub(r"^# (.+)$", f'<div style="font-size: 24px; font-weight: bold; color: #333; margin: 12px 0; line-height: 1.4;">\\1</div>', inner_html, flags=re.MULTILINE)
        inner_html = re.sub(r"\*\*(.+?)\*\*", f'<span style="background-color: {primary_color}33; color: {primary_color}; padding: 2px 6px; border-radius: 4px; display: inline-block;">\\1</span>', inner_html)

        return f'''<section style="background-color: #fcf9f2; border-radius: 12px; margin: 24px 0; border: 1px solid #f0ebe1; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="padding: 24px 20px 60px 20px; position: relative;">
    <div style="font-size: 11px; font-weight: bold; color: {primary_color}; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 16px;">{main_title}</div>
    <div style="font-size: 13px; color: #999; margin-bottom: 8px;">{sub_title}</div>
    {inner_html}
  </div>
  <div style="background-color: {primary_color}; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between;">
    <span style="color: {text_color}; font-weight: bold; font-size: 14px;">文摘</span>
    <div>
      <span style="color: rgba(255,255,255,0.9); font-size: 11px; border: 1px solid rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">可共赏</span>
      <span style="color: rgba(255,255,255,0.9); font-size: 11px; border: 1px solid rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">慢阅读</span>
      <span style="color: rgba(255,255,255,0.9); font-size: 11px; border: 1px solid rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">治愈系</span>
    </div>
  </div>
</section>'''

    def _render_grid(self, content: str, params: str, primary_color: str) -> str:
        """渲染 grid 组件"""
        cards = [c.strip() for c in content.split("---") if c.strip()]
        grid_html = '<section style="display: flex; justify-content: space-between; align-items: stretch; margin: 20px 0; overflow-x: auto; padding-bottom: 8px; gap: 8px;">'

        for i, card in enumerate(cards):
            is_first = i == 0
            bg = primary_color if is_first else "#fcfcfc"
            color = self._get_contrast_color(primary_color) if is_first else "#333"
            border = "none" if is_first else "1px solid #f0f0f0"

            lines = card.split("\n")
            sub_title = lines[0] if lines else ""
            main_text = "<br>".join(lines[1:]) if len(lines) > 1 else ""

            grid_html += f'''<div style="flex: 1; min-width: 110px; background-color: {bg}; border-radius: 8px; padding: 12px; border: {border}; box-sizing: border-box;">
  <div style="font-size: 10px; font-weight: bold; color: {'rgba(255,255,255,0.7)' if is_first else '#aaa'}; margin-bottom: 6px;">PART 0{i + 1}</div>
  <div style="font-size: 14px; font-weight: bold; color: {color}; line-height: 1.4; margin-bottom: 6px;">{sub_title}</div>
  <div style="font-size: 11px; color: {'rgba(255,255,255,0.9)' if is_first else '#777'}; line-height: 1.5;">{main_text}</div>
</div>'''

        grid_html += '</section>'
        return grid_html

    def _render_timeline(self, content: str, params: str, primary_color: str) -> str:
        """渲染 timeline 组件"""
        items = [item.strip() for item in content.split("---") if item.strip()]
        timeline_html = f'''<section style="margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow-x: auto;">
  <div style="position: relative; padding-left: 24px;">'''

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            lines = item.split("\n", 1)
            time_text = lines[0].strip() if lines else ""
            desc_text = lines[1].strip() if len(lines) > 1 else ""
            line_style = "" if is_last else f"border-left: 2px solid {primary_color}40;"

            timeline_html += f'''<div style="position: relative; margin-bottom: {'0' if is_last else '20px'}; {line_style}">
  <div style="position: absolute; left: -28px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background-color: {primary_color}; box-shadow: 0 0 0 4px {primary_color}20;"></div>
  <div style="font-size: 12px; color: {primary_color}; font-weight: bold; margin-bottom: 4px;">{time_text}</div>
  <div style="font-size: 14px; color: #333; line-height: 1.6;">{desc_text}</div>
</div>'''

        timeline_html += '</div></section>'
        return timeline_html

    def _render_steps(self, content: str, params: str, primary_color: str) -> str:
        """渲染 steps 组件"""
        items = [item.strip() for item in content.split("---") if item.strip()]
        text_color = self._get_contrast_color(primary_color)
        steps_html = f'''<section style="margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="display: flex; flex-wrap: wrap; gap: 16px;">'''

        for i, item in enumerate(items):
            num = f"0{i + 1}" if i < 9 else str(i + 1)
            lines = item.split("\n", 1)
            step_title = lines[0].strip() if lines else ""
            step_desc = lines[1].strip() if len(lines) > 1 else ""

            steps_html += f'''<div style="flex: 1; min-width: 200px; background-color: {primary_color}; border-radius: 8px; padding: 16px; box-sizing: border-box;">
  <div style="display: inline-block; background-color: {text_color}; color: {primary_color}; font-size: 12px; font-weight: bold; padding: 4px 10px; border-radius: 12px; margin-bottom: 12px;">{num}</div>
  <div style="font-size: 16px; font-weight: bold; color: {text_color}; margin-bottom: 8px;">{step_title}</div>
  <div style="font-size: 13px; color: {'rgba(255,255,255,0.85)' if text_color == '#ffffff' else '#666'}; line-height: 1.5;">{step_desc}</div>
</div>'''

        steps_html += '</div></section>'
        return steps_html

    def _render_compare(self, content: str, params: str, primary_color: str) -> str:
        """渲染 compare 组件"""
        parts = [p.strip() for p in content.split("---") if p.strip()]
        while len(parts) < 2:
            parts.append("")

        left_content = parts[0]
        right_content = parts[1]

        return f'''<section style="margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="display: flex; gap: 16px; flex-wrap: wrap; align-items: stretch;">
    <div style="flex: 1; min-width: 200px; background-color: #f0fdf4; border-radius: 8px; padding: 16px; border: 1px solid #bbf7d0; box-sizing: border-box; display: flex; flex-direction: column;">
      <div style="display: inline-block; background-color: #22c55e; color: #fff; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-bottom: 12px; align-self: flex-start;">正确</div>
      <div style="font-size: 14px; color: #166534; line-height: 1.6; flex: 1;">{left_content}</div>
    </div>
    <div style="flex: 1; min-width: 200px; background-color: #fef2f2; border-radius: 8px; padding: 16px; border: 1px solid #fecaca; box-sizing: border-box; display: flex; flex-direction: column;">
      <div style="display: inline-block; background-color: #ef4444; color: #fff; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-bottom: 12px; align-self: flex-start;">错误</div>
      <div style="font-size: 14px; color: #991b1b; line-height: 1.6; flex: 1;">{right_content}</div>
    </div>
  </div>
</section>'''

    def _render_focus(self, content: str, params: str, primary_color: str) -> str:
        """渲染 focus 组件"""
        bg_rgba = self._hex_to_rgba(primary_color, 0.1)
        text_color = self._get_contrast_color(primary_color)
        lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
        main_text = lines[0] if lines else content.strip()
        display_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", main_text)

        return f'''<section style="margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="background-color: {bg_rgba}; border-top: 3px solid {primary_color}; border-bottom: 3px solid {primary_color}; border-radius: 0; padding: 32px 24px; text-align: center; position: relative;">
    <div style="font-size: 48px; color: {primary_color}40; position: absolute; top: 8px; left: 24px; font-family: Georgia, serif;">"</div>
    <div style="font-size: 20px; font-weight: bold; color: {text_color}; line-height: 1.6; position: relative; z-index: 1;">{display_text}</div>
    <div style="font-size: 48px; color: {primary_color}40; position: absolute; bottom: -16px; right: 24px; font-family: Georgia, serif;">"</div>
  </div>
</section>'''

    def _sanitize(self, soup: BeautifulSoup) -> None:
        """安全清理：移除微信不支持的标签和属性"""
        # 移除不支持的标签
        for tag_name in list(self.WECHAT_UNSUPPORTED_TAGS):
            for tag in soup.find_all(tag_name):
                tag.unwrap()

        # 移除不支持的属性
        for tag in soup.find_all(True):
            for attr in list(tag.attrs.keys()):
                if attr.lower() in self.WECHAT_UNSUPPORTED_ATTRS:
                    del tag[attr]

        # 清理空的 style 属性
        for tag in soup.find_all(True):
            if tag.get('style') and not tag.get('style').strip():
                del tag['style']


def convert_markdown_to_wechat_html(
    markdown_content: str,
    theme_name: str = "default",
    themes_dir: str = "./themes"
) -> str:
    """
    将 Markdown 转换为微信兼容 HTML 的便捷函数

    Args:
        markdown_content: 输入的 Markdown 文本
        theme_name: 主题名称，如 "macaron/blue"、"wenyan/default" 等
        themes_dir: 主题文件目录路径

    Returns:
        带内联样式的 HTML 字符串

    Example:
        >>> html = convert_markdown_to_wechat_html("# Hello\\n\\nThis is **bold** text.", "macaron/blue")
        >>> print(html)
    """
    # 导入 ThemeLoader 以加载主题
    try:
        from .wechat_formatter_skill import ThemeLoader
    except ImportError:
        from wechat_formatter_skill import ThemeLoader

    # 加载主题配置
    theme = ThemeLoader.load_theme(theme_name, themes_dir)

    # 执行转换
    converter = MarkdownToWeChatConverter(theme)
    return converter.convert(markdown_content)


def is_markdown(text: str) -> bool:
    """
    检测文本是否为 Markdown 格式

    检查常见的 Markdown 模式：
    - 标题 (#, ##, etc.)
    - 粗体/斜体 (**text*, *text*)
    - 链接 [text](url)
    - 图片 ![alt](src)
    - 代码块 ```
    - 列表 - 或 1.
    - 引用 >
    - 表格 |
    """
    markdown_patterns = [
        r"^#{1,6}\s+.+$",
        r"\*\*.+?\*\*",
        r"\*(.+?)\*",
        r"`[^`]+`",
        r"```",
        r"\[.+?\]\(.+?\)",
        r"!\[.+?\]\(.+?\)",
        r"^[\s]*[-*]\s+",
        r"^[\s]*\d+\.\s+",
        r"^>\s+",
        r"\|.+\|",
        r"^[-*_]{3,}$",
    ]

    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True

    return False


if __name__ == "__main__":
    # 测试
    converter = MarkdownToWeChatConverter()

    test_md = """# 测试标题

这是一个段落，包含 **粗体** 和 *斜体*。

::: release 周刊 精选
# 这里是标题
内容部分
:::

::: grid
第一项
描述一
---
第二项
描述二
:::

::: focus
这是一句**金句**
:::

```python
def hello():
    print("Hello")
```
"""

    print(converter.convert(test_md))