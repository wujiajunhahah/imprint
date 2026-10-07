#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imprint 自检（Tier 1，免费、<2s、不联网）。

重点检查三件事：
1. DESIGN.md 的 spec 格式是否完整（token 是规范性内容，缺了等于规格失效）
2. 规则表是否保持「规则 / 为什么 / 反例」三段——缺「为什么」会退化成教条
3. 有没有身份泄露（开盒防护）——通用模式 + 本地词表（词表不进仓库）

用法：
  python3 scripts/validate.py
  python3 scripts/validate.py --quiet
退出码：0 = 全过；1 = 有失败。
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 体积上限（ratchet）：超了就拆分，不要放宽阈值
SIZE_CAPS = {
    'SKILL.md': 180,
    'DESIGN.md': 200,
    'README.md': 160,
    'AGENTS.md': 120,
    'references/refusal-list.md': 160,
    'references/cases.md': 160,
}

# DESIGN.md frontmatter 必须有的键
REQUIRED_SPEC_KEYS = ['motion', 'intervention', 'feedback', 'typography',
                      'measurement', 'disclosure']

# 通用泄露模式（任何人都不该出现在可发布的品味套件里）
LEAK_PATTERNS = [
    (r'(?<!\d)1[3-9]\d{9}(?!\d)', '中国大陆手机号'),
    (r'(?<!\d)\d{17}[\dXx](?!\d)', '身份证号'),
    (r'[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '邮箱地址'),
    (r'ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{16,}', '凭据'),
    (r'https?://(?!github\.com/(VoltAgent|emilkowalski)|example\.com)[^\s)\]]*\.(space|me|im|cn|com)(?=[/\s)\]]|$)',
     '个人站点链接（请用 example.com 占位）'),
]

# 允许出现的公开引用（外部参考，非个人信息）
LEAK_ALLOW = [
    r'github\.com/VoltAgent',
    r'github\.com/emilkowalski',
    r'example\.com',
]

# 本地词表：把自己的姓名 / 项目名 / 域名写进 .leak-terms.local（已 gitignore）
LOCAL_TERMS_FILE = os.path.join(ROOT, '.leak-terms.local')

FORBIDDEN_SCRIPT_PATTERNS = [
    (r'https?://|urllib|requests\.|\bcurl\b|\bwget\b', '网络调用'),
    (r'\bsudo\b|rm\s+-rf\s+/', '提权 / 危险删除'),
    (r'analytics|telemetry\s*=|\.track\(', '遥测'),
]


def rel(p):
    return os.path.relpath(p, ROOT)


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    return m.group(1) if m else None


def check(name, fn, quiet):
    try:
        problems = fn()
    except Exception as e:
        problems = [f'检查器异常: {type(e).__name__}: {e}']
    ok = not problems
    if not ok or not quiet:
        print(f'[{"PASS" if ok else "FAIL"}] {name}')
    for p in problems:
        print(f'    - {p}')
    return ok


# ---------------------------------------------------------------- 检查项

def c_spec_format():
    """DESIGN.md 必须是 spec 格式，且必需 token 齐全。"""
    out = []
    f = os.path.join(ROOT, 'DESIGN.md')
    if not os.path.exists(f):
        return ['DESIGN.md 缺失']
    t = read(f)
    if 'design-md-format=spec' not in t:
        out.append('缺少 `design-md-format=spec` 标记（格式不可判定）')
    fm = parse_frontmatter(t)
    if not fm:
        return out + ['DESIGN.md 没有 frontmatter（token 必须是机器可读的）']
    for key in REQUIRED_SPEC_KEYS:
        if not re.search(rf'^{key}\s*:', fm, re.M):
            out.append(f'DESIGN.md frontmatter 缺必需键: {key}')
    for need in ['Direction', 'Mood', 'Decisions Log', 'Refusals']:
        if need.lower() not in t.lower():
            out.append(f'DESIGN.md 缺散文段落: {need}')
    if not re.search(r'^## Decisions Log', t, re.M) and 'decisions log' not in t.lower():
        out.append('DESIGN.md 缺 Decisions Log（这是规格里最重要的部分）')
    return out


def c_rule_three_parts():
    """规则表必须是「规则 / 为什么 / 反例」三段；反例列不得为空。"""
    out = []
    f = os.path.join(ROOT, 'SKILL.md')
    t = read(f)
    lines = t.split('\n')
    i, tables, empty_cells, dash_only = 0, 0, 0, 0
    while i < len(lines):
        if lines[i].strip().startswith('|') and i + 1 < len(lines) and \
                re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if '规则' not in ' '.join(header) or '为什么' not in ' '.join(header):
                i += 1
                continue
            tables += 1
            if len(header) < 3:
                out.append(f'SKILL.md: 规则表缺「反例」列（表头: {" | ".join(header)}）')
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if len(cells) >= 3:
                    third = cells[2]
                    if not third:
                        empty_cells += 1
                        out.append(f'SKILL.md: 规则「{cells[0][:20]}」的反例列为空')
                    elif third in ('—', '-', '--', '无'):
                        dash_only += 1
                i += 1
            continue
        i += 1
    if tables == 0:
        out.append('SKILL.md 里没找到规则表（规则 / 为什么 / 反例）')
    if tables and dash_only > tables * 3:      # 粗判：反例几乎全填「—」等于没有
        out.append(f'反例列有 {dash_only} 处只写了「—」，规则正在退化成教条，请补真实例外')
    return out


def c_leak_scan():
    """开盒防护：通用模式 + 本地词表。"""
    out = []
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules')]
        for n in names:
            if n.endswith(('.md', '.py', '.sh', '.yml', '.yaml', '.txt')):
                files.append(os.path.join(base, n))

    local_terms = []
    if os.path.exists(LOCAL_TERMS_FILE):
        local_terms = [l.strip() for l in read(LOCAL_TERMS_FILE).split('\n')
                       if l.strip() and not l.strip().startswith('#')]

    for f in sorted(files):
        if os.path.basename(f) == '.leak-terms.local':
            continue
        t = read(f)
        for pat, label in LEAK_PATTERNS:
            for m in re.finditer(pat, t):
                hit = m.group(0)
                if any(re.search(a, hit) for a in LEAK_ALLOW):
                    continue
                out.append(f'{rel(f)}: 命中{label} → {hit[:40]}')
        for term in local_terms:
            if term in t:
                out.append(f'{rel(f)}: 命中本地词表「{term}」（这属于身份信息，不该出现在可发布内容里）')
    if not local_terms:
        # 提示而非失败：干净 clone / CI 环境下本来就没有本地词表
        print('    （提示）未找到 .leak-terms.local。建议把你自己的姓名/项目名/域名'
              '写进去再跑一次 —— 该文件不进仓库，但能挡住"开盒"。')
    return out


def c_scripts_safe():
    """扫描 scripts/ 下可执行脚本。

    跳过两类不构成违规的内容：
    - 注释与说明文字
    - 模式定义行（本文件自身的 LEAK_PATTERNS / FORBIDDEN_SCRIPT_PATTERNS
      里必然包含这些关键词，扫自己会永远报错）
    """
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, 'scripts'))):
        p = os.path.join(ROOT, 'scripts', f)
        if not os.path.isfile(p) or not f.endswith(('.py', '.sh')):
            continue
        src_lines = read(p).split('\n')
        t = '\n'.join(src_lines)
        in_pattern_block = False
        for pat, label in FORBIDDEN_SCRIPT_PATTERNS:
            for m in re.finditer(pat, t):
                line = t[:m.start()].count('\n') + 1
                ctx = src_lines[line - 1].strip()
                if ctx.startswith('#') or '不允许' in ctx or '禁止' in ctx:
                    continue
                # 模式定义行：形如 (r'...', '标签')，是扫描器自己的规则表
                if re.match(r"^[\(\[]?\s*r?['\"]", ctx) and ctx.rstrip().endswith((",", ")")):
                    continue
                if 'FORBIDDEN_SCRIPT_PATTERNS' in ctx or 'LEAK_PATTERNS' in ctx:
                    continue
                out.append(f'{rel(p)}:{line}: 命中{label} → {ctx[:50]}')
    return out


def c_size_caps():
    out = []
    for relp, cap in SIZE_CAPS.items():
        f = os.path.join(ROOT, relp)
        if not os.path.exists(f):
            out.append(f'{relp} 缺失')
            continue
        n = sum(1 for _ in open(f, encoding='utf-8'))
        if n > cap:
            out.append(f'{relp}: {n} 行 > 上限 {cap}（拆分，不要放宽阈值）')
    return out


def c_refs():
    out = []
    for f in ['SKILL.md', 'README.md', 'AGENTS.md', 'DESIGN.md',
              'references/refusal-list.md', 'references/cases.md']:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            continue
        t = read(p)
        for ref in set(re.findall(r'`(references/[a-z-]+\.md|DESIGN\.md|SKILL\.md|AGENTS\.md)`', t)):
            if not os.path.exists(os.path.join(ROOT, ref)):
                out.append(f'{f} 引用了不存在的 {ref}')
    return out


CHECKS = [
    ('DESIGN.md 是完整 spec（token 齐 + 立场段齐）', c_spec_format),
    ('规则表保持三段（规则/为什么/反例）', c_rule_three_parts),
    ('泄露扫描（通用模式 + 本地词表）', c_leak_scan),
    ('脚本无网络 / 提权 / 遥测', c_scripts_safe),
    ('体积 ratchet', c_size_caps),
    ('交叉引用有效', c_refs),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    print(f'imprint 自检 · {ROOT}\n')
    results = [check(n, f, a.quiet) for n, f in CHECKS]
    passed, total = sum(results), len(results)
    print(f'\n{passed}/{total} 通过')
    if passed < total:
        print('STATUS: BLOCKED — 先修上面的失败项')
        return 1
    print('STATUS: DONE — Tier 1 全过（未做行为验证）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
