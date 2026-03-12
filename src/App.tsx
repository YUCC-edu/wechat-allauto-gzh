import React, { useState, useEffect, useMemo } from 'react';
import { loadAllThemes, ThemeInfo } from './utils/themeLoader';
import { WeChatHTMLConverter } from './utils/WeChatHTMLConverter';
import { Smartphone, Code, Eye, Palette, RefreshCw } from 'lucide-react';

const TEMPLATES = {
  default: {
    name: '功能介绍',
    content: `# 微信公众号排版预览

欢迎使用微信公众号排版预览工具！这里展示了各种精美的主题排版效果。

## 核心功能

* **多主题支持**：内置文颜主题和马卡龙色系主题
* **实时预览**：左侧输入 Markdown，右侧实时查看排版效果
* **微信规范**：严格按照微信公众号的 HTML 规范生成

### 代码块展示

\`\`\`python
def hello_world():
    print("Hello, WeChat!")
    return True
\`\`\`

### 引用与强调

> 排版是一门艺术，好的排版能让阅读成为一种享受。

在这里，你可以使用 **粗体**，也可以使用 *斜体*，或者添加一个 [链接](https://mp.weixin.qq.com)。

### 列表展示

1. 第一步：选择一个喜欢的主题
2. 第二步：输入你的 Markdown 内容
3. 第三步：复制生成的 HTML 到微信公众号后台

### 表格展示

| 参数 | 数值 | 说明 |
| --- | --- | --- |
| 主题数量 | 20+ | 包含多种风格 |
| 响应速度 | 毫秒级 | 实时渲染无延迟 |

---

![示例图片](https://picsum.photos/seed/wechat/800/400)

感谢使用！`
  },
  tech: {
    name: '技术教程',
    content: `# Python 异步编程指南

在现代 Web 开发中，异步编程已经成为提升性能的关键技术。

## 1. 什么是异步编程？

异步编程允许程序在等待 I/O 操作（如网络请求、文件读写）完成时，继续执行其他任务，而不是阻塞等待。

### 核心概念

* **Event Loop (事件循环)**：负责调度和执行异步任务。
* **Coroutine (协程)**：使用 \`async def\` 定义的函数。
* **Future/Task**：代表一个异步操作的最终结果。

## 2. 基础示例

下面是一个简单的 \`asyncio\` 示例：

\`\`\`python
import asyncio

async def fetch_data():
    print("开始获取数据...")
    await asyncio.sleep(2)  # 模拟网络请求
    print("数据获取完成！")
    return {"status": 200}

async def main():
    await fetch_data()

asyncio.run(main())
\`\`\`

## 3. 性能对比

| 模式 | 耗时 | 资源占用 |
| --- | --- | --- |
| 同步阻塞 | 10.5s | 低 |
| 多线程 | 3.2s | 高 |
| 异步 I/O | 3.1s | 极低 |

> 提示：在 I/O 密集型任务中，异步编程的优势最为明显。

## 总结

掌握异步编程，能让你的 Python 应用性能产生质的飞跃。`
  },
  essay: {
    name: '生活随笔',
    content: `# 周末的咖啡馆时光

阳光透过落地窗洒在木质桌面上，这是一个难得清闲的周末下午。

## 城市的避风港

在快节奏的城市生活中，街角的咖啡馆就像是一个小小的避风港。推开门，伴随着清脆的风铃声，浓郁的咖啡豆香气扑面而来。

> 生活不是为了赶路，而是为了感受路上的风景。

### 今天的点单

* **手冲耶加雪菲**：带有淡淡的柑橘酸甜，口感干净明亮。
* **海盐海绵蛋糕**：微咸的奶油中和了蛋糕的甜腻，恰到好处。

## 慢下来的意义

平时我们总是在追赶 DDl，回复不完的消息，处理不完的邮件。只有在这样的时刻，时间才真正属于自己。

1. 翻开一本买来许久却没时间看的书
2. 在笔记本上随意写下几句感悟
3. 仅仅是看着窗外匆匆走过的人群发呆

![咖啡时光](https://picsum.photos/seed/coffee/800/500)

或许，我们需要经常给自己按下“暂停键”，才能更好地继续前行。`
  }
};

export default function App() {
  const [themes, setThemes] = useState<ThemeInfo[]>([]);
  const [selectedThemeId, setSelectedThemeId] = useState<string>('');
  const [selectedTemplate, setSelectedTemplate] = useState<keyof typeof TEMPLATES>('default');
  const [markdown, setMarkdown] = useState(TEMPLATES.default.content);
  const [html, setHtml] = useState('');
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');

  useEffect(() => {
    const loadedThemes = loadAllThemes();
    setThemes(loadedThemes);
    if (loadedThemes.length > 0) {
      setSelectedThemeId(loadedThemes[0].id);
    }
  }, []);

  const selectedTheme = useMemo(() => {
    return themes.find(t => t.id === selectedThemeId);
  }, [themes, selectedThemeId]);

  useEffect(() => {
    if (selectedTheme) {
      const converter = new WeChatHTMLConverter(selectedTheme.config);
      setHtml(converter.convert(markdown));
    }
  }, [markdown, selectedTheme]);

  const categories = useMemo(() => {
    const cats = new Set(themes.map(t => t.category));
    return Array.from(cats);
  }, [themes]);

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-slate-200 flex flex-col h-full z-10 shadow-sm">
        <div className="p-4 border-b border-slate-200 flex items-center gap-2 bg-slate-50">
          <Palette className="w-5 h-5 text-indigo-600" />
          <h1 className="font-semibold text-slate-800">排版主题预览</h1>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-6">
          {categories.map(category => (
            <div key={category}>
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 px-2">
                {category === 'wenyan' ? '文颜主题' : category === 'macaron' ? '马卡龙主题' : category === 'shuimo' ? '水墨主题' : category}
              </h2>
              <div className="space-y-1">
                {themes.filter(t => t.category === category).map(theme => (
                  <button
                    key={theme.id}
                    onClick={() => setSelectedThemeId(theme.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                      selectedThemeId === theme.id
                        ? 'bg-indigo-50 text-indigo-700 font-medium'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full shadow-sm border border-black/5" 
                        style={{ backgroundColor: theme.config.colors?.primary || '#ccc' }}
                      />
                      <span className="truncate">{theme.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="font-medium text-slate-800">
              {selectedTheme?.name || 'Loading...'}
            </h2>
            {selectedTheme?.config.description && (
              <span className="text-sm text-slate-500 hidden md:inline-block">
                {selectedTheme.config.description}
              </span>
            )}
          </div>
          
          <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
            <button
              onClick={() => setViewMode('preview')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                viewMode === 'preview' 
                  ? 'bg-white text-slate-800 shadow-sm' 
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Eye className="w-4 h-4" />
              预览
            </button>
            <button
              onClick={() => setViewMode('code')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                viewMode === 'code' 
                  ? 'bg-white text-slate-800 shadow-sm' 
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Code className="w-4 h-4" />
              HTML
            </button>
          </div>
        </header>

        {/* Editor & Preview Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Markdown Editor */}
          <div className="w-1/2 border-r border-slate-200 flex flex-col bg-white">
            <div className="p-2 border-b border-slate-100 bg-slate-50 text-xs font-medium text-slate-500 uppercase tracking-wider flex justify-between items-center">
              <div className="flex items-center gap-3">
                <span>Markdown 输入</span>
                <select 
                  value={selectedTemplate}
                  onChange={(e) => {
                    const key = e.target.value as keyof typeof TEMPLATES;
                    setSelectedTemplate(key);
                    setMarkdown(TEMPLATES[key].content);
                  }}
                  className="bg-white border border-slate-200 rounded px-2 py-1 text-slate-700 outline-none focus:border-indigo-500 font-sans normal-case"
                >
                  {Object.entries(TEMPLATES).map(([key, tpl]) => (
                    <option key={key} value={key}>{tpl.name}</option>
                  ))}
                </select>
              </div>
              <button 
                onClick={() => setMarkdown(TEMPLATES[selectedTemplate].content)}
                className="hover:text-indigo-600 transition-colors flex items-center gap-1"
                title="重置为当前模板默认内容"
              >
                <RefreshCw className="w-3 h-3" /> 重置
              </button>
            </div>
            <textarea
              value={markdown}
              onChange={(e) => setMarkdown(e.target.value)}
              className="flex-1 w-full p-6 resize-none focus:outline-none font-mono text-sm text-slate-700 leading-relaxed bg-slate-50/50"
              placeholder="在这里输入 Markdown..."
              spellCheck={false}
            />
          </div>

          {/* Preview/Code Pane */}
          <div className="w-1/2 bg-slate-100 flex flex-col relative">
            <div className="p-2 border-b border-slate-200 bg-slate-50 text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center gap-2">
              {viewMode === 'preview' ? <Smartphone className="w-3.5 h-3.5" /> : <Code className="w-3.5 h-3.5" />}
              <span>{viewMode === 'preview' ? '微信公众号预览' : '生成的 HTML'}</span>
            </div>
            
            <div className="flex-1 overflow-auto p-8 flex justify-center items-start">
              {viewMode === 'preview' ? (
                <div className="w-[375px] min-h-[667px] bg-white shadow-xl rounded-[2rem] border-[8px] border-slate-800 overflow-hidden relative flex flex-col">
                  {/* Phone Notch */}
                  <div className="absolute top-0 inset-x-0 h-6 flex justify-center z-20">
                    <div className="w-32 h-4 bg-slate-800 rounded-b-xl"></div>
                  </div>
                  
                  {/* WeChat Header Mock */}
                  <div className="h-16 bg-slate-100 border-b border-slate-200 flex items-end justify-center pb-3 shrink-0 pt-6">
                    <h3 className="font-medium text-slate-800">公众号文章</h3>
                  </div>
                  
                  {/* Article Content */}
                  <div className="flex-1 overflow-y-auto bg-white">
                    <div 
                      className="p-4 pb-12"
                      dangerouslySetInnerHTML={{ __html: html }}
                    />
                  </div>
                </div>
              ) : (
                <div className="w-full h-full bg-slate-900 rounded-lg shadow-inner p-4 overflow-auto">
                  <pre className="text-slate-300 font-mono text-xs whitespace-pre-wrap break-all">
                    {html}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
