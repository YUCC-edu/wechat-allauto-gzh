import re
import html as html_module
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class ThemeLoader:
    """从 YAML 文件加载主题"""
    _cache: Dict[str, dict] = {}
    
    @classmethod
    def load_theme(cls, theme_name: str, themes_dir: str = "./themes") -> dict:
        """加载指定主题，如果不存在则返回默认配置"""
        if theme_name in cls._cache:
            return cls._cache[theme_name]
            
        themes_dir_path = Path(themes_dir)
        if not themes_dir_path.exists():
            # 如果传入的 themes_dir 不存在，尝试使用相对于当前文件的路径
            themes_dir_path = Path(__file__).parent.parent / "themes"
            
        theme_file = themes_dir_path / f"{theme_name}.yaml"
        if not theme_file.exists():
            # 尝试检查是否是一个目录，如果是，则加载该目录下的 default.yaml
            dir_theme_file = themes_dir_path / theme_name / "default.yaml"
            if dir_theme_file.exists():
                theme_file = dir_theme_file
            else:
                print(f"Warning: Theme '{theme_name}' not found. Falling back to default theme.")
                # 提供一个内置的默认主题作为 fallback
                return {
                    "name": "默认主题",
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
                
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme_data = yaml.safe_load(f)
            
        result = {
            'name': theme_data.get('name', '未命名主题'),
            'colors': theme_data.get('colors', {}),
        }
        result.update(theme_data.get('styles', {}))
        cls._cache[theme_name] = result
        return result

class WeChatHTMLConverter:
    """微信公众号 HTML 转换器 (OpenClaw 专项优化版)"""
    
    def __init__(self, theme_name: str = "default", themes_dir: str = "./themes"):
        self.theme_name = theme_name
        self.theme = ThemeLoader.load_theme(theme_name, themes_dir)
        
    def _style_to_str(self, style_dict: dict) -> str:
        if not style_dict:
            return ""
        return "; ".join([f"{k.replace('_', '-')}: {v}" for k, v in style_dict.items() if v])
        
    def escape_html(self, text: str) -> str:
        return html_module.escape(text, quote=False)
        
    def convert(self, markdown_text: str) -> str:
        html_content = markdown_text
        html_content = self._process_code_blocks(html_content)
        html_content = self._process_headings(html_content)
        html_content = self._process_tables(html_content)
        html_content = self._process_images(html_content)
        html_content = self._process_links(html_content)
        html_content = self._process_inline_code(html_content)
        html_content = self._process_emphasis(html_content)
        html_content = self._process_lists(html_content)
        html_content = self._process_blockquotes(html_content)
        html_content = self._process_hr(html_content)
        html_content = self._process_paragraphs(html_content)
        html_content = self._cleanup(html_content)
        return html_content

    def _process_code_blocks(self, text: str) -> str:
        pattern = r'```(\w+)?\n(.*?)```'
        style = self._style_to_str(self.theme.get("code_block", {}))
        
        def replace_code_block(match):
            code = match.group(2)
            code_escaped = self.escape_html(code)
            return f'''<section style="margin: 16px 0; max-width: 100%; box-sizing: border-box;"><pre style="{style}; overflow-x: auto; font-family: 'Courier New', monospace; box-sizing: border-box;"><code style="display: block; white-space: pre; font-size: 13px; line-height: 1.6;">{code_escaped}</code></pre></section>'''
        
        return re.sub(pattern, replace_code_block, text, flags=re.DOTALL)

    def _process_headings(self, text: str) -> str:
        h1_style = self._style_to_str(self.theme.get("h1", {}))
        h3_style = self._style_to_str(self.theme.get("h3", {}))
        
        primary_color = self.theme.get("colors", {}).get("primary", "#ec4899")
        h2_theme_style = self.theme.get("h2", {})
        text_align = h2_theme_style.get("text_align", "left")
        font_size = h2_theme_style.get("font_size", "18px")
        
        h2_container_style = f"margin: 32px 0 16px 0; text-align: {text_align}; line-height: 1.5;"
        h2_inner_style = f"display: inline-block; background-color: {primary_color}; color: #ffffff; padding: 6px 16px; border-radius: 12px; font-size: {font_size}; font-weight: bold; letter-spacing: 1px;"
        
        text = re.sub(r'^# (.+)$', lambda m: f'<h1 style="{h1_style}">{self.escape_html(m.group(1))}</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', lambda m: f'<h2 style="{h2_container_style}"><span style="{h2_inner_style}">{self.escape_html(m.group(1))}</span></h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', lambda m: f'<h3 style="{h3_style}">{self.escape_html(m.group(1))}</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.+)$', lambda m: f'<h4 style="{h3_style}">{self.escape_html(m.group(1))}</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^##### (.+)$', lambda m: f'<h5 style="{h3_style}">{self.escape_html(m.group(1))}</h5>', text, flags=re.MULTILINE)
        text = re.sub(r'^###### (.+)$', lambda m: f'<h6 style="{h3_style}">{self.escape_html(m.group(1))}</h6>', text, flags=re.MULTILINE)
        return text

    def _process_emphasis(self, text: str) -> str:
        strong_style = self._style_to_str(self.theme.get("strong", {}))
        text = re.sub(r'\*\*(.+?)\*\*', lambda m: f'<strong style="{strong_style}">{self.escape_html(m.group(1))}</strong>', text)
        text_color = self.theme.get("body", {}).get("color", "#4a4a4a")
        text = re.sub(r'\*(.+?)\*', lambda m: f'<em style="font-style: italic; color: {text_color};">{self.escape_html(m.group(1))}</em>', text)
        return text

    def _process_inline_code(self, text: str) -> str:
        style = self._style_to_str(self.theme.get("code_inline", {}))
        return re.sub(r'`(.+?)`', lambda m: f'<code style="{style}">{self.escape_html(m.group(1))}</code>', text)

    def _process_links(self, text: str) -> str:
        style = self._style_to_str(self.theme.get("link", {}))
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}" style="{style}">{self.escape_html(m.group(1))}</a>', text)

    def _process_images(self, text: str) -> str:
        img_style = self.theme.get("image", {})
        img_border_radius = img_style.get("border_radius", "8px")
        img_shadow = img_style.get("box_shadow", "none")
        shadow_style = f"box-shadow: {img_shadow};" if img_shadow and img_shadow != "none" else ""
        return re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            lambda m: f'<p style="text-align: center; margin: 20px 0; padding: 0 16px;"><img src="{m.group(2)}" alt="{self.escape_html(m.group(1))}" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: {img_border_radius}; {shadow_style}"></p>',
            text
        )

    def _process_lists(self, text: str) -> str:
        lines = text.split('\n')
        result = []
        in_ul = False
        in_ol = False
        
        list_style = self.theme.get("list", {})
        list_style_str = self._style_to_str(list_style)
        line_height = list_style.get("line_height", "1.75")
        text_color = self.theme.get("body", {}).get("color", "#333")
        
        for line in lines:
            ul_match = re.match(r'^[\s]*[-\*] (.+)$', line)
            ol_match = re.match(r'^[\s]*(\d+)\. (.+)$', line)
            
            if ul_match:
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append(f'<ul style="{list_style_str}; list-style-type: disc; padding-left: 24px;">')
                    in_ul = True
                content = ul_match.group(1)
                result.append(f'<li style="margin: 4px 0; line-height: {line_height}; color: {text_color};">{content}</li>')
            elif ol_match:
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append(f'<ol style="{list_style_str}; list-style-type: decimal; padding-left: 24px;">')
                    in_ol = True
                content = ol_match.group(2)
                result.append(f'<li style="margin: 4px 0; line-height: {line_height}; color: {text_color};">{content}</li>')
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)
                
        if in_ul: result.append('</ul>')
        if in_ol: result.append('</ol>')
        return '\n'.join(result)

    def _process_blockquotes(self, text: str) -> str:
        lines = text.split('\n')
        result = []
        in_quote = False
        quote_content = []
        style = self._style_to_str(self.theme.get("blockquote", {}))
        
        for line in lines:
            quote_match = re.match(r'^[\s]*> (.+)$', line)
            if quote_match:
                if not in_quote:
                    in_quote = True
                    quote_content = []
                quote_content.append(quote_match.group(1))
            else:
                if in_quote:
                    content = '<br>'.join(quote_content)
                    result.append(f'<blockquote style="{style}">{content}</blockquote>')
                    in_quote = False
                    quote_content = []
                result.append(line)
                
        if in_quote:
            content = '<br>'.join(quote_content)
            result.append(f'<blockquote style="{style}">{content}</blockquote>')
        return '\n'.join(result)

    def _process_hr(self, text: str) -> str:
        style = self._style_to_str(self.theme.get("separator", {}))
        return re.sub(r'^[\s]*[-\*_]{3,}[\s]*$', f'<section style="{style}"></section>', text, flags=re.MULTILINE)

    def _process_tables(self, text: str) -> str:
        lines = text.split('\n')
        result = []
        i = 0
        primary_color = self.theme.get("colors", {}).get("primary", "#ec4899")
        
        while i < len(lines):
            line = lines[i].strip()
            if '|' in line and not line.startswith('>'):
                table_lines = []
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i].strip())
                    i += 1
                
                if len(table_lines) >= 2:
                    rows = []
                    for row in table_lines:
                        cells = [c.strip() for c in row.split('|')]
                        if cells and cells[0] == '': cells.pop(0)
                        if cells and cells[-1] == '': cells.pop()
                        rows.append(cells)
                    
                    headers = rows[0]
                    content_rows = rows[2:] if len(rows) > 2 else []
                    
                    if headers and content_rows:
                        html_list = []
                        html_list.append('<section style="margin: 16px 0; width: 100%; overflow-x: auto; box-sizing: border-box;">')
                        html_list.append('<table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; color: #333; box-sizing: border-box;">')
                        
                        html_list.append('<thead><tr>')
                        for header in headers:
                            html_list.append(f'<th style="padding: 8px 12px; border: 1px solid #e2e8f0; background-color: {primary_color}15; color: {primary_color}; font-weight: bold;">{self.escape_html(header)}</th>')
                        html_list.append('</tr></thead>')
                        
                        html_list.append('<tbody>')
                        for row in content_rows:
                            html_list.append('<tr>')
                            for cell in row:
                                html_list.append(f'<td style="padding: 8px 12px; border: 1px solid #e2e8f0;">{self.escape_html(cell)}</td>')
                            html_list.append('</tr>')
                        html_list.append('</tbody></table></section>')
                        
                        result.append(''.join(html_list))
                        continue
            
            result.append(lines[i] if i < len(lines) else "")
            i += 1
            
        return '\n'.join(result)

    def _process_paragraphs(self, text: str) -> str:
        lines = text.split('\n')
        result = []
        paragraph = []
        
        body_style = self.theme.get("body", {}).copy()
        body_style["margin"] = "0"
        body_style["padding"] = "0"
        style = self._style_to_str(body_style)
        
        def flush_paragraph():
            nonlocal paragraph
            if paragraph:
                content = ''.join(paragraph)
                if content.strip():
                    result.append(f'<p style="{style}">{content}</p>')
                paragraph = []
        
        consecutive_empty_lines = 0
        
        for line in lines:
            stripped = line.strip()
            is_block_tag = re.match(r'^(</?(h[1-6]|ul|ol|li|blockquote|pre|section|p|div|table|tr|td|th)(>|\s))', stripped)
            
            if is_block_tag:
                flush_paragraph()
                result.append(line)
                consecutive_empty_lines = 0
            elif stripped:
                paragraph.append(stripped)
                consecutive_empty_lines = 0
            else:
                flush_paragraph()
                consecutive_empty_lines += 1
                if consecutive_empty_lines > 1:
                    result.append(f'<p style="{style}"><br></p>')
                    
        flush_paragraph()
        return '\n'.join(result)

    def _cleanup(self, text: str) -> str:
        text = re.sub(r'\n{2,}', '\n', text)
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        text = re.sub(r'>[\s\n]+<', '><', text)
        text = text.replace('\n', '')
        return text.strip()

# ==========================================
# OpenClaw Skill 接口定义
# ==========================================

def convert_markdown_to_wechat_html(markdown_content: str, theme_name: str = "default", themes_dir: str = "./themes") -> str:
    """
    [OpenClaw Skill] 将 Markdown 文本转换为微信公众号兼容的 HTML 格式。
    
    Args:
        markdown_content (str): 需要转换的 Markdown 文本内容。
        theme_name (str): 主题名称，默认 "default"。
        themes_dir (str): 主题 YAML 文件所在的目录路径。
        
    Returns:
        str: 转换后的微信公众号兼容 HTML 字符串。
    """
    converter = WeChatHTMLConverter(theme_name=theme_name, themes_dir=themes_dir)
    return converter.convert(markdown_content)

if __name__ == "__main__":
    # 测试用例
    sample_md = '''
## 核心功能介绍
这里是段落测试。
包含**粗体**和*斜体*。

| 参数 | 说明 |
| --- | --- |
| 速度 | 极快 |
| 兼容 | 完美 |

* 列表项1
* 列表项2

```python
print("Hello WeChat!")
```
    '''
    print(convert_markdown_to_wechat_html(sample_md))
