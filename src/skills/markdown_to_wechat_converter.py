"""
微信公众号 Markdown 转 HTML 转换器

将 Markdown 文本转换为带内联样式的微信兼容 HTML。
参考前端 src/utils/WeChatHTMLConverter.ts 实现。
"""

import re
import html as html_module
from typing import Dict, Optional, Any


class MarkdownToWeChatConverter:
    """Markdown 转微信兼容 HTML 转换器"""
    
    def __init__(self, theme: Optional[Dict[str, Any]] = None):
        """
        初始化转换器
        
        Args:
            theme: 主题配置字典，包含 colors, body, h1-h6, blockquote, 
                  code_block, code_inline, list, separator, image, link, 
                  strong, table, table_th, table_td 等样式配置
        """
        self.theme = theme or self._default_theme()
    
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
            "code_block": {"background_color": "#f4f4f5", "padding": "16px", "border_radius": "8px"},
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
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;"))
    
    def _get_primary_color(self) -> str:
        """获取主题主色调"""
        return self.theme.get("colors", {}).get("primary", "#ec4899")
    
    def _is_category(self, category: str) -> bool:
        """检查当前主题是否属于指定分类"""
        return self.theme.get("category") == category
    
    def convert(self, markdown_text: str) -> str:
        """
        将 Markdown 转换为微信兼容 HTML
        
        Args:
            markdown_text: 输入的 Markdown 文本
            
        Returns:
            带内联样式的 HTML 字符串
        """
        html_content = markdown_text
        
        # 按顺序处理各元素
        html_content = self._process_code_blocks(html_content)
        html_content = self._process_custom_containers(html_content)
        html_content = self._process_headings(html_content)
        html_content = self._process_emphasis(html_content)
        html_content = self._process_inline_code(html_content)
        html_content = self._process_links(html_content)
        html_content = self._process_images(html_content)
        html_content = self._process_lists(html_content)
        html_content = self._process_tables(html_content)
        html_content = self._process_blockquotes(html_content)
        html_content = self._process_hr(html_content)
        html_content = self._process_paragraphs(html_content)
        html_content = self._cleanup(html_content)
        
        return html_content
    
    def _process_code_blocks(self, text: str) -> str:
        """处理代码块"""
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        if is_wenyan:
            style = f"font-size: 14px; line-height: 1.8; margin: 16px 0; padding: 16px; border-radius: 8px; background: #f8fafc; color: #333; border-top: 3px solid {primary_color}; box-shadow: 0 2px 6px rgba(0,0,0,0.05);"
        else:
            style = self._style_to_str(self.theme.get("code_block"))
        
        def replace_code_block(match):
            lang = match.group(1)
            code = match.group(2)
            escaped = self._escape_html(code)
            return f'<section style="margin: 16px 0; max-width: 100%; box-sizing: border-box;"><pre style="{style}; overflow-x: auto; font-family: \'Courier New\', monospace; box-sizing: border-box;"><code style="display: block; white-space: pre; font-size: 13px; line-height: 1.6;">{escaped}</code></pre></section>'
        
        return re.sub(r"```(\w+)?\n([\s\S]*?)```", replace_code_block, text)
    
    def _process_custom_containers(self, text: str) -> str:
        """处理自定义容器 ::: release 和 ::: grid"""
        primary_color = self._get_primary_color()
        
        def replace_release(match):
            content = match.group(1)
            inner_html = content
            inner_html = re.sub(r"^# (.+)$", f'<div style="font-size: 24px; font-weight: bold; color: #333; margin: 12px 0; line-height: 1.4;">\\1</div>', inner_html, flags=re.MULTILINE)
            inner_html = re.sub(r"\*\*(.+?)\*\*", f'<span style="background-color: {primary_color}33; color: {primary_color}; padding: 2px 6px; border-radius: 4px; display: inline-block;">\\1</span>', inner_html)
            
            return f'''
          <section style="background-color: #fcf9f2; border-radius: 12px; margin: 24px 0; border: 1px solid #f0ebe1; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="padding: 24px 20px 60px 20px; position: relative;">
              <div style="font-size: 11px; font-weight: bold; color: {primary_color}; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 16px;">WEEKLY SELECTION</div>
              <div style="font-size: 13px; color: #999; margin-bottom: 8px;">不仅仅是文字</div>
              {inner_html}
            </div>
            <div style="background-color: {primary_color}; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between;">
              <span style="color: #fff; font-weight: bold; font-size: 14px;">文摘</span>
              <div>
                <span style="color: rgba(255,255,255,0.9); font-size: 11px; border: 1px solid rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">可共赏</span>
                <span style="color: rgba(255,255,255,0.9); font-size: 11px; border: 1px solid rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">慢阅读</span>
                <span style="color: rgba(255,255,255,0.9); font-size: 11px; border: 1px solid rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 4px; margin-left: 6px;">治愈系</span>
              </div>
            </div>
          </section>'''
        
        text = re.sub(r"::: release\n([\s\S]*?)\n:::", replace_release, text)
        
        def replace_grid(match):
            content = match.group(1)
            cards = [c.strip() for c in content.split("---") if c.strip()]
            
            grid_html = '<section style="display: flex; justify-content: space-between; align-items: stretch; margin: 20px 0; overflow-x: auto; padding-bottom: 8px; gap: 8px;">'
            
            for i, card in enumerate(cards):
                is_first = i == 0
                bg = primary_color if is_first else "#fcfcfc"
                color = "#fff" if is_first else "#333"
                border = "none" if is_first else "1px solid #f0f0f0"
                
                lines = card.split("\n")
                sub_title = lines[0] if lines else ""
                main_text = "<br>".join(lines[1:]) if len(lines) > 1 else ""
                
                grid_html += f'''
              <div style="flex: 1; min-width: 110px; background-color: {bg}; border-radius: 8px; padding: 12px; border: {border}; box-sizing: border-box;">
                <div style="font-size: 10px; font-weight: bold; color: {'rgba(255,255,255,0.7)' if is_first else '#aaa'}; margin-bottom: 6px;">PART 0{i + 1}</div>
                <div style="font-size: 14px; font-weight: bold; color: {color}; line-height: 1.4; margin-bottom: 6px;">{sub_title}</div>
                <div style="font-size: 11px; color: {'rgba(255,255,255,0.9)' if is_first else '#777'}; line-height: 1.5;">{main_text}</div>
              </div>'''
            
            grid_html += "</section>"
            return grid_html
        
        text = re.sub(r"::: grid\n([\s\S]*?)\n:::", replace_grid, text)
        
        return text
    
    def _process_headings(self, text: str) -> str:
        """处理标题"""
        is_wenyan = self._is_category("wenyan")
        is_shuimo = self._is_category("shuimo")
        primary_color = self._get_primary_color()
        
        h1_style = self._style_to_str(self.theme.get("h1"))
        h3_style = self._style_to_str(self.theme.get("h3"))
        h4_style = self._style_to_str(self.theme.get("h4")) or h3_style
        h5_style = self._style_to_str(self.theme.get("h5")) or h3_style
        h6_style = self._style_to_str(self.theme.get("h6")) or h3_style
        
        # H1
        text = re.sub(r"^# (.+)$", lambda m: f'<h1 style="{h1_style}">{self._escape_html(m.group(1))}</h1>', text, flags=re.MULTILINE)
        
        # H2
        if is_wenyan:
            text_align = self.theme.get("h2", {}).get("text_align", "left")
            h2_style = f"display: inline-block; font-size: 22px; font-weight: bold; color: {primary_color}; border-bottom: 2px solid {primary_color}; padding-bottom: 6px; letter-spacing: 2px;"
            text = re.sub(r"^## (.+)$", lambda m: f'<section style="margin-top: 32px; margin-bottom: 16px; text-align: {text_align};"><h2 style="{h2_style}">{self._escape_html(m.group(1))}</h2></section>', text, flags=re.MULTILINE)
        elif is_shuimo:
            h2_style = self._style_to_str(self.theme.get("h2"))
            text = re.sub(r"^## (.+)$", lambda m: f'<h2 style="{h2_style}">{self._escape_html(m.group(1))}</h2>', text, flags=re.MULTILINE)
        else:
            h2_theme = self.theme.get("h2", {})
            text_align = h2_theme.get("text_align", "left")
            font_size = h2_theme.get("font_size", "18px")
            h2_container = f"margin: 32px 0 16px 0; text-align: {text_align}; line-height: 1.5;"
            h2_inner = f"display: inline-block; background-color: {primary_color}; color: #ffffff; padding: 6px 16px; border-radius: 12px; font-size: {font_size}; font-weight: bold; letter-spacing: 1px;"
            text = re.sub(r"^## (.+)$", lambda m: f'<section style="{h2_container}"><span style="{h2_inner}">{self._escape_html(m.group(1))}</span></section>', text, flags=re.MULTILINE)
        
        # H3
        if is_wenyan:
            h3_style = f"font-size: 18px; font-weight: bold; color: #333; border-left: 4px solid {primary_color}; padding-left: 10px; margin-top: 24px; margin-bottom: 12px; line-height: 1.5;"
        text = re.sub(r"^### (.+)$", lambda m: f'<h3 style="{h3_style}">{self._escape_html(m.group(1))}</h3>', text, flags=re.MULTILINE)
        
        # H4-H6
        text = re.sub(r"^#### (.+)$", lambda m: f'<h4 style="{h4_style}">{self._escape_html(m.group(1))}</h4>', text, flags=re.MULTILINE)
        text = re.sub(r"^##### (.+)$", lambda m: f'<h5 style="{h5_style}">{self._escape_html(m.group(1))}</h5>', text, flags=re.MULTILINE)
        text = re.sub(r"^###### (.+)$", lambda m: f'<h6 style="{h6_style}">{self._escape_html(m.group(1))}</h6>', text, flags=re.MULTILINE)
        
        return text
    
    def _process_emphasis(self, text: str) -> str:
        """处理强调（粗体、斜体）"""
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        if is_wenyan:
            strong_style = f"color: {primary_color}; font-weight: bold;"
        else:
            strong_style = self._style_to_str(self.theme.get("strong"))
        
        text_color = self.theme.get("body", {}).get("color", "#4a4a4a")
        
        # 粗体 **text**
        text = re.sub(r"\*\*(.+?)\*\*", lambda m: f'<strong style="{strong_style}">{self._escape_html(m.group(1))}</strong>', text)
        # 斜体 *text*
        text = re.sub(r"\*(.+?)\*", lambda m: f'<em style="font-style: italic; color: {text_color};">{self._escape_html(m.group(1))}</em>', text)
        
        return text
    
    def _process_inline_code(self, text: str) -> str:
        """处理行内代码 `code`"""
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        if is_wenyan:
            style = f"font-size: 13px; padding: 2px 6px; border-radius: 4px; background: #f1f5f9; color: {primary_color}; font-family: 'Courier New', monospace;"
        else:
            style = self._style_to_str(self.theme.get("code_inline"))
        
        return re.sub(r"`([^`]+)`", lambda m: f'<code style="{style}">{self._escape_html(m.group(1))}</code>', text)
    
    def _process_links(self, text: str) -> str:
        """处理链接 [text](url)"""
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        if is_wenyan:
            style = f"color: {primary_color}; text-decoration: none; border-bottom: 1px solid {primary_color};"
        else:
            style = self._style_to_str(self.theme.get("link"))
        
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}" style="{style}">{self._escape_html(m.group(1))}</a>', text)
    
    def _process_images(self, text: str) -> str:
        """处理图片 ![alt](src)"""
        is_wenyan = self._is_category("wenyan")
        img_config = self.theme.get("image", {})
        
        img_border_radius = "4px" if is_wenyan else img_config.get("border_radius", "8px")
        img_shadow = "0 4px 12px rgba(0,0,0,0.1)" if is_wenyan else img_config.get("box_shadow", "none")
        shadow_style = f"box-shadow: {img_shadow};" if img_shadow and img_shadow != "none" else ""
        
        return re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            lambda m: f'<p style="text-align: center; margin: 24px 0; padding: 0 16px;"><img src="{m.group(2)}" alt="{self._escape_html(m.group(1))}" referrerpolicy="no-referrer" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: {img_border_radius}; {shadow_style}"></p>',
            text
        )
    
    def _process_lists(self, text: str) -> str:
        """处理列表"""
        lines = text.split("\n")
        result = []
        in_ul = False
        in_ol = False
        
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        list_config = self.theme.get("list", {})
        list_style = self._style_to_str(list_config)
        bullet_color = list_config.get("bullet_color", "#4a90d9")
        font_size = list_config.get("font_size", "15px")
        line_height = list_config.get("line_height", "1.75")
        text_color = self.theme.get("body", {}).get("color", "#333")
        
        if is_wenyan:
            list_style_str = "margin: 16px 0; padding-left: 24px; color: #333; line-height: 1.8; font-size: 16px;"
            li_style = "margin: 8px 0; line-height: 1.8; color: #333;"
        else:
            list_style_str = list_style
            li_style = f"margin: 4px 0; line-height: {line_height}; color: {text_color};"
        
        for line in lines:
            ul_match = re.match(r"^[\s]*[-\*] (.+)$", line)
            ol_match = re.match(r"^[\s]*(\d+)\. (.+)$", line)
            
            if ul_match:
                if not in_ul:
                    if in_ol:
                        result.append("</ol>")
                        in_ol = False
                    result.append(f'<ul style="{list_style_str}; list-style-type: disc; padding-left: 24px;">')
                    in_ul = True
                content = ul_match.group(1)
                result.append(f'<li style="{li_style}">{content}</li>')
            elif ol_match:
                if not in_ol:
                    if in_ul:
                        result.append("</ul>")
                        in_ul = False
                    result.append(f'<ol style="{list_style_str}; list-style-type: decimal; padding-left: 24px;">')
                    in_ol = True
                content = ol_match.group(2)
                result.append(f'<li style="{li_style}">{content}</li>')
            else:
                if in_ul:
                    result.append("</ul>")
                    in_ul = False
                if in_ol:
                    result.append("</ol>")
                    in_ol = False
                result.append(line)
        
        if in_ul:
            result.append("</ul>")
        if in_ol:
            result.append("</ol>")
        
        return "\n".join(result)
    
    def _process_tables(self, text: str) -> str:
        """处理表格"""
        lines = text.split("\n")
        result = []
        i = 0
        primary_color = self._get_primary_color()
        
        while i < len(lines):
            line = lines[i].strip()
            
            if "|" in line and not line.startswith(">"):
                table_lines = []
                while i < len(lines) and "|" in lines[i]:
                    table_lines.append(lines[i].strip())
                    i += 1
                
                if len(table_lines) >= 2:
                    rows = []
                    for row in table_lines:
                        cells = [c.strip() for c in row.split("|")]
                        # 过滤首尾空单元格
                        if cells and cells[0] == "":
                            cells = cells[1:]
                        if cells and cells[-1] == "":
                            cells = cells[:-1]
                        rows.append(cells)
                    
                    headers = rows[0]
                    content_rows = rows[2:]  # 跳过表头和分隔符行
                    
                    if headers and content_rows:
                        html_list = []
                        html_list.append('<section style="margin: 16px 0; width: 100%; overflow-x: auto; box-sizing: border-box;">')
                        html_list.append('<table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; color: #333; box-sizing: border-box;">')
                        
                        # 表头
                        html_list.append("<thead><tr>")
                        for header in headers:
                            if self._is_category("wenyan"):
                                th_style = f"padding: 10px 14px; border: 1px solid {primary_color}; background-color: {primary_color}; color: #ffffff; font-weight: bold; text-align: center;"
                            elif self.theme.get("table_th"):
                                th_style = self._style_to_str(self.theme.get("table_th"))
                            else:
                                th_style = f"padding: 8px 12px; border: 1px solid #e2e8f0; background-color: {primary_color}15; color: {primary_color}; font-weight: bold;"
                            html_list.append(f'<th style="{th_style}">{self._escape_html(header)}</th>')
                        html_list.append("</tr></thead>")
                        
                        # 表体
                        html_list.append("<tbody>")
                        for row in content_rows:
                            html_list.append("<tr>")
                            for cell in row:
                                if self._is_category("wenyan"):
                                    td_style = f"padding: 10px 14px; border: 1px solid #e5e7eb; color: #374151; text-align: center;"
                                elif self.theme.get("table_td"):
                                    td_style = self._style_to_str(self.theme.get("table_td"))
                                else:
                                    td_style = "padding: 8px 12px; border: 1px solid #e2e8f0;"
                                html_list.append(f'<td style="{td_style}">{self._escape_html(cell)}</td>')
                            html_list.append("</tr>")
                        html_list.append("</tbody></table></section>")
                        
                        result.append("".join(html_list))
                continue
            
            result.append(lines[i])
            i += 1
        
        return "\n".join(result)
    
    def _process_blockquotes(self, text: str) -> str:
        """处理引用块"""
        lines = text.split("\n")
        result = []
        in_quote = False
        quote_content = []
        
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        if is_wenyan:
            style = f"background-color: #f9f9f9; border-left: 4px solid {primary_color}; padding: 16px; margin: 20px 0; color: #555; font-size: 15px; line-height: 1.8; font-style: italic; border-radius: 0 8px 8px 0;"
        else:
            style = self._style_to_str(self.theme.get("blockquote"))
        
        for line in lines:
            quote_match = re.match(r"^[\s]*> (.+)$", line)
            if quote_match:
                if not in_quote:
                    in_quote = True
                    quote_content = []
                quote_content.append(quote_match.group(1))
            else:
                if in_quote:
                    content = "<br>".join(quote_content)
                    result.append(f'<blockquote style="{style}">{content}</blockquote>')
                    in_quote = False
                    quote_content = []
                result.append(line)
        
        if in_quote:
            content = "<br>".join(quote_content)
            result.append(f'<blockquote style="{style}">{content}</blockquote>')
        
        return "\n".join(result)
    
    def _process_hr(self, text: str) -> str:
        """处理分割线"""
        is_wenyan = self._is_category("wenyan")
        primary_color = self._get_primary_color()
        
        if is_wenyan:
            style = f"border: none; border-top: 1px dashed {primary_color}; margin: 32px auto; width: 80%; opacity: 0.6;"
        else:
            style = self._style_to_str(self.theme.get("separator"))
        
        return re.sub(r"^[\s]*[-\*_]{3,}[\s]*$", f'<section style="{style}"></section>', text, flags=re.MULTILINE)
    
    def _process_paragraphs(self, text: str) -> str:
        """处理段落"""
        lines = text.split("\n")
        result = []
        paragraph = []
        
        body_config = self.theme.get("body", {})
        body_style = self._style_to_str({**body_config, "margin": "0", "padding": "0"})
        
        def flush_paragraph():
            if paragraph:
                content = "".join(paragraph)
                if content.strip():
                    result.append(f'<p style="{body_style}">{content}</p>')
                paragraph.clear()
        
        consecutive_empty = 0
        
        for line in lines:
            stripped = line.strip()
            # 检查是否是以块级标签开头的已处理行
            is_block_tag = bool(re.match(r"^(<\/?(h[1-6]|ul|ol|li|blockquote|pre|section|p|div|table|tr|td|th)(>|\s))", stripped))
            
            if is_block_tag:
                flush_paragraph()
                result.append(line)
                consecutive_empty = 0
            elif stripped:
                paragraph.append(stripped)
                consecutive_empty = 0
            else:
                flush_paragraph()
                consecutive_empty += 1
                if consecutive_empty > 1:
                    result.append(f'<p style="{body_style}"><br></p>')
        
        flush_paragraph()
        return "\n".join(result)
    
    def _cleanup(self, text: str) -> str:
        """清理和优化 HTML"""
        # 合并多个空行
        text = re.sub(r"\n{2,}", "\n", text)
        # 去除每行首尾空格
        text = "\n".join(line.strip() for line in text.split("\n"))
        # 清理标签之间的空白
        text = re.sub(r">[\s\n]+<", "><", text)
        # 移除所有换行符（微信不支持）
        text = text.replace("\n", "")
        
        return text.strip()


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


# 辅助函数：检测文本是否为 Markdown
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
        r"^#{1,6}\s+.+$",  # 标题
        r"\*\*.+?\*\*",     # 粗体
        r"\*(.+?)\*",       # 斜体（排除列表）
        r"`[^`]+`",         # 行内代码
        r"```",             # 代码块
        r"\[.+?\]\(.+?\)",  # 链接
        r"!\[.+?\]\(.+?\)", # 图片
        r"^[\s]*[-*]\s+",   # 无序列表
        r"^[\s]*\d+\.\s+",  # 有序列表
        r"^>\s+",           # 引用
        r"\|.+\|",          # 表格
        r"^[-*_]{3,}$",    # 分割线
    ]
    
    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    return False
