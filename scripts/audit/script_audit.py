#!/usr/bin/env python3
"""lhg-salary-talk 确定性话术审计：7 条规则，零第三方依赖。

扫描目标目录的 Markdown 话术稿，检查话术结构（开价锚定/让步交换/
收尾书面确认）与禁忌话术（过早暴露底线/威胁式语言/情绪化表述）；
输出 JSON 与人类可读报告；有 blocker 时以 exit code 2 退出。

用法：
    python3 script_audit.py --target <目录> [--format json|text] [--fail-on blocker|warning|nit]

规则文案均为本项目原创，未复制任何第三方原文案与代码。
"""

import argparse
import json
import os
import re
import sys

VERSION = "1.0.0"
TOOL = "lhg-salary-talk/script-audit"

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "dist", "build", ".venv",
}
SCAN_EXTS = {".md", ".markdown"}

EARLY_BOTTOM_RES = [re.compile(p) for p in
                    (r"我最低接受", r"我的底线是", r"底线是\s*\d", r"低于.*免谈", r"少一分都不行")]
THREAT_RES = [re.compile(p) for p in
              (r"不给就走", r"我有的是\s*offer", r"大把公司", r"爱要不要", r"不涨就走")]
OFFER_RES = [re.compile(p) for p in (r"开价", r"期望薪资", r"期望薪酬")]
ANCHOR_PROOF_RES = [re.compile(p) for p in (r"市场", r"调研", r"数据", r"同行", r"报告")]
CONCEDE_RES = [re.compile(p) for p in (r"让步", )]
TRADE_RES = [re.compile(p) for p in (r"交换", r"相应", r"条件", r"换取", r"作为交换")]
WRITTEN_RES = [re.compile(p) for p in (r"书面", r"邮件确认", r"确认函", r"offer letter")]
EMOTION_RES = [re.compile(p) for p in
               (r"委屈", r"被压榨", r"太不公平", r"卖命", r"血汗", r"欺负人")]
HEADING_RE = re.compile(r"^#{1,6}\s+")


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


def _line_hits(rule_id, lines, path, patterns):
    out = []
    for i, ln in enumerate(lines):
        for p in patterns:
            if p.search(ln):
                out.append(_mk(rule_id, path, i + 1, ln.strip()))
                break
    return out


@rule("TALK-001", "blocker", "禁忌话术", "过早暴露底线",
      "话术中出现了'我最低接受…''我的底线是…'。底线一旦出口，谈判就变成了'从底线往上砍'。底线只写在准备文档里，永远不要说出口。")
def r_talk_001(lines, text, path, ctx):
    return _line_hits("TALK-001", lines, path, EARLY_BOTTOM_RES)


@rule("TALK-002", "blocker", "禁忌话术", "威胁式语言",
      "话术中出现威胁式表达。威胁把谈判变成对抗，对方要么强硬反弹、要么记仇——offer 谈下来入职也难受。施压靠 BATNA 的'存在'，不靠嘴。")
def r_talk_002(lines, text, path, ctx):
    return _line_hits("TALK-002", lines, path, THREAT_RES)


@rule("TALK-003", "warning", "话术结构", "开价无锚定依据",
      "话术里有开价，但全篇没有市场数据/调研/报告做支撑。没有依据的开价就是'我觉得'，对方一句'超预算了'就能打回来。每个数字后面跟一句依据。")
def r_talk_003(lines, text, path, ctx):
    if _has(text, OFFER_RES) and not _has(text, ANCHOR_PROOF_RES):
        return [_mk("TALK-003", path, 1, "开价缺少市场数据/调研依据")]
    return []


@rule("TALK-004", "warning", "话术结构", "让步无交换",
      "话术里有让步，但没有'交换'（让一步、换一个条件）。单方面降价等于告诉对方'再压一压还有'。每次让步都配一个对价。")
def r_talk_004(lines, text, path, ctx):
    if _has(text, CONCEDE_RES) and not _has(text, TRADE_RES):
        return [_mk("TALK-004", path, 1, "让步缺少对价交换设计")]
    return []


@rule("TALK-005", "warning", "话术结构", "收尾无书面确认",
      "话术没有'书面确认'环节。口头 offer 不作数：谈定后必须要求书面 offer / 邮件确认，口头承诺变卦零成本。")
def r_talk_005(lines, text, path, ctx):
    if not _has(text, WRITTEN_RES):
        return [_mk("TALK-005", path, 1, "全文未提及书面确认")]
    return []


@rule("TALK-006", "warning", "禁忌话术", "情绪化表述",
      "话术中出现情绪化/诉苦式表达。谈判桌上讲委屈等于递刀子：对方会认定你'非这家不可'，议价直接崩。情绪留在家里，桌上只讲价值与依据。")
def r_talk_006(lines, text, path, ctx):
    return _line_hits("TALK-006", lines, path, EMOTION_RES)


@rule("TALK-007", "nit", "话术质量", "话术段落过长",
      "某段话术超过 180 字。谈判是轮次制的，一次说太多等于把多个让步点一次性暴露。拆成要点句，一轮只讲一个点。")
def r_talk_007(lines, text, path, ctx):
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip().strip('"“”')
        if HEADING_RE.match(ln) or len(s) < 180:
            continue
        out.append(_mk("TALK-007", path, i + 1, "该段 %d 字，建议拆分" % len(s)))
    return out


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
    ap = argparse.ArgumentParser(description="lhg-salary-talk 确定性话术审计")
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
        print("话术审计：扫描 %d 文件，运行 %d 条规则" % (s["files_scanned"], s["rules_run"]))
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
