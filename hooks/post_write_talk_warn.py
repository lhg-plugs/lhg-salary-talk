#!/usr/bin/env python3
"""lhg-salary-talk 硬门②（警告级，不拦截）：写谈判准备/话术稿 md 时提醒跑审计。

触发：PostToolUse / Write|Edit。只做提醒，永远 exit 0、不拦截写入。

逻辑：被写的 .md 文件若含谈判关键词（底线/BATNA/话术/让步），
提醒跑 prep_audit.py / script_audit.py 检查策略要素与禁忌话术。

逃生方式：LHG_ST_HOOKS_OFF=1（环境变量）可关闭本提醒；
或 /plugin disable lhg-salary-talk 停用整个插件。
零第三方依赖；内部出错 fail-open。
"""

import json
import os
import re
import sys

TALK_RE = re.compile(r"底线|BATNA|话术|让步")


def main() -> int:
    if os.environ.get("LHG_ST_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # 输入解析失败：fail-open

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path.endswith(".md"):
        return 0

    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return 0  # 读不到文件：fail-open

    if not TALK_RE.search(text):
        return 0  # 与谈判准备无关，不提醒

    msg = (
        "谈判准备提醒（lhg-salary-talk）：%s 含谈判准备内容。\n"
        "写完请跑审计确认 blocker 清零：\n"
        "  python3 <插件目录>/scripts/audit/prep_audit.py --target <准备文档目录>\n"
        "  python3 <插件目录>/scripts/audit/script_audit.py --target <准备文档目录>\n"
        "关闭本提醒：export LHG_ST_HOOKS_OFF=1（当前会话有效）。"
    ) % file_path
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
