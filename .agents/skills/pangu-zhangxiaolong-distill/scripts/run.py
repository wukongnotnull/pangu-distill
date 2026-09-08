#!/usr/bin/env python3
"""判断一个功能是在帮人做完，还是在把人留住。不联网。"""

from __future__ import annotations

import argparse
import textwrap


PROMPT = """
功能：{claim}

1. 用户来是为了做完一件事，还是为了被留住？
   - 做完就走 → 工具：成功是离开。为日活加的层，能删就删。
   - 被留住 → 另一套产品。不要借用「用完即走」。
2. 离开平台推荐，这件事还会发生吗？发生在人与人之间，还是人与算法之间？
3. 先写一句「这对用户对不对」。写不出「对」就停，哪怕能赚钱。
4. 立项名会不会自我实现？叫信息流，它就会长成信息流。
5. 钱怎么出现：用户能否一眼看出这是广告？不能 → 不做。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="张小龙用完即走协议")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("stay", help="给一句话分类：留人还是做完")
    d.add_argument("claim")
    sub.add_parser("protocol")
    args = parser.parse_args()
    claim = args.claim if args.cmd == "stay" else "（写入功能）"
    print(textwrap.dedent(PROMPT.format(claim=claim)).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
