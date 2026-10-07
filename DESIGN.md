---
# imprint: design-md-format=spec
# frontmatter 是规范性的（机器可读）；散文段落是判断依据。
# 把本文件复制进你的项目根目录，让 agent 按它构建与评审界面。
name: imprint-restraint

motion:
  micro: 120ms           # 微交互反馈 100–150
  transition: 200ms      # 状态切换 150–250
  overlay: 260ms         # 模态/抽屉 200–300
  ambient: 5000ms        # 常驻律动周期 4–6s
  hard-limit: 300ms      # 交互类硬上限
  enter-easing: ease-out
  move-easing: ease-in-out
  hover-easing: ease
  ambient-easing: sine
  enter-scale-from: 0.95 # 绝不从 0 起

intervention:
  silent-window: 300s    # 5 分钟内只记录不输出
  cooldown: 1800s        # 同一事项冷却 30 分钟
  escalation: evidence-only   # 仅强风险信号允许明确提示
  quiet-default: true    # 默认静默

feedback:
  placement-priority: [ambient, wearable, screen]   # 屏幕是最后选择
  dashboard: forbidden            # 不做实时数字仪表盘
  focus-mode: binary-only         # 专注态只给"继续/建议暂停"
  notification-style: none        # 不用弹窗

typography:
  body-max-chars: 65
  numerals: tabular               # 数字对齐用 tabular-nums
  underline: links-only
  overused-display-faces: [Inter, Roboto, Arial, Helvetica, Open Sans, Lato]

measurement:
  require-control-group: true
  report-per-item: true           # 逐项给结论，不给单一总分
  require-adversarial-negatives: true
  ship-rule: cut-something        # 门槛测试必须导致砍掉某个功能

spacing:
  2xs: 2px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px

disclosure:
  require-boundary-line: true     # 每条对外陈述配"能证明到哪一步"
  require-exclusion-section: true # 交付物必须写"不包含什么"
  ban: [first-of-its-kind, industry-leading, revolutionary]
---

# Design Spec — Restraint

## Overview

- **这是什么**：一套"克制优先"的产品判断规格，可复制进任何项目
- **给谁用**：给 AI coding agent 读，用来约束它默认的"加功能/加提醒/加动效"倾向
- **Project type**：适用于任何会被用户在**专注状态下长时间使用**的产品（工具、工作台、健康/传感、Agent）
- **不适用于**：游戏、营销落地页、以娱乐为主的消费产品——它们的注意力模型相反

## Direction

**Direction:** Calm / Utilitarian — 功能优先，界面退后，**用户不需要看着它才有效果**

**Decoration level:** Minimal — 装饰只出现在首屏与空态；使用中零装饰

**Mood:** 像一件好用的工具：安静、可靠、不主动说话。用户想起它是因为它帮上了忙，不是因为它打扰过你

**Reference:** 环境光、机械装置的缓慢动作、纸的留白。反面参照：任何以"通知"为核心的产品

**核心张力**：产品想帮忙，但帮忙的方式必须是**让用户更少需要它**。

## Interaction

**默认不出手。** 系统在绝大多数时间什么都不做，只记录。

三级介入，逐级升级，**默认停在第一级**：

| 级别 | 触发 | 表现 |
|---|---|---|
| silent log | 检测到变化 | 无输出 |
| light nudge | 持续恶化 > 5 分钟 | 环境里的最小变化 |
| escalation | 强风险信号 | 明确提示 |

**原则名：evidence before interruption** —— 有跨模态证据才配打断用户。

**控制权归用户**：任何自动行为可取消、可撤回、失败可降级、有审计。

## Motion

动效的任务是**说明状态变化**，不是让人赞叹。

- 交互类 ≤ 300ms；常驻律动 4–6s，像呼吸不像闪灯
- 入场从 `scale(0.95)` 起，不从 `0`
- 两条具身通道：
  - **motion（动作表意）** — 语义明确，用于高风险节点
  - **breath（呼吸律动）** — 低打扰，用于节律托举
- 每个动效要能说出它表达的语义；说不出就删

## Layout

- 正文 ≤ 65 字符/行
- 数字用 tabular-nums 对齐
- 下划线只用于链接
- 留白用间距系统，不靠缩小字号塞内容
- **一页能说清的事，不用两页**；一个组件能表达的，不加第二个

## Decisions Log

> 每次为这个规格做取舍时追加一行。**这是规格里最重要的部分**——它记录的是"为什么当时没选另一条路"。

| 日期 | 决定 | 放弃了什么 | 为什么 |
|---|---|---|---|
| — | 默认静默、异常才介入 | 放弃了"实时可见"带来的确定感 | 实时可见会把用户变成盯着仪表盘的人，而产品的目标是让人不盯着它 |
| — | 反馈优先放环境 | 放弃了屏幕的表达力 | 屏幕提示本身就是一次打断，与前提冲突 |
| — | 不做通用阈值 | 放弃了开箱即用的省事 | 个体差异大于共性，通用阈值必然误报 |
| — | 门槛测试必须导致砍功能 | 放弃了"保留可能性"的舒适 | 不砍就等于没做决策，测试变成装饰 |

## Refusals

**不做**：打断式通知 · 实时数字焦虑 · 通用阈值 · 不可中断的自动化 · 无证据的效果宣称 · 装饰性动效 · "全球首个"式表述 · 让用户误以为是人的 AI 表达

完整理由见 `references/refusal-list.md`。

## 怎么把本规格合并进你自己的项目

1. 复制本文件到你项目根目录，重命名为 `DESIGN.md`
2. **先保留 frontmatter 的 token 值**（它们是可判定规则），再按你的品牌改颜色与字体
3. 把你的取舍追加进 `Decisions Log`——**不要覆盖已有的**，那是判断依据
4. 在你的 `AGENTS.md` 里加一句：*构建 UI 前先读 `DESIGN.md`；偏离 token 的值视为需要说明的例外*
