import React, { useState, useEffect, useMemo } from 'react';
import { loadAllThemes, ThemeInfo } from './utils/themeLoader';
import { WeChatHTMLConverter } from './utils/WeChatHTMLConverter';
import { Smartphone, Code, Eye, Palette, RefreshCw } from 'lucide-react';

const TEMPLATES = {
  default: {
    name: '功能介绍',
    content: `# 微信公众号排版预览工具

欢迎使用！这是一个功能完备的 Markdown 到微信 HTML 转换工具，支持多主题切换和实时预览。

## 核心特性

* **实时预览**：左右分栏编辑，毫秒级响应
* **20+ 精美主题**：涵盖马卡龙、文颜、水墨等多种风格
* **高级组件**：支持 release、grid、timeline 等排版组件
* **微信规范**：生成纯内联样式 HTML，完美兼容公众号平台

### 苹果风格代码块

\`\`\`javascript
const converter = new WeChatHTMLConverter(themeConfig);
const html = converter.convert(markdownText);

console.log('转换结果:', html.length, '字符');
\`\`\`

### 引用与强调

> 好的排版让阅读成为一种享受。
> 好的设计是尽可能少的设计。

在这里，你可以使用 **粗体** 强调重点，也可以用 *斜体* 表达情感，或者添加 [链接](https://mp.weixin.qq.com) 指向参考资料。

### 操作步骤

1. 选择一个喜欢的主题风格
2. 在左侧输入 Markdown 内容
3. 右侧实时预览排版效果
4. 点击「HTML」查看生成的代码
5. 复制代码到公众号后台使用

### 主题色配置

| 主题类型 | 数量 | 风格描述 |
| --- | --- | --- |
| 马卡龙 | 12 | 清新明亮，低饱和度 |
| 文颜 | 8 | 古风雅致，传统色彩 |
| 水墨 | 1 | 中国传统水墨风格 |
| 极客 | 1 | 终端命令行风格 |

---

![主题预览](https://picsum.photos/seed/wechat/800/400)

开始创作你的第一篇文章吧！
`
  },
  tech: {
    name: '技术教程',
    content: `# Swift 并发编程指南

Swift 5.5 引入了全新的并发模型，让异步代码的编写变得前所未有的简洁和安全。

## 1. async/await 基础

传统的回调地狱已经成为过去。Swift 的 async/await 语法让异步代码看起来像同步代码一样直观。

### 基本用法

\`\`\`swift
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

Task {
    do {
        let user = try await fetchUser(id: 42)
        print("用户名称: \\(user.name)")
    } catch {
        print("获取失败: \\(error)")
    }
}
\`\`\`

### 并行执行

当多个任务相互独立时，可以并行启动它们，显著提升执行效率：

\`\`\`swift
func fetchAllUsers() async throws -> [User] {
    async let user1 = fetchUser(id: 1)
    async let user2 = fetchUser(id: 2)
    async let user3 = fetchUser(id: 3)
    
    return try await [user1, user2, user3]
}
\`\`\`

## 2. Actor 模型 - 线程安全

Actor 是 Swift 提供的全新并发类型，自动保证状态访问的线程安全。

\`\`\`swift
actor BankAccount {
    private var balance: Double = 0
    
    func deposit(_ amount: Double) {
        balance += amount
    }
    
    func withdraw(_ amount: Double) throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }
        balance -= amount
    }
    
    var currentBalance: Double {
        balance
    }
}

let account = BankAccount()
await account.deposit(1000)
let balance = await account.currentBalance
\`\`\`

## 3. Task 取消与优先级

\`\`\`swift
func downloadFile(from url: URL) async throws -> Data {
    let task = Task {
        var data = Data()
        for await chunk in url.session.bytes(from: url) {
            try Task.checkCancellation()
            data.append(contentsOf: chunk)
        }
        return data
    }
    
    // 5秒后取消
    try await Task.sleep(nanoseconds: 5_000_000_000)
    task.cancel()
    
    return try await task.value
}
\`\`\`

## 性能对比

| 方式 | 代码复杂度 | 性能 | 线程安全 |
| --- | --- | --- | --- |
| 回调 | 高 | 好 | 否 |
| Promise | 中 | 好 | 否 |
| async/await | 低 | 优 | 否 |
| Actor | 低 | 优 | 是 |

> **提示**：善用 TaskGroup 可以动态管理大量并发任务，是处理批量操作的利器。

## 总结

Swift 的现代并发模型完美融合了性能与安全性。掌握 async/await 和 Actor，你就能编写出既优雅又高效的异步代码。
`
  },
  essay: {
    name: '生活随笔',
    content: `# 周末的咖啡馆时光

阳光透过落地窗洒在木质桌面上，
这是一个难得清闲的周末下午。

## 城市的避风港

在快节奏的城市生活中，街角的咖啡馆就像是一个小小的避风港。推开门，伴随着清脆的风铃声，浓郁的咖啡豆香气扑面而来。

> 生活不是为了赶路，而是为了感受路上的风景。

### 今日点单

* **手冲耶加雪菲** - 带有淡淡的柑橘酸甜，口感干净明亮
* **海盐海绵蛋糕** - 微咸的奶油中和了蛋糕的甜腻，恰到好处
* **冰美式** - 简单纯粹，苦中带香

## 慢下来的意义

平时我们总是在追赶 DDl，回复不完的消息，处理不完的邮件。只有在这样的时刻，时间才真正属于自己。

1. 翻开一本买来许久却没时间看的书
2. 在笔记本上随意写下几句感悟
3. 仅仅是看着窗外匆匆走过的人群发呆

::: focus
偶尔慢下来，才能走得更远。
:::

## 窗外的风景

阳光的角度在慢慢变化，从正午的炽热变成了午后的温柔。咖啡馆里的人来来往往，每个人都有自己的故事。

| 时间 | 场景 | 心情 |
| --- | --- | --- |
| 12:00 | 刚进门 | 疲惫 |
| 13:00 | 喝第一口咖啡 | 放松 |
| 15:00 | 看完半本书 | 平静 |
| 17:00 | 离开 | 充实 |

::: timeline
10:00 抵达咖啡馆
选了一个靠窗的位置
---
12:00 午餐时间
点了一份简餐和手冲
---
15:00 阅读时光
沉浸在书中的世界
---
17:00 离开
带着满足感回家
:::

或许，我们需要经常给自己按下「暂停键」，才能更好地继续前行。
`
  },
  product: {
    name: '高级排版示例',
    content: `# 高级排版组件完全指南

本文档展示所有高级排版组件的用法，包括 release、grid、timeline、steps、compare、focus 等组件。

---

## release 组件 - 精选文章卡片

### 默认样式
::: release
# 写作是最好的自我投资
写作不仅仅是文字的排列组合，更是思维的梳理和情感的表达。每一位写作者都在用自己的方式影响世界。
:::

### 自定义参数
::: release 周刊 精选 原创 深度 思考
# 如何提升思考深度
在这个信息爆炸的时代，我们每天被各种碎片化的信息包围。真正的深度思考能力，成为了一种稀缺而珍贵的能力。
:::

---

## grid 组件 - 多列网格布局

### 默认 PART 前缀
::: grid
晨光
清晨的第一缕阳光，温柔地唤醒沉睡的城市
---
午后
慵懒的午后时光，一杯咖啡一段文字
---
黄昏
落日余晖洒满窗台，思绪随风飘远
:::

### 自定义前缀
::: grid 章节
第一章
觉醒 - 当你开始意识到时间的珍贵
---
第二章
行动 - 从此刻开始，不再等待
---
第三章
坚持 - 重复的力量，时间的复利
:::

---

## timeline 组件 - 时间线布局

### 项目里程碑
::: timeline
2024-01 需求分析
完成市场调研和用户访谈
---
2024-02 产品设计
交互原型评审，视觉稿定稿
---
2024-03 技术开发
核心功能开发，敏捷迭代
---
2024-04 测试上线
全量发布，用户反馈收集
:::

---

## steps 组件 - 步骤指示器

### 三步学习法
::: steps
第一步 广泛涉猎
快速阅读大量相关资料，建立整体认知框架
---
第二步 深度研究
针对核心主题进行深入阅读和思考
---
第三步 实践输出
将所学知识用于实践，形成自己的见解
:::

---

## compare 组件 - 对比布局

### 方案 A vs 方案 B
::: compare
**方案 A：渐进式改变**
- 低风险，易于执行
- 短期效果不明显
- 适合组织变革
- 需要长期坚持
---
**方案 B：激进式重构**
- 高风险，可能颠覆
- 短期效果显著
- 适合初创公司
- 需要强执行力
:::

---

## focus 组件 - 金句卡片

### 核心观点强调
::: focus
种一棵树最好的时间是十年前，其次是现在。
:::

::: focus
**成功的秘诀**在于持续做那些微小的、看似无关紧要的事情。
:::

---

## 苹果风格代码块

\`\`\`swift
import UIKit

class ViewController: UIViewController {
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "Hello, World!"
        label.textColor = .label
        label.textAlignment = .center
        label.font = .systemFont(ofSize: 24, weight: .bold)
        return label
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(titleLabel)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            titleLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
}
\`\`\`

\`\`\`python
import asyncio
from typing import List, Optional

class AsyncFetcher:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._cache: dict = {}
    
    async def fetch(self, url: str) -> Optional[dict]:
        if url in self._cache:
            return self._cache[url]
        
        async with asyncio.timeout(self.timeout):
            response = await self._request(url)
            self._cache[url] = response
            return response
    
    async def _request(self, url: str) -> dict:
        # 实现请求逻辑
        pass
\`\`\`

---

## 标准 Markdown 元素

### 引用块
> 好的设计是尽可能少的设计。
> — 迪特·拉姆斯

### 表格
| 组件 | 用途 | 难度 |
| --- | --- | --- |
| release | 精选卡片 | ⭐⭐ |
| grid | 多列布局 | ⭐ |
| timeline | 时间线 | ⭐⭐ |
| steps | 步骤指示 | ⭐⭐ |
| compare | 对比展示 | ⭐⭐ |
| focus | 金句强调 | ⭐ |

### 有序列表
1. 第一步：选择合适的组件
2. 第二步：填充内容
3. 第三步：调整参数
4. 第四步：预览效果

感谢阅读！
`
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
