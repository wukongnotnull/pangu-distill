#!/usr/bin/env python3
"""把一句「命运句」拆成第一性协议的检查清单。不联网，不发明构成。"""

from __future__ import annotations

import argparse
import textwrap


PROTOCOL = """
命运句：{claim}

1. 这是重复已知，还是约束变了？（类比过今天 / 第一性做新东西）
2. 列出构成与约束。只写你愿意用「尽可能确定」担保的。没有事实就停，去检索。
3. 逐条标：定律 / 可核对数量 / 行情或惯例。后两类降级，不删数据。
4. 单元在你行动之后还在原处吗？会还手 → 不要给材料价答案。
5. 从留下的硬层往上建。建不出就写信息不足。
6. 给关键不确定数量一段范围，并问谁是庄家。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="第一性原理协议（盘古蒸馏产物）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decompose", help="拆一句命运句")
    d.add_argument("claim", help="被当成命运的那句话")

    sub.add_parser("protocol", help="只打印步骤")

    args = parser.parse_args()
    if args.cmd == "protocol":
        print(textwrap.dedent(PROTOCOL.format(claim="（在此写入命运句）")).strip())
        return 0
    print(textwrap.dedent(PROTOCOL.format(claim=args.claim)).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
