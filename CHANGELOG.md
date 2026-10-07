# Changelog

## [0.1.0] - 2026-09-28

首个版本。

### 内容

- **SKILL.md** — 判断规则，五组（干预强度 / 落点优先级 / 动效语义 / 测量 / 边界），每条为「规则 / 为什么 / 反例」
- **DESIGN.md** — 可移植规格：frontmatter token（motion / intervention / feedback / typography / measurement / disclosure）+ 散文立场（Direction / Mood / Decisions Log / Refusals）
- **references/refusal-list.md** — 八条拒绝 + 例外 + 冲突优先级
- **references/cases.md** — 三个案例，展示规则如何改变决定
- **scripts/validate.py** — 自检：spec 格式、规则三段完整性、**泄露扫描**、脚本安全性、体积上限

### 设计决定

- **印记来自拒绝，不来自功能** — 核心是那八条"不做"
- **每条规则必须带反例** — 缺"为什么"的条目是偏好，不是规则；验证器会拦
- **泄露扫描的词表放在本地** — 机制进仓库，身份词不进仓库
- **不预置品牌色/字体** — 只给可判定 token（时长、阈值、字数），视觉留给使用者

### 已知未覆盖

静态检查只能证明文件自洽，不能证明判断质量。行为层验证未建立。
