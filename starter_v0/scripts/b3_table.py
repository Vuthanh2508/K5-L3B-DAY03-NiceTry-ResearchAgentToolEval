"""In bảng B3 (markdown) từ run JSON mới nhất của suite group.
Chạy từ starter_v0/:  python b3_table.py   (hoặc python b3_table.py runs/<file>.json)
"""
import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else max(Path("runs").glob("*_group_*.json"), key=lambda p: p.stat().st_mtime)
data = json.loads(path.read_text(encoding="utf-8"))


def fmt_calls(calls):
    return ", ".join(f"{c['name']}({', '.join(f'{k}={v}' for k, v in (c.get('args') or {}).items())})" for c in calls) or "không gọi tool"


print(f"Run: `{path.name}`\n")
print("| Case ID | What It Tests | Expected Tool/Behavior | Result |")
print("|---|---|---|---|")
for item in data["results"]:
    expect, res = item["expect"], item["result"]
    expected = "no_tool" if expect.get("no_tool") else fmt_calls(expect.get("tool_calls", []))
    kind = "multi" if item["is_multiturn"] else "single"
    result = "PASS" if res["passed"] else f"FAIL: {'; '.join(res.get('failures', []))} (thực tế: {fmt_calls(res.get('actual_tool_calls', []))})"
    print(f"| {item['id']} ({kind}) | {item['metadata'].get('what_it_tests', '')} | {expected} | {result} |")
s = data["summary"]
print(f"\nTổng: {sum(r['result']['passed'] for r in data['results'])}/{len(data['results'])} pass")
