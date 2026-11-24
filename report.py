"""Generate a local daily report from a UTF-8 CSV. All amounts are yuan."""
import argparse
import csv
import html
from datetime import date
from decimal import Decimal
from pathlib import Path


def amount(raw):
    if not raw.strip():
        return None
    value = Decimal(raw)
    if not value.is_finite() or value < 0:
        raise ValueError("金额须为非负数")
    return value


def render(source, day):
    rows = []
    seen = set()
    with source.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["日期"] != day:
                continue
            room = row["直播间"]
            if not room or room in seen:
                raise ValueError("直播间缺失或重复")
            seen.add(room)
            gmv, spend = (amount(row[k]) for k in ("成交额", "投流消耗"))
            missing = [k for k in ("成交额", "投流消耗") if not row[k].strip()]
            status = row["状态"]
            if status == "未开播":
                if any(v not in (None, 0) for v in (gmv, spend)):
                    raise ValueError("未开播记录含非零金额，请核对")
                note = status
            elif status == "已开播":
                note = "待补：" + "、".join(missing) if missing else "已齐"
            else:
                raise ValueError("请填写开播状态")
            roi = f"{gmv / spend:.2f}" if gmv is not None and spend else "/"
            cells = [room, *["—" if v is None else f"{v:,.2f}" for v in (gmv, spend)], roi, note]
            rows.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in cells) + "</tr>")
    if not rows:
        raise ValueError("该日期没有记录")
    return ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>直播经营日报</title>"
            "<style>body{font:18px system-ui;margin:5%}td,th{padding:12px;border-bottom:1px solid #ccc}</style>"
            f"<h1>{day} 直播经营日报</h1><table><tr><th>直播间</th><th>成交额（元）</th>"
            "<th>投流消耗（元）</th><th>ROI</th><th>核对结果</th></tr>" + "".join(rows) + "</table></html>")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("day", type=date.fromisoformat)
    args = p.parse_args()
    page = render(args.csv, args.day.isoformat())
    target = Path(f"日报-{args.day}.html")
    target.write_text(page, encoding="utf-8")
    print(target)
