# IELTS Writing Teacher Lookup Portal
### 雅思写作教师备课检索入口

> **用 LLM 把老师手头杂乱的备课笔记，整理成上课能用的可视化、高效、简洁、明了的检索界面。**
> An LLM-assisted workflow that turns a teacher's scattered writing prep notes into a clean, searchable, one-page lookup portal usable mid-class.
>
> 本仓库以雅思写作备课为实例，但核心逻辑同样适用于 TOEFL / GRE / 四六级 / 考研写作 等任意"题目集 + 多版本讲解"的英文写作辅导场景。
> Built around IELTS writing prep as a worked example — the same workflow applies to TOEFL, GRE, college-level English writing coaching, and any context with "a question bank × multiple explanation passes".

<p>
  <a href="#中文">简体中文</a> ·
  <a href="#english">English</a> ·
  <a href="docs/WORKFLOW_INSIGHTS.md"><b>📓 Workflow Insights</b></a> ·
  <a href="LIVE_DEMO_URL_TBD"><b>🚀 Live Demo</b></a>
</p>

![demo placeholder — 2 秒动画：搜索框输入 "第 01" → 即时跳出对应题](docs/demo.gif)

---

## 中文

### 这是什么

老师在备课和讲课时常常被一个细节绊住——
讲解材料散在 Word、HTML、PPT 多个文件里，学生临场问"老师第 X 题怎么讲"，老师在讲台上要 3 秒内找到，但实际要翻 2-3 个文件。

这个项目把 "学生练习题册位置 ↔ 老师讲解锚点" 做成一页可搜索 HTML：

- 输入 **"第 01"**、**"01"**、**"Gap year"** 都能命中
- 一键跳转到对应讲解段
- 纯静态，可 GitHub Pages 托管，可 USB 拷给同事

**这不是搜索引擎，是教师讲台上的快速定位器。**

> 仓库的演示数据用的是雅思写作题库；但同样的代码可以装载托福独立写作、GRE Issue/Argument、四六级写作等任意写作训练题库——只要数据按约定格式准备好。

### 谁会用

- **主要**：英语写作辅导老师（雅思 / TOEFL / GRE / 四六级 / 考研写作等）
- **本仓库实例**：以 IELTS 写作备课为示范，因为作者是雅思写作老师；其他考试可通过替换数据接入
- **衍生**：任何需要"题目集 ↔ 多版本讲解"双向定位的辅导场景
- **不是给学生用的**

### 怎么工作

```
原始备课材料 (Word / Markdown)
        │
        ▼
   Python builder  ───  数据抽取 + HTML 模板渲染
        │
        ▼
   单页 HTML (索引表 + 模糊搜索 + 即时结果卡片)
        │
        ▼
   一键跳转老师讲解锚点
```

**关键设计 3 条：**

1. **模糊搜索**：`第 01` / `第01` / `01` / `Gap year` 都能命中（自带数字-中文标点-空格的归一化）
2. **纯静态**：无后端、无数据库、无依赖，可 GitHub Pages 托管，可 USB 拷给同事
3. **多源 anchor 映射**：处理"学生版排序 ≠ 老师讲解页排序"的现实工作流问题

> 详细设计判断、Anti-patterns、可迁移模式见 [**docs/WORKFLOW_INSIGHTS.md**](docs/WORKFLOW_INSIGHTS.md)。

---

## English

### What

A single-page lookup portal for IELTS writing teachers. Type a question number (`第 01`, `01`), category (`static charts`, `essays on media`), or keyword (`Gap year`) — in any common phrasing — and the page instantly finds the matching practice item and jumps to the teacher's prepared explanation.

**Not a search engine. A teacher's mid-class location finder.**

### Why

Lesson materials live scattered across Word, HTML, and PPTX. When a student asks "how should I explain question 7 again?" mid-class, the teacher has about 3 seconds before the moment is gone. This tool collapses that lookup to one click.

### How

```
Source prep notes (Word / Markdown)
        │
        ▼
  Python builder  ───  data extraction + HTML template rendering
        │
        ▼
   Single-page HTML (index table + fuzzy search + instant result cards)
        │
        ▼
   One-click jump to the teacher's explanation anchor
```

**Three design decisions:**

1. **Fuzzy search** — normalizes Chinese/English punctuation and zero-padding so all common phrasings hit
2. **Static-only** — no backend, no database, no build chain; deployable to GitHub Pages or a USB stick
3. **Multi-source anchor mapping** — handles the real-world mismatch between student-facing ordering and teacher-side lesson ordering

> Full design rationale, anti-patterns, and transferable patterns: [**docs/WORKFLOW_INSIGHTS.md**](docs/WORKFLOW_INSIGHTS.md).

---

## 仓库结构 · Repository tour

```
teacher-lookup/
├── README.md                                # ← you are here
├── LICENSE                                  # MIT
├── .gitignore
├── requirements.txt                         # Standard library only; no required deps
├── IELTS_Writing_教师讲解检索入口.html      # The generated single-page lookup portal
├── teacher_lookup_audit.json                # Build audit (relative paths, safe to commit)
├── docs/
│   └── WORKFLOW_INSIGHTS.md                 # 工作流复盘 + 可迁移洞察（核心文档）
├── examples/
│   └── demo.yaml                            # Sample data schema for future YAML pipeline
└── scripts/
    └── build_teacher_lookup.py              # The builder (zero external deps)
```

## 5 分钟跑起来 · Try it

```bash
git clone https://github.com/<user>/ielts-writing-teacher-lookup.git
cd ielts-writing-teacher-lookup

# Standard library only — no pip install required
python scripts/build_teacher_lookup.py

# Open the generated portal
open IELTS_Writing_教师讲解检索入口.html
```

To point the builder at a different project root, set `LOOKUP_ROOT`:

```bash
LOOKUP_ROOT=/path/to/your/prep/workspace python scripts/build_teacher_lookup.py
```

---

## For PMs & Recruiters · 给 AI 教育产品方向同行

我是一名英语写作辅导老师，正在转向 AI 教育产品方向。

我做的不是写代码，是**把老师手头杂乱的备课笔记，整理成上课能用的可视化、高效、简洁、明了的检索界面**。

这个项目从我自己的雅思写作备课流程长出来，但底层的工作流——"题目集 → 多版本讲解 → 课堂秒级定位"——在任何写作辅导场景（雅思 / TOEFL / GRE / 四六级 / 考研写作）都同样成立。

这个过程让我看清楚 3 件事：

1. **教师工具的 UI 阈值比 ToC 产品低 70%**——第一版能跑能搜就够，美化是 v2
2. **LLM 在教学场景的瓶颈不是模型能力，而是教师工作流的颗粒度**——你得理解老师讲台上的 3 秒决策窗口
3. **静态 HTML + Python 生成器，比 SaaS 平台对小团队/单老师场景实用 10 倍**

这个项目代表的能力组合：**领域 know-how × 产品意识 × 能动手交付**。

完整复盘和可迁移模式见 [docs/WORKFLOW_INSIGHTS.md](docs/WORKFLOW_INSIGHTS.md)——8 个 section、5 个可迁移模式、4 条 anti-patterns，把这个项目里没明说的判断都写下来了。

---

## Known limitations · 已知限制

- **No synonyms / pinyin search.** Single-teacher use case doesn't need a full search engine — out of scope.
- **Demo data is intentionally minimal.** Ships with public sample prompts; production deployments load the teacher's own prep notes through a YAML/JSON config.
- **Question-number search constrained to 1–30.** Matches a realistic syllabus size; longer test banks would need adjustment.
- **HTML template is currently inlined in the Python builder.** Future refactor: split template into a separate file under `templates/` once the builder grows past ~1500 lines.

## Roadmap

- [ ] Add Mermaid-rendered workflow diagram in `docs/workflow.md`
- [ ] **Pluggable subject domains** — swap data files to support TOEFL / GRE / 四六级 / 考研写作 (the search and rendering logic stays the same)
- [ ] YAML config support so the builder loads `examples/demo.yaml`-shaped data
- [ ] Optional PWA export for offline classroom use
- [ ] Per-question annotation editor for collaborative prep
- [ ] Extract HTML template + JS to `templates/` for easier customization

## License

**MIT** — free to fork, adapt, use commercially. See [LICENSE](LICENSE).

## 致谢 · Acknowledgments

本项目的架构设计、bug 发现、包装策略由 Claude Code + Codex 协同讨论达成。Codex code review 指出了原始版本的关键 bug（数字搜索 fallback 误匹配），并参与了脱敏策略制定。完整对话脉络见 [docs/WORKFLOW_INSIGHTS.md § 8](docs/WORKFLOW_INSIGHTS.md)。

This project's architecture, bug discovery, and packaging strategy were developed through a back-and-forth between Claude Code and Codex. Codex's code review surfaced the original critical search bug and helped shape the de-identification approach.
