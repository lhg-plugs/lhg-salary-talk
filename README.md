<!-- About 简介（推送后填写到仓库 About 栏）：
薪酬谈判专家：策略到话术演练的谈判准备 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-salary-talk
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, salary-negotiation, career -->

# lhg-salary-talk：薪酬谈判专家

> **一句话介绍**：给 AI 助手装上"薪酬谈判流水线"——谈判策略（BATNA/底线/让步阶梯）、四阶段话术、角色扮演演练、底线清单，一次谈判差数万，准备必须结构化。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-salary-talk
> /plugin install lhg-salary-talk@lhg-plugs
> ```

## 它是什么

`lhg-salary-talk` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **4 个命令**（谈判准备流水线）：`salary-talk` 一条龙（输入→策略→演练→底线清单），`strategy` 策略设计，`drill` 话术演练，`audit` 准备审计
- **4 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：谈判策略、话术设计、演练复盘、准备自查
- **3 个专家 agent**：谈判策略师、谈判陪练（扮 HR 施压）、准备审计师
- **2 个硬门 hooks**：commit 前准备审计拦截、写准备文档提醒跑审计（均可一键豁免）
- **15 条确定性审计规则**：纯 Python、零第三方依赖，策略要素与禁忌话术秒级检查

## 4 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-salary-talk:salary-talk` | 谈判一条龙（输入→策略→演练→底线清单） | `/lhg-salary-talk:salary-talk "XX科技 高级前端"` |
| `/lhg-salary-talk:strategy` | 策略设计：BATNA/三点定位/让步阶梯/筹码 | `/lhg-salary-talk:strategy` |
| `/lhg-salary-talk:drill` | 话术演练：写稿→禁忌扫描→角色扮演 2 轮 | `/lhg-salary-talk:drill` |
| `/lhg-salary-talk:audit` | 准备审计（脚本 + 人工复核 + 底线清单） | `/lhg-salary-talk:audit` |

## 自查说明

自查 = 确定性脚本（机器）+ 人工复核（人）：

1. 先跑 `scripts/audit/` 下的两个脚本（准备审计 8 条、话术审计 7 条规则），零 LLM 成本；
2. 发现分三级：**blocker**（缺 BATNA/底线/开价/让步阶梯、过早暴露底线、威胁式语言——必须修，commit 前 hook 会拦截）、**warning**（缺备选筹码/异议应对、数据无来源、让步无交换、收尾无书面确认——修或写豁免理由）、**nit**（缺复盘计划、话术段落过长——顺手修）；
3. 再做人工复核：数字重算一遍、话术读出声、底线默写、最坏情况预演。

blocker 清零才算做完；为清零改规则算作弊，不许。

## 目录结构

```
lhg-salary-talk/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 4 个命令：salary-talk / strategy / drill / audit
├── skills/                  # 4 个平台中立 skill（lhg-st-strategy/script/drill/audit）
├── agents/                  # 3 个专家 agent（strategist / coach / auditor）
├── hooks/                   # 2 个硬门（commit 前审计拦截 / 写稿提醒）+ 豁免说明
├── scripts/audit/           # 15 条确定性审计规则（零第三方依赖）
├── fixtures/                # 冒烟测试用例（坏/好对照）
├── smoke_test.py            # 一键冒烟测试
├── ATTRIBUTION.md           # 灵感来源与许可声明
└── LICENSE                  # MIT
```

## 诚实声明

- **不编造薪资数字**：市场薪资数据必须由用户亲手核实（招聘软件/猎头/同行交流）并在文档中写清来源。本插件只帮你组织策略与话术，不提供、更不编造任何薪资行情数字——无来源的数字会被审计标为 warning。
- **审计是启发式**：脚本能抓"缺要素"和"禁忌话术"，抓不到"你的 BATNA 是真是假""底线数字合不合理"。人工复核（数字重算/底线默写）不可省略。
- **谈判结果不承诺**：策略与话术提高胜率，不保证结果。对方预算、HC 紧迫度等变量不在本插件掌控内。
- **未核实项**：ResumeSkills 的 `salary-negotiation-prep` 在本插件编写时未核实其许可声明，本插件仅借鉴其"结构化谈判准备"的高层思路，未复制其任何原文案与代码（见 ATTRIBUTION.md）。

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你拿到 offer、要谈薪资了，想一次把策略、话术、演练做扎实时 → 用 `/lhg-salary-talk:salary-talk` 一条龙
- 你只有 15 分钟，HR 电话马上打过来时 → 用 `drill` 的极速演练模式
- 你写好了话术稿，怕里面有"暴露底线""威胁式"这种作死表达时 → 跑 `/lhg-salary-talk:audit`
- 你想在跳槽季给每家公司都建一份谈判档案时 → 策略模板可复用，一家一份 `谈判准备.md`

**什么时候不用：**

- 你只是想查"这个岗位市场价多少" → 本插件不提供薪资数据，去招聘软件/问猎头/问同行，查到后拿回来做策略
- 你期望 AI 替你谈判 → 谈判必须本人上桌，AI 只能帮你准备
- 你希望"话术越强势越好" → 威胁式语言是本插件的 blocker，强势靠 BATNA 和依据，不靠嗓门

## lhg-plugs 插件矩阵

| 插件 | 一句话 | 安装 |
|---|---|---|
| [lhg-salary-talk](https://github.com/lhg-plugs/lhg-salary-talk) | 薪酬谈判专家：策略到话术演练的谈判准备 | `/plugin install lhg-salary-talk@lhg-plugs` |
| [lhg-fullstack](https://github.com/lhg-plugs/lhg-fullstack) | 小白一句话 → 高质量全栈应用 | `/plugin install lhg-fullstack@lhg-plugs` |
| [lhg-video-edit](https://github.com/lhg-plugs/lhg-video-edit) | 一句话把口播素材剪成爆款短视频（+口播脚本子命令） | `/plugin install lhg-video-edit@lhg-plugs` |
| [lhg-wechat-article](https://github.com/lhg-plugs/lhg-wechat-article) | 公众号写作专家：选题到排版一气呵成 | `/plugin install lhg-wechat-article@lhg-plugs` |
| [lhg-xiaohongshu](https://github.com/lhg-plugs/lhg-xiaohongshu) | 小红书种草专家：卖点到爆款笔记一键生成 | `/plugin install lhg-xiaohongshu@lhg-plugs` |
| [lhg-resume](https://github.com/lhg-plugs/lhg-resume) | 简历优化专家：ATS诊断到模拟面试一条龙 | `/plugin install lhg-resume@lhg-plugs` |
| [lhg-ppt](https://github.com/lhg-plugs/lhg-ppt) | PPT制作专家：述职融资答辩一键成稿 | `/plugin install lhg-ppt@lhg-plugs` |
| [lhg-excel](https://github.com/lhg-plugs/lhg-excel) | 表格数据专家：清洗透视图表一条龙 | `/plugin install lhg-excel@lhg-plugs` |
| [lhg-thesis](https://github.com/lhg-plugs/lhg-thesis) | 毕业论文助手：开题到盲审的写作流水线 | `/plugin install lhg-thesis@lhg-plugs` |
| [lhg-miniprogram](https://github.com/lhg-plugs/lhg-miniprogram) | 小程序开发专家：一句话生成微信小程序 | `/plugin install lhg-miniprogram@lhg-plugs` |
| [lhg-contract](https://github.com/lhg-plugs/lhg-contract) | 合同审查助手：风险条款标红+修改建议 | `/plugin install lhg-contract@lhg-plugs` |
| [lhg-lit-review](https://github.com/lhg-plugs/lhg-lit-review) | 文献综述专家：从文献收集到规范引用的写作流水线 | `/plugin install lhg-lit-review@lhg-plugs` |

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（JSON 合法、skill/command/agent 完整性、15 条规则、fixtures 命中、hooks 行为）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-salary-talk/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
