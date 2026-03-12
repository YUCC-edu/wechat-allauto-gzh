import yaml from 'js-yaml';

export interface ThemeConfig {
  name: string;
  description: string;
  keywords: string[];
  category?: string;
  colors?: Record<string, string>;
  [key: string]: any;
}

export class WeChatHTMLConverter {
  private theme: ThemeConfig;

  constructor(theme: ThemeConfig) {
    this.theme = theme;
  }

  setTheme(theme: ThemeConfig) {
    this.theme = theme;
  }

  private styleToStr(styleDict: Record<string, string> | undefined): string {
    if (!styleDict) return '';
    return Object.entries(styleDict)
      .filter(([_, v]) => v)
      .map(([k, v]) => `${k.replace(/_/g, '-')}: ${v}`)
      .join('; ');
  }

  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  convert(markdownText: string): string {
    let htmlContent = markdownText;

    htmlContent = this.processCodeBlocks(htmlContent);
    htmlContent = this.processHeadings(htmlContent);
    htmlContent = this.processEmphasis(htmlContent);
    htmlContent = this.processInlineCode(htmlContent);
    htmlContent = this.processLinks(htmlContent);
    htmlContent = this.processImages(htmlContent);
    htmlContent = this.processLists(htmlContent);
    htmlContent = this.processTables(htmlContent);
    htmlContent = this.processBlockquotes(htmlContent);
    htmlContent = this.processHr(htmlContent);
    htmlContent = this.processParagraphs(htmlContent);
    htmlContent = this.cleanup(htmlContent);

    return htmlContent;
  }

  private processCodeBlocks(text: string): string {
    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    const style = isWenyan
      ? `font-size: 14px; line-height: 1.8; margin: 16px 0; padding: 16px; border-radius: 8px; background: #f8fafc; color: #333; border-top: 3px solid ${primaryColor}; box-shadow: 0 2px 6px rgba(0,0,0,0.05);`
      : this.styleToStr(this.theme.code_block);
    return text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      const escaped = this.escapeHtml(code);
      return `<section style="margin: 16px 0; max-width: 100%; box-sizing: border-box;"><pre style="${style}; overflow-x: auto; font-family: 'Courier New', monospace; box-sizing: border-box;"><code style="display: block; white-space: pre; font-size: 13px; line-height: 1.6;">${escaped}</code></pre></section>`;
    });
  }

  private processHeadings(text: string): string {
    const h1Style = this.styleToStr(this.theme.h1);
    const h3Style = this.styleToStr(this.theme.h3);
    const h4Style = this.styleToStr(this.theme.h4);
    const h5Style = this.styleToStr(this.theme.h5);
    const h6Style = this.styleToStr(this.theme.h6);

    const isWenyan = this.theme.category === 'wenyan';
    const isShuimo = this.theme.category === 'shuimo';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    
    let result = text;
    result = result.replace(/^# (.+)$/gm, (m, p1) => `<h1 style="${h1Style}">${this.escapeHtml(p1)}</h1>`);
    
    if (isWenyan) {
      const textAlign = this.theme.h2?.text_align || 'left';
      // Elegant Wenyan style for H2: bottom border, letter spacing, primary color
      const h2Style = `display: inline-block; font-size: 22px; font-weight: bold; color: ${primaryColor}; border-bottom: 2px solid ${primaryColor}; padding-bottom: 6px; letter-spacing: 2px;`;
      result = result.replace(/^## (.+)$/gm, (m, p1) => `<section style="margin-top: 32px; margin-bottom: 16px; text-align: ${textAlign};"><h2 style="${h2Style}">${this.escapeHtml(p1)}</h2></section>`);
    } else if (isShuimo) {
      const h2Style = this.styleToStr(this.theme.h2);
      result = result.replace(/^## (.+)$/gm, (m, p1) => `<h2 style="${h2Style}">${this.escapeHtml(p1)}</h2>`);
    } else {
      // H2 Custom Style: Rounded color block
      const h2ThemeStyle = this.theme.h2 || {};
      const textAlign = h2ThemeStyle.text_align || 'left';
      const fontSize = h2ThemeStyle.font_size || '18px';
      
      const h2ContainerStyle = `margin: 32px 0 16px 0; text-align: ${textAlign}; line-height: 1.5;`;
      const h2InnerStyle = `display: inline-block; background-color: ${primaryColor}; color: #ffffff; padding: 6px 16px; border-radius: 12px; font-size: ${fontSize}; font-weight: bold; letter-spacing: 1px;`;
      result = result.replace(/^## (.+)$/gm, (m, p1) => `<h2 style="${h2ContainerStyle}"><span style="${h2InnerStyle}">${this.escapeHtml(p1)}</span></h2>`);
    }

    if (isWenyan) {
      const h3WenyanStyle = `font-size: 18px; font-weight: bold; color: #333; border-left: 4px solid ${primaryColor}; padding-left: 10px; margin-top: 24px; margin-bottom: 12px; line-height: 1.5;`;
      result = result.replace(/^### (.+)$/gm, (m, p1) => `<h3 style="${h3WenyanStyle}">${this.escapeHtml(p1)}</h3>`);
    } else {
      result = result.replace(/^### (.+)$/gm, (m, p1) => `<h3 style="${h3Style}">${this.escapeHtml(p1)}</h3>`);
    }
    
    result = result.replace(/^#### (.+)$/gm, (m, p1) => `<h4 style="${h4Style || h3Style}">${this.escapeHtml(p1)}</h4>`);
    result = result.replace(/^##### (.+)$/gm, (m, p1) => `<h5 style="${h5Style || h3Style}">${this.escapeHtml(p1)}</h5>`);
    result = result.replace(/^###### (.+)$/gm, (m, p1) => `<h6 style="${h6Style || h3Style}">${this.escapeHtml(p1)}</h6>`);
    return result;
  }

  private processEmphasis(text: string): string {
    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    const strongStyle = isWenyan 
      ? `color: ${primaryColor}; font-weight: bold;` 
      : this.styleToStr(this.theme.strong);
    const textColor = this.theme.body?.color || '#4a4a4a';

    let result = text;
    result = result.replace(/\*\*(.+?)\*\*/g, (m, p1) => `<strong style="${strongStyle}">${this.escapeHtml(p1)}</strong>`);
    result = result.replace(/\*(.+?)\*/g, (m, p1) => `<em style="font-style: italic; color: ${textColor};">${this.escapeHtml(p1)}</em>`);
    return result;
  }

  private processInlineCode(text: string): string {
    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    const style = isWenyan
      ? `font-size: 13px; padding: 2px 6px; border-radius: 4px; background: #f1f5f9; color: ${primaryColor}; font-family: 'Courier New', monospace;`
      : this.styleToStr(this.theme.code_inline);
    return text.replace(/`([^`]+)`/g, (m, p1) => `<code style="${style}">${this.escapeHtml(p1)}</code>`);
  }

  private processLinks(text: string): string {
    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    const style = isWenyan
      ? `color: ${primaryColor}; text-decoration: none; border-bottom: 1px solid ${primaryColor};`
      : this.styleToStr(this.theme.link);
    return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, p1, p2) => `<a href="${p2}" style="${style}">${this.escapeHtml(p1)}</a>`);
  }

  private processImages(text: string): string {
    const isWenyan = this.theme.category === 'wenyan';
    const imgStyle = this.theme.image || {};
    const imgBorderRadius = isWenyan ? '4px' : (imgStyle.border_radius || '8px');
    const imgShadow = isWenyan ? '0 4px 12px rgba(0,0,0,0.1)' : (imgStyle.box_shadow || 'none');
    const shadowStyle = imgShadow && imgShadow !== 'none' ? `box-shadow: ${imgShadow};` : '';

    return text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (m, p1, p2) => {
      return `<p style="text-align: center; margin: 24px 0; padding: 0 16px;"><img src="${p2}" alt="${this.escapeHtml(p1)}" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: ${imgBorderRadius}; ${shadowStyle}"></p>`;
    });
  }

  private processLists(text: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    let inUl = false;
    let inOl = false;

    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';

    const listStyle = this.theme.list || {};
    const listStyleStr = this.styleToStr(listStyle);
    const bulletColor = listStyle.bullet_color || '#4a90d9';
    const fontSize = listStyle.font_size || '15px';
    const lineHeight = listStyle.line_height || '1.75';
    const textColor = this.theme.body?.color || '#333';

    const listStyleStrToUse = isWenyan 
      ? `margin: 16px 0; padding-left: 24px; color: #333; line-height: 1.8; font-size: 16px;` 
      : listStyleStr;

    const liStyle = isWenyan 
      ? `margin: 8px 0; line-height: 1.8; color: #333;` 
      : `margin: 4px 0; line-height: ${lineHeight}; color: ${textColor};`;

    for (const line of lines) {
      const ulMatch = line.match(/^[\s]*[-\*] (.+)$/);
      const olMatch = line.match(/^[\s]*(\d+)\. (.+)$/);

      if (ulMatch) {
        if (!inUl) {
          if (inOl) {
            result.push('</ol>');
            inOl = false;
          }
          result.push(`<ul style="${listStyleStrToUse}; list-style-type: disc; padding-left: 24px;">`);
          inUl = true;
        }
        const content = ulMatch[1];
        result.push(`<li style="${liStyle}">${content}</li>`);
      } else if (olMatch) {
        if (!inOl) {
          if (inUl) {
            result.push('</ul>');
            inUl = false;
          }
          result.push(`<ol style="${listStyleStrToUse}; list-style-type: decimal; padding-left: 24px;">`);
          inOl = true;
        }
        const content = olMatch[2];
        result.push(`<li style="${liStyle}">${content}</li>`);
      } else {
        if (inUl) {
          result.push('</ul>');
          inUl = false;
        }
        if (inOl) {
          result.push('</ol>');
          inOl = false;
        }
        result.push(line);
      }
    }

    if (inUl) result.push('</ul>');
    if (inOl) result.push('</ol>');

    return result.join('\n');
  }

  private processBlockquotes(text: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    let inQuote = false;
    let quoteContent: string[] = [];

    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    const style = isWenyan
      ? `background-color: #f9f9f9; border-left: 4px solid ${primaryColor}; padding: 16px; margin: 20px 0; color: #555; font-size: 15px; line-height: 1.8; font-style: italic; border-radius: 0 8px 8px 0;`
      : this.styleToStr(this.theme.blockquote);

    for (const line of lines) {
      const quoteMatch = line.match(/^[\s]*> (.+)$/);
      if (quoteMatch) {
        if (!inQuote) {
          inQuote = true;
          quoteContent = [];
        }
        quoteContent.push(quoteMatch[1]);
      } else {
        if (inQuote) {
          const content = quoteContent.join('<br>');
          result.push(`<blockquote style="${style}">${content}</blockquote>`);
          inQuote = false;
          quoteContent = [];
        }
        result.push(line);
      }
    }

    if (inQuote) {
      const content = quoteContent.join('<br>');
      result.push(`<blockquote style="${style}">${content}</blockquote>`);
    }

    return result.join('\n');
  }

  private processHr(text: string): string {
    const isWenyan = this.theme.category === 'wenyan';
    const primaryColor = this.theme.colors?.primary || '#ec4899';
    const style = isWenyan
      ? `border: none; border-top: 1px dashed ${primaryColor}; margin: 32px auto; width: 80%; opacity: 0.6;`
      : this.styleToStr(this.theme.separator);
    return text.replace(/^[\s]*[-\*_]{3,}[\s]*$/gm, `<section style="${style}"></section>`);
  }

  private processTables(text: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    let i = 0;

    const primaryColor = this.theme.colors?.primary || '#ec4899';

    while (i < lines.length) {
      const line = lines[i].trim();

      if (line.includes('|') && !line.startsWith('>')) {
        const tableLines: string[] = [];
        while (i < lines.length && lines[i].includes('|')) {
          tableLines.push(lines[i].trim());
          i++;
        }

        if (tableLines.length >= 2) {
          const rows = tableLines.map(row => 
            row.split('|').map(c => c.trim()).filter((_, index, arr) => 
              !(index === 0 && arr[0] === '') && !(index === arr.length - 1 && arr[arr.length - 1] === '')
            )
          );

          const headers = rows[0];
          const contentRows = rows.slice(2); // skip separator

          if (headers && contentRows.length > 0) {
            const htmlList: string[] = [];
            htmlList.push(`<section style="margin: 16px 0; width: 100%; overflow-x: auto; box-sizing: border-box;">`);
            htmlList.push(`<table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; color: #333; box-sizing: border-box;">`);
            
            // Header
            htmlList.push(`<thead><tr>`);
            for (const header of headers) {
              if (this.theme.category === 'wenyan') {
                htmlList.push(`<th style="padding: 10px 14px; border: 1px solid ${primaryColor}; background-color: ${primaryColor}; color: #ffffff; font-weight: bold; text-align: center;">${this.escapeHtml(header)}</th>`);
              } else if (this.theme.table_th) {
                const thStyle = this.styleToStr(this.theme.table_th);
                htmlList.push(`<th style="${thStyle}">${this.escapeHtml(header)}</th>`);
              } else {
                htmlList.push(`<th style="padding: 8px 12px; border: 1px solid #e2e8f0; background-color: ${primaryColor}15; color: ${primaryColor}; font-weight: bold;">${this.escapeHtml(header)}</th>`);
              }
            }
            htmlList.push(`</tr></thead>`);

            // Body
            htmlList.push(`<tbody>`);
            for (const row of contentRows) {
              htmlList.push(`<tr>`);
              for (const cell of row) {
                if (this.theme.category === 'wenyan') {
                  htmlList.push(`<td style="padding: 10px 14px; border: 1px solid #e5e7eb; color: #374151; text-align: center;">${this.escapeHtml(cell)}</td>`);
                } else if (this.theme.table_td) {
                  const tdStyle = this.styleToStr(this.theme.table_td);
                  htmlList.push(`<td style="${tdStyle}">${this.escapeHtml(cell)}</td>`);
                } else {
                  htmlList.push(`<td style="padding: 8px 12px; border: 1px solid #e2e8f0;">${this.escapeHtml(cell)}</td>`);
                }
              }
              htmlList.push(`</tr>`);
            }
            htmlList.push(`</tbody></table></section>`);
            
            result.push(htmlList.join(''));
          }
        }
        continue;
      }

      result.push(lines[i]);
      i++;
    }

    return result.join('\n');
  }

  private processParagraphs(text: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    let paragraph: string[] = [];

    // Force margin to 0 to avoid empty lines between paragraphs
    const style = this.styleToStr({
      ...this.theme.body,
      margin: '0',
      padding: '0',
    });

    const flushParagraph = () => {
      if (paragraph.length > 0) {
        const content = paragraph.join('');
        if (content.trim()) {
          result.push(`<p style="${style}">${content}</p>`);
        }
        paragraph = [];
      }
    };

    let consecutiveEmptyLines = 0;

    for (const line of lines) {
      const stripped = line.trim();
      const isBlockTag = /^(<\/?(h[1-6]|ul|ol|li|blockquote|pre|section|p|div|table|tr|td|th)(>|\s))/.test(stripped);

      if (isBlockTag) {
        flushParagraph();
        result.push(line);
        consecutiveEmptyLines = 0;
      } else if (stripped) {
        paragraph.push(stripped);
        consecutiveEmptyLines = 0;
      } else {
        flushParagraph();
        consecutiveEmptyLines++;
        if (consecutiveEmptyLines > 1) {
          result.push(`<p style="${style}"><br></p>`);
        }
      }
    }
    flushParagraph();

    return result.join('\n');
  }

  private cleanup(text: string): string {
    let result = text;
    result = result.replace(/\n{2,}/g, '\n');
    result = result.split('\n').map(line => line.trim()).join('\n');
    result = result.replace(/>[\s\n]+</g, '><');
    result = result.replace(/\n/g, '');
    return result.trim();
  }
}
