from __future__ import annotations

import html
import importlib.util
import json
import os
from pathlib import Path


# Project root resolution:
#   1) LOOKUP_ROOT environment variable (explicit override)
#   2) Default to 4 levels up from this script (the writing-prep workspace)
# This lets the script work from any clone location without hard-coding paths.
_ENV_ROOT = os.environ.get("LOOKUP_ROOT")
ROOT = Path(_ENV_ROOT).resolve() if _ENV_ROOT else Path(__file__).resolve().parents[4]

OUT_DIR = ROOT / "outputs/manual-20260525/teacher-lookup"
HTML_PATH = OUT_DIR / "IELTS_Writing_教师讲解检索入口.html"
AUDIT_PATH = OUT_DIR / "teacher_lookup_audit.json"
STUDENT_BUILDER = ROOT / "outputs/manual-20260525/student-practice-word/scripts/build_student_practice_docx.py"
TASK1_HTML = ROOT / "outputs/manual-20260523/task1-all-lessons-full-html/index.html"
TASK2_HTML = ROOT / "Context/html/Task2_大作文总整合入口.html"


def _rel_to_root(path: Path) -> str:
    """Return path relative to ROOT if possible, else the absolute string.

    Used in audit output so generated JSON doesn't leak absolute local paths.
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_student_builder():
    spec = importlib.util.spec_from_file_location("student_builder", STUDENT_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {STUDENT_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def relative_href(target: Path, anchor: str) -> str:
    return Path(os.path.relpath(target, OUT_DIR)).as_posix() + anchor


def task1_position(item: dict) -> str:
    return f"图表作文练习 > {item['chartCategory']} > 第 {item['displayNo']:02d} 题"


def task2_position(item: dict) -> str:
    return f"大作文练习 > {item['topicGroup']} > 第 {item['displayNo']:02d} 题"


def flatten_task1_details(item: dict) -> str:
    parts: list[str] = []
    data = item.get("data") or []
    for row in data:
        if isinstance(row, (list, tuple)):
            parts.extend(str(cell) for cell in row)
        else:
            parts.append(str(row))
    steps = item.get("steps") or []
    for step in steps:
        if isinstance(step, dict):
            parts.extend(str(value) for value in step.values())
        else:
            parts.append(str(step))
    return " ".join(parts)


def build_html(task1: list[dict], task2: list[dict]) -> str:
    task1_rows = []
    for item in task1:
        anchor = f"#t{item['id']}"
        href = relative_href(TASK1_HTML, anchor)
        detail_text = flatten_task1_details(item)
        searchable = " ".join(
            [
                task1_position(item),
                item["title"],
                item.get("cnTitle", ""),
                item.get("subtype", ""),
                item.get("prompt", ""),
                detail_text,
            ]
        )
        task1_rows.append(
            f"""
            <tr data-search="{esc(searchable)}" data-kind="chart" data-position="{esc(task1_position(item))}" data-title="{esc(item['title'])}" data-type="{esc(item['subtype'] or item['type'])}" data-prompt="{esc(item['prompt'])}" data-anchor="{esc(anchor)}" data-href="{esc(href)}">
              <td><strong>{esc(task1_position(item))}</strong><small>原讲解锚点：{esc(anchor)}</small></td>
              <td>{esc(item['title'])}<small>{esc(item.get('cnTitle', ''))}</small></td>
              <td>{esc(item['subtype'] or item['type'])}</td>
              <td>{esc(item['prompt'])}</td>
              <td><a class="btn" href="{esc(href)}">打开讲解</a></td>
            </tr>
            """
        )

    task2_rows = []
    for item in task2:
        anchor = f"#topic-{item['id']:02d}"
        href = relative_href(TASK2_HTML, anchor)
        searchable = " ".join(
            [
                task2_position(item),
                item["title"],
                item.get("typeGroup", ""),
                item.get("rawType", ""),
                item.get("prompt", ""),
            ]
        )
        task2_rows.append(
            f"""
            <tr data-search="{esc(searchable)}" data-kind="essay" data-position="{esc(task2_position(item))}" data-title="{esc(item['title'])}" data-type="{esc(item['typeGroup'])}" data-prompt="{esc(item['prompt'])}" data-anchor="{esc(anchor)}" data-href="{esc(href)}">
              <td><strong>{esc(task2_position(item))}</strong><small>原讲解锚点：{esc(anchor)}</small></td>
              <td>{esc(item['title'])}</td>
              <td>{esc(item['typeGroup'])}</td>
              <td>{esc(item['prompt'])}</td>
              <td><a class="btn" href="{esc(href)}">打开讲解</a></td>
            </tr>
            """
        )

    task1_groups = {}
    for item in task1:
        task1_groups.setdefault(item["chartCategory"], []).append(item)
    task2_groups = {}
    for item in task2:
        task2_groups.setdefault(item["topicGroup"], []).append(item)

    task1_group_links = "".join(
        f'<a href="#chart-all" data-kind="chart" data-query="图表作文练习 > {esc(name)}">{esc(name)} <span>{len(items)}</span></a>'
        for name, items in task1_groups.items()
    )
    task2_group_links = "".join(
        f'<a href="#essay-all" data-kind="essay" data-query="大作文练习 > {esc(name)}">{esc(name)} <span>{len(items)}</span></a>'
        for name, items in task2_groups.items()
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>IELTS Writing 教师讲解检索入口</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #5d6978;
      --line: #d9dee7;
      --pale: #f5f7fb;
      --blue: #2e74b5;
      --blue-dark: #1f5f99;
      --paper: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
      color: var(--ink);
      background: #f2f4f8;
      line-height: 1.55;
    }}
    header {{
      background: var(--paper);
      border-bottom: 1px solid var(--line);
      padding: 28px 32px 22px;
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 28px;
      line-height: 1.2;
    }}
    .sub {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .searchbar {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 10px;
      align-items: center;
    }}
    input {{
      width: 100%;
      border: 1px solid #b8c4d4;
      border-radius: 8px;
      padding: 12px 14px;
      font-size: 16px;
      outline: none;
      background: #fff;
    }}
    input:focus {{ border-color: var(--blue); box-shadow: 0 0 0 3px rgba(46,116,181,.14); }}
    button, .toggle {{
      border: 1px solid #b8c4d4;
      background: #fff;
      color: var(--ink);
      border-radius: 8px;
      padding: 11px 14px;
      font-size: 14px;
      cursor: pointer;
    }}
    button.active, .toggle.active {{
      background: var(--blue);
      border-color: var(--blue);
      color: #fff;
    }}
    .quick-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }}
    .quick-tags button {{
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 13px;
      color: var(--blue-dark);
      background: #f7fbff;
      border-color: #c7d7ea;
    }}
    main {{ padding: 24px 32px 48px; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .card h2 {{
      margin: 0 0 10px;
      font-size: 18px;
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .links a {{
      color: var(--blue-dark);
      border: 1px solid #c8d5e6;
      background: #f9fbfe;
      padding: 6px 9px;
      border-radius: 7px;
      text-decoration: none;
      font-size: 13px;
    }}
    .links span {{ color: var(--muted); margin-left: 3px; }}
    .live-panel {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 18px 0;
      overflow: hidden;
    }}
    .live-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfcfe;
    }}
    .live-head h2 {{
      margin: 0;
      font-size: 20px;
    }}
    .live-head span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .result-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      padding: 14px;
    }}
    .result-card {{
      border: 1px solid #d4dcea;
      border-radius: 8px;
      background: #fff;
      padding: 14px;
    }}
    .result-card:hover {{ border-color: #9ab5d6; }}
    .result-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 12px;
    }}
    .pill {{
      display: inline-block;
      border: 1px solid #d4dcea;
      background: #f7f9fc;
      border-radius: 999px;
      padding: 2px 8px;
    }}
    .result-title {{
      margin: 0 0 8px;
      font-size: 17px;
      font-weight: 700;
      line-height: 1.35;
    }}
    .result-prompt {{
      margin: 0 0 12px;
      color: #334155;
      font-size: 13px;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .empty-state {{
      padding: 24px;
      color: var(--muted);
      font-size: 14px;
    }}
    section {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 18px 0;
      overflow: hidden;
    }}
    section h2 {{
      margin: 0;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      font-size: 22px;
      background: #fbfcfe;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 13px 12px;
      vertical-align: top;
      text-align: left;
      font-size: 14px;
    }}
    th {{
      color: #334155;
      background: var(--pale);
      font-weight: 700;
    }}
    th:nth-child(1), td:nth-child(1) {{ width: 23%; }}
    th:nth-child(2), td:nth-child(2) {{ width: 20%; }}
    th:nth-child(3), td:nth-child(3) {{ width: 14%; }}
    th:nth-child(4), td:nth-child(4) {{ width: 32%; }}
    th:nth-child(5), td:nth-child(5) {{ width: 11%; }}
    small {{
      display: block;
      color: var(--muted);
      margin-top: 4px;
      font-size: 12px;
    }}
    .btn {{
      display: inline-block;
      padding: 7px 10px;
      border-radius: 7px;
      background: var(--blue);
      color: #fff;
      text-decoration: none;
      font-size: 13px;
      white-space: nowrap;
    }}
    .btn:hover {{ background: var(--blue-dark); }}
    .hidden {{ display: none; }}
    .count {{ color: var(--muted); font-weight: 400; font-size: 14px; margin-left: 8px; }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .searchbar {{ grid-template-columns: 1fr; }}
      .summary {{ grid-template-columns: 1fr; }}
      table, thead, tbody, tr, th, td {{ display: block; width: 100% !important; }}
      thead {{ display: none; }}
      tr {{ border-bottom: 1px solid var(--line); padding: 10px 0; }}
      td {{ border-bottom: 0; padding: 8px 12px; }}
      td::before {{ content: attr(data-label); display: block; color: var(--muted); font-size: 12px; margin-bottom: 2px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>IELTS Writing 教师讲解检索入口</h1>
    <p class="sub">按学生练习题册的位置检索，一键跳到对应老师讲解 HTML。小作文已处理“学生版分类排序”和“旧讲解页原始编号”的转换。</p>
    <div class="searchbar">
      <input id="search" placeholder="输入学生版题号、分类、标题或题干关键词，例如：静态图 第 01、Gap year、water heating、social networking">
      <button class="toggle active" data-filter="all">全部</button>
      <button class="toggle" data-filter="chart">图表作文</button>
      <button class="toggle" data-filter="essay">大作文</button>
    </div>
    <div class="quick-tags">
      <button data-query="静态图 第 01">静态图 第 01</button>
      <button data-query="Gap year">Gap year</button>
      <button data-query="water heating">water heating</button>
      <button data-query="social networking">social networking</button>
      <button data-query="地图题">地图题</button>
      <button data-query="儿童广告">儿童广告</button>
    </div>
  </header>
  <main>
    <div class="summary">
      <div class="card">
        <h2>图表作文练习：{len(task1)} 题</h2>
        <div class="links">{task1_group_links}</div>
      </div>
      <div class="card">
        <h2>大作文练习：{len(task2)} 题</h2>
        <div class="links">{task2_group_links}</div>
      </div>
    </div>

    <div class="live-panel" id="live-panel">
      <div class="live-head">
        <h2>即时搜索结果</h2>
        <span id="live-count">输入关键词后显示匹配题目</span>
      </div>
      <div id="live-results" class="result-grid">
        <div class="empty-state">可以搜索题号、分类、标题、题干关键词或题型。例：`静态图 第 01`、`Gap year`、`water heating`、`social networking`。</div>
      </div>
    </div>

    <section id="chart-all">
      <h2>图表作文对应表 <span class="count" id="chart-count"></span></h2>
      <table>
        <thead><tr><th>学生版位置</th><th>标题</th><th>图表类型</th><th>题目</th><th>讲解页</th></tr></thead>
        <tbody>{''.join(task1_rows)}</tbody>
      </table>
    </section>

    <section id="essay-all">
      <h2>大作文对应表 <span class="count" id="essay-count"></span></h2>
      <table>
        <thead><tr><th>学生版位置</th><th>标题</th><th>题型</th><th>题目</th><th>讲解页</th></tr></thead>
        <tbody>{''.join(task2_rows)}</tbody>
      </table>
    </section>
  </main>
  <script>
    const search = document.getElementById('search');
    const toggles = [...document.querySelectorAll('.toggle')];
    const rows = [...document.querySelectorAll('tbody tr')];
    const chartCount = document.getElementById('chart-count');
    const essayCount = document.getElementById('essay-count');
    const liveCount = document.getElementById('live-count');
    const liveResults = document.getElementById('live-results');
    let filter = 'all';

    for (const cell of document.querySelectorAll('tbody tr')) {{
      const labels = ['学生版位置', '标题', '类型', '题目', '讲解页'];
      [...cell.children].forEach((td, index) => td.setAttribute('data-label', labels[index] || ''));
    }}

    function escapeHtml(value) {{
      return String(value || '').replace(/[&<>"']/g, char => ({{
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }}[char]));
    }}

    function normalizeText(value) {{
      return String(value || '')
        .toLowerCase()
        .replace(/第\\s*0+(\\d+)\\s*题/g, '第$1题')
        .replace(/[\\s,，.。:：;；/\\\\|\\-—_>]+/g, '')
        .replace(/第0+(\\d+)/g, '第$1');
    }}

    function matches(row, rawQuery) {{
      const q = rawQuery.trim();
      if (!q) return true;
      const raw = (row.dataset.search || '').toLowerCase();
      const position = (row.dataset.position || '').toLowerCase();

      function matchQuestionNumber(n) {{
        const padded = String(n).padStart(2, '0');
        return position.includes(`第 ${{padded}} 题`);
      }}

      // Pure-digit query ("1", "01", "05") → interpret as "find question N".
      // Constrained to 1-30 to avoid false positives against years (1970, 2002) and percentages in chart data.
      const pureDigit = q.match(/^0*(\\d+)$/);
      if (pureDigit) {{
        const n = parseInt(pureDigit[1], 10);
        if (n >= 1 && n <= 30) return matchQuestionNumber(n);
      }}

      const rawNorm = normalizeText(raw);
      const qNorm = normalizeText(q);
      if (rawNorm.includes(qNorm)) return true;
      const rawNoLeadingZero = rawNorm.replace(/第0+(\\d+)题/g, '第$1题');
      const qNoLeadingZero = qNorm.replace(/第0+(\\d+)题/g, '第$1题');
      if (rawNoLeadingZero.includes(qNoLeadingZero)) return true;

      // Multi-token: digit tokens match question numbers only; non-digit tokens use fuzzy match.
      const tokens = q.toLowerCase().split(/\\s+/).filter(t => t.length > 0);
      if (!tokens.length) return false;
      return tokens.every(token => {{
        if (/^\\d+$/.test(token)) {{
          const n = parseInt(token, 10);
          if (n >= 1 && n <= 30) return matchQuestionNumber(n);
          return raw.includes(token);
        }}
        if (token === '第' || token === '题') return true;
        const tnorm = normalizeText(token);
        if (tnorm.length < 2) return false;
        return rawNorm.includes(tnorm) || raw.includes(token);
      }});
    }}

    function renderLiveResults(visibleRows, rawQuery) {{
      const q = rawQuery.trim();
      if (!q) {{
        liveCount.textContent = '输入关键词后显示匹配题目';
        liveResults.className = 'result-grid';
        liveResults.innerHTML = '<div class="empty-state">可以搜索题号、分类、标题、题干关键词或题型。例：`静态图 第 01`、`Gap year`、`water heating`、`social networking`。</div>';
        return;
      }}
      liveCount.textContent = `找到 ${{visibleRows.length}} 道匹配题目`;
      if (!visibleRows.length) {{
        liveResults.className = '';
        liveResults.innerHTML = '<div class="empty-state">没有匹配结果。可以换成英文关键词、题目里的核心名词，或直接搜分类和题号。</div>';
        return;
      }}
      liveResults.className = 'result-grid';
      liveResults.innerHTML = visibleRows.slice(0, 12).map(row => {{
        const kindName = row.dataset.kind === 'chart' ? '图表作文' : '大作文';
        const prompt = row.dataset.prompt || '';
        const promptText = prompt.length > 220 ? prompt.slice(0, 220) + '...' : prompt;
        return `
          <article class="result-card">
            <div class="result-meta">
              <span class="pill">${{escapeHtml(kindName)}}</span>
              <span class="pill">${{escapeHtml(row.dataset.type)}}</span>
              <span class="pill">${{escapeHtml(row.dataset.anchor)}}</span>
            </div>
            <p class="result-title">${{escapeHtml(row.dataset.position)}}<br>${{escapeHtml(row.dataset.title)}}</p>
            <p class="result-prompt">${{escapeHtml(promptText)}}</p>
            <a class="btn" href="${{escapeHtml(row.dataset.href)}}">打开讲解</a>
          </article>
        `;
      }}).join('');
    }}

    function applyFilter() {{
      const q = search.value.trim();
      let chartVisible = 0;
      let essayVisible = 0;
      const visibleRows = [];
      for (const row of rows) {{
        const kind = row.dataset.kind;
        const show = (filter === 'all' || filter === kind) && matches(row, q);
        row.classList.toggle('hidden', !show);
        if (show) {{
          visibleRows.push(row);
          if (kind === 'chart') chartVisible++;
          if (kind === 'essay') essayVisible++;
        }}
      }}
      chartCount.textContent = `当前显示 ${{chartVisible}} 题`;
      essayCount.textContent = `当前显示 ${{essayVisible}} 题`;
      document.getElementById('chart-all').classList.toggle('hidden', filter === 'essay');
      document.getElementById('essay-all').classList.toggle('hidden', filter === 'chart');
      renderLiveResults(visibleRows, q);
    }}

    toggles.forEach(btn => {{
      btn.addEventListener('click', () => {{
        filter = btn.dataset.filter;
        toggles.forEach(b => b.classList.toggle('active', b === btn));
        applyFilter();
      }});
    }});
    document.querySelectorAll('.links a').forEach(link => {{
      link.addEventListener('click', () => {{
        search.value = link.dataset.query || '';
        filter = link.dataset.kind || 'all';
        toggles.forEach(b => b.classList.toggle('active', b.dataset.filter === filter));
        applyFilter();
      }});
    }});
    document.querySelectorAll('.quick-tags button').forEach(btn => {{
      btn.addEventListener('click', () => {{
        search.value = btn.dataset.query || '';
        filter = 'all';
        toggles.forEach(b => b.classList.toggle('active', b.dataset.filter === 'all'));
        applyFilter();
        document.getElementById('live-panel').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }});
    }});
    search.addEventListener('input', applyFilter);
    applyFilter();
  </script>
</body>
</html>
"""


def verify_anchors(task1: list[dict], task2: list[dict]) -> dict:
    task1_text = TASK1_HTML.read_text(encoding="utf-8")
    task2_text = TASK2_HTML.read_text(encoding="utf-8")
    missing_task1 = [f"t{item['id']}" for item in task1 if f'id="t{item["id"]}"' not in task1_text]
    missing_task2 = [f"topic-{item['id']:02d}" for item in task2 if f'id="topic-{item["id"]:02d}"' not in task2_text]
    return {
        "task1_count": len(task1),
        "task2_count": len(task2),
        "missing_task1_anchors": missing_task1,
        "missing_task2_anchors": missing_task2,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    builder = load_student_builder()
    task1 = builder.extract_task1_topics()
    task2 = builder.extract_task2_topics()
    for idx, item in enumerate(task1, 1):
        item["displayNo"] = idx
    for idx, item in enumerate(task2, 1):
        item["displayNo"] = idx
    HTML_PATH.write_text(build_html(task1, task2), encoding="utf-8")
    audit = verify_anchors(task1, task2)
    audit.update(
        {
            # Paths recorded relative to ROOT so the audit JSON stays portable.
            "html": _rel_to_root(HTML_PATH),
            "task1_html": _rel_to_root(TASK1_HTML),
            "task2_html": _rel_to_root(TASK2_HTML),
            "task1_groups": {k: len(v) for k, v in builder.grouped(task1, "chartCategory").items()},
            "task2_groups": {k: len(v) for k, v in builder.grouped(task2, "topicGroup").items()},
        }
    )
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
