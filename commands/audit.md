---
description: 谈判准备审计：跑确定性脚本检查策略与话术，人工复核，输出底线清单与通过/不通过结论。
argument-hint: [准备文档目录]
---

# /lhg-salary-talk:audit —— 谈判准备审计

用户输入在 `$ARGUMENTS` 中：`[准备文档目录]`。缺省为当前目录。

## 流程（加载 lhg-st-audit 全程指导）

### 1. 跑脚本
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit/prep_audit.py   --target <目录> --format text
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit/script_audit.py --target <目录> --format text
```
记下 blocker / warning / nit 的数量与明细（含文件、行号、规则说明）。

### 2. 分级处理
- blocker（缺 BATNA/底线/开价/让步阶梯、过早暴露底线、威胁式语言）：逐条修，修一条用脚本复查一条
- 修不掉的（如 BATNA 实在没有）→ 列入"需人工处理"，并调整策略打"价值牌"，**不许**为清零改规则
- warning（缺筹码/异议应对、数据无来源、让步无交换、收尾无书面确认）：修掉或写豁免理由

### 3. 人工复核（脚本做不到的）
- 数字复核：三点定位重算一遍，底线是算出来的还是拍脑袋的？
- 话术试读：读出声，说不出口的句子全部改写
- 底线默写：合上文档默写底线与阶梯——记不住等于没准备
- 最坏情况："只给底线价，走还是留？"提前做决定

### 4. 输出底线清单
一页纸 `底线清单.md`：开价/目标/底线/让步阶梯/绝不说的三句话/deadline。结论写清"通过 / 不通过"。

## 硬规则
- 有 blocker 就说"通过" → 不许
- 为清零改脚本规则或阈值 → 这是作弊，不许
- 自查报告是作战地图，不许发给对方
