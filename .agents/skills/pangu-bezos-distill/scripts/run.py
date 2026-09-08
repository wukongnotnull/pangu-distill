#!/usr/bin/env python3
"""把一个决定标成单向门或双向门。不联网。"""

from __future__ import annotations

import argparse
import textwrap


PROMPT = """
决定：{claim}

1. 走错之后，能否以可接受代价退回？
   - 能 → 双向门：高判断的个人或小团队快定。错了再开门。
   - 不能 → 单向门：慢、咨询、写清不可逆点。
2. 不要用同一套重流程审所有门。
3. 若是「没试过会不会在 80 岁缠着我」的人生单向门，另用后悔最小化。
4. 伤害他人的不可逆，不要盗用后悔最小化。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="贝索斯门协议")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("door", help="给一句话分类")
    d.add_argument("claim")
    sub.add_parser("protocol")
    args = parser.parse_args()
    claim = args.claim if args.cmd == "door" else "（写入决定）"
    print(textwrap.dedent(PROMPT.format(claim=claim)).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
