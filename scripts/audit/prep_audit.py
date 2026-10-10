#!/usr/bin/env python3
"""lhg-salary-talk 确定性谈判准备审计：8 条规则，零第三方依赖。

扫描目标目录的 Markdown 谈判准备文档，检查 BATNA、底线、开价锚点、
让步阶梯等关键要素是否齐全；输出 JSON 与人类可读报告；
有 blocker 时以 exit code 2 退出（供 hooks 与 CI 使用）。

用法：
    python3 prep_audit.py --target <目录> [--format json|text] [--fail-on blocker|warning|nit]

规则文案均为本项目原创（BATNA 等谈判概念为公共知识，
检测规则为独立实现；未复制任何第三方原文案与代码）。
"""

import argparse
import json
import os
import re
import sys

VERSION = "1.0.0"
TOOL = "lhg-salary-talk/prep-audit"

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "dist", "build", ".venv",
}
SCAN_EXTS = {".md", ".markdown"}

BATNA_RES = [re.compile(p) for p in (r"BATNA", r"最佳备选", r"备选方案", r"退路")]
BOTTOM_RES = [re.compile(p) for p in (r"底线", r"最低接受", r"walk-?away")]
ANCHOR_RES = [re.compile(p) for p in (r"开价", r"目标薪资", r"期望薪资", r"锚定", r"目标薪酬")]
LADDER_RES = [re.compile(p) for p in (r"让步阶梯", r"让步计划", r"让步轮次", r"让步策略")]
CHIP_RES = [re.compile(p) for p in
            (r"签约奖金", r"签字费", r"股票", r"期权", r"RSU", r"职级", r"远程办公", r"title")]
OBJECTION_RES = [re.compile(p) for p in (r"异议", r"对方可能", r"HR可能", r"如果对方")]
REVIEW_RES = [re.compile(p) for p in (r"复盘", )]
SALARY_NUM_RE = re.compile(r"\d+\s*[kK万]")
SOURCE_RES = [re.compile(p) for p in (r"数据来源", r"来源：", r"来源:", r"数据来自")]


class Finding:
    __slots__ = ("rule_id", "severity", "category", "title", "file", "line", "snippet", "detail")

    def __init__(self, rule_id, severity, category, title, file, line, snippet, detail):
        self.rule_id = rule_id
        self.severity = severity
        self.category = category
        self.title = title
        self.file = file
        self.line = line
        self.snippet = snippet
        self.detail = detail

    def to_dict(self):
        return {
            "rule_id": self.rule_id, "severity": self.severity,
            "category": self.category, "title": self.title,
            "file": self.file, "line": self.line,
            "snippet": self.snippet, "detail": self.detail,
        }


def collect_files(target):
    out = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in SCAN_EXTS:
                out.append(os.path.join(root, f))
    return sorted(out)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


# ---------------------------------------------------------------- 规则定义

RULES = []
_RULE_BY_ID = {}


def rule(rule_id, severity, category, title, detail):
    def deco(fn):
        r = {"id": rule_id, "severity": severity, "category": category,
             "title": title, "detail": detail}
        _RULE_BY_ID[rule_id] = r
        r["check"] = fn
        RULES.append(r)
        return fn
    return deco


def _mk(rule_id, path, line, snippet):
    r = _RULE_BY_ID[rule_id]
    return Finding(r["id"], r["severity"], r["category"], r["title"],
                   path, line, snippet[:160], r["detail"])


def _has(text, patterns):
    return any(p.search(text) for p in patterns)


@rule("PREP-001", "blocker", "策略要素", "缺 BATNA",
      "没有最佳备选方案（BATNA）。没有退路的谈判只能被动接受，谈崩的代价无限大。先想清楚'谈不成我去哪'。")
def r_prep_001(lines, text, path, ctx):
    if not _has(text, BATNA_RES):
        return [_mk("PREP-001", path, 1, "全文未提及 BATNA/备选方案")]
    return []


@rule("PREP-002", "blocker", "策略要素", "缺谈判底线",
      "没有明确的 walk-away 点（最低接受条件）。底线不清，谈判中容易被对方牵着走，事后后悔。")
def r_prep_002(lines, text, path, ctx):
    if not _has(text, BOTTOM_RES):
        return [_mk("PREP-002", path, 1, "全文未明确谈判底线")]
    return []


@rule("PREP-003", "blocker", "策略要素", "缺开价锚点",
      "没有目标薪资/开价锚点。开价是锚定效应的载体，没想好开多少就上桌等于把定价权让给对方。")
def r_prep_003(lines, text, path, ctx):
    if not _has(text, ANCHOR_RES):
        return [_mk("PREP-003", path, 1, "全文未设定开价/目标薪资")]
    return []


@rule("PREP-004", "blocker", "策略要素", "缺让步阶梯",
      "没有设计让步阶梯（至少 3 轮让步：让多少、换什么）。临场让步最容易乱了阵脚，阶梯必须提前写好。")
def r_prep_004(lines, text, path, ctx):
    if not _has(text, LADDER_RES):
        return [_mk("PREP-004", path, 1, "全文未设计让步阶梯")]
    return []


@rule("PREP-005", "warning", "筹码", "缺备选筹码",
      "只谈 base 薪资，没准备备选筹码（签约奖金/股票期权/职级/远程）。薪资谈不拢时，筹码是第二战场。")
def r_prep_005(lines, text, path, ctx):
    if not _has(text, CHIP_RES):
        return [_mk("PREP-005", path, 1, "未准备薪资之外的备选筹码")]
    return []


@rule("PREP-006", "warning", "预案", "缺异议应对",
      "没有预演对方可能的异议（'预算不够''你年限不够'等）。被问住时的沉默比拒绝更伤议价。")
def r_prep_006(lines, text, path, ctx):
    if not _has(text, OBJECTION_RES):
        return [_mk("PREP-006", path, 1, "未准备异议应对话术")]
    return []


@rule("PREP-007", "warning", "诚实", "市场数据无来源标注",
      "文档中出现了薪资数字，但未标注数据来源。本插件不编造薪资数字：所有市场数据必须来自你亲手核实的来源（招聘软件/猎头/同行），并在文档中写清来源。")
def r_prep_007(lines, text, path, ctx):
    if SALARY_NUM_RE.search(text) and not _has(text, SOURCE_RES):
        m = SALARY_NUM_RE.search(text)
        ln = next((i + 1 for i, l in enumerate(lines) if SALARY_NUM_RE.search(l)), 1)
        return [_mk("PREP-007", path, ln, "薪资数字 %s 未标注数据来源" % m.group(0))]
    return []


@rule("PREP-008", "nit", "复盘", "缺复盘计划",
      "没有谈判后复盘计划。无论成败，复盘'对方哪句话是虚招、我哪次让步让早了'，下次谈判直接受益。")
def r_prep_008(lines, text, path, ctx):
    if not _has(text, REVIEW_RES):
        return [_mk("PREP-008", path, 1, "未安排谈判后复盘")]
    return []


# ---------------------------------------------------------------- 运行器

def run(target):
    files = collect_files(target)
    findings = []
    for path in files:
        text = read_text(path)
        lines = text.split("\n")
        rel = os.path.relpath(path, target)
        ctx = {}
        for r in RULES:
            try:
                for f in r["check"](lines, text, path, ctx) or []:
                    f.file = rel
                    findings.append(f)
            except Exception:
                continue  # 单条规则异常不影响整体
    return files, findings


def main(argv=None):
    ap = argparse.ArgumentParser(description="lhg-salary-talk 谈判准备审计")
    ap.add_argument("--target", default=".", help="扫描目录")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    ap.add_argument("--fail-on", choices=["blocker", "warning", "nit"], default="blocker")
    args = ap.parse_args(argv)

    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        print("target 不是目录：%s" % args.target, file=sys.stderr)
        return 1

    files, findings = run(target)
    sev_rank = {"blocker": 3, "warning": 2, "nit": 1}
    counts = {"blocker": 0, "warning": 0, "nit": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    result = {
        "tool": TOOL,
        "version": VERSION,
        "target": args.target,
        "summary": {
            "files_scanned": len(files),
            "rules_run": len(RULES),
            "blocker": counts["blocker"],
            "warning": counts["warning"],
            "nit": counts["nit"],
        },
        "findings": [f.to_dict() for f in sorted(
            findings, key=lambda x: (-sev_rank.get(x.severity, 0), x.file, x.line))],
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["summary"]
        print("谈判准备审计：扫描 %d 文件，运行 %d 条规则" % (s["files_scanned"], s["rules_run"]))
        print("blocker=%d warning=%d nit=%d" % (s["blocker"], s["warning"], s["nit"]))
        for f in result["findings"]:
            print("[%s][%s] %s:%d %s" % (
                f["severity"].upper(), f["rule_id"], f["file"], f["line"], f["title"]))
            print("    %s" % f["detail"])
            if f["snippet"]:
                print("    → %s" % f["snippet"])

    level = sev_rank[args.fail_on]
    bad = any(sev_rank.get(f.severity, 0) >= level for f in findings)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
