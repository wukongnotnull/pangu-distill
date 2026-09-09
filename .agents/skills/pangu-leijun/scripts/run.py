#!/usr/bin/env python3
"""用七字诀扫一遍方案。不联网。"""

from __future__ import annotations

import argparse
import textwrap


PROMPT = """
方案：{claim}

1. 专注：这是一款，还是不自信的 100 款？切口还能不能再小？
2. 极致：做到别人拿不走了吗？还会被抄，先查自己。
3. 口碑：用户带着什么期望进来？交货超过那杆秤了吗？没有就先做产品，不要先做嗓门。
4. 快：能不能在安全前提下更快？慢了问题会全露。人身安全、发不出工资，不要用快盖。
5. 这是方法论，还是只上了一个 App？
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="雷军七字诀协议")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("scan", help="用七字诀扫一句话")
    d.add_argument("claim")
    sub.add_parser("protocol")
    args = parser.parse_args()
    claim = args.claim if args.cmd == "scan" else "（写入方案）"
    print(textwrap.dedent(PROMPT.format(claim=claim)).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
