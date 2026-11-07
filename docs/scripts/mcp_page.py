import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
GROUP_JA = {
 "2.1": "完了と停止", "2.2": "セッションを見る", "2.3": "セッション・子セッションを起動して操作する",
 "2.4": "セッション間メッセージ", "2.5": "メモ", "2.6": "定時実行", "2.7": "掃除",
 "2.8": "エージェントメモリ", "2.9": "ブラウザ（Chromium）", "2.10": "画像", "2.11": None,
 "2.12": "リポジトリ・ブランチ・作業項目", "2.13": "アシスタントの会話", "2.14": "管理者向け（外部 MCP）",
}
SWITCH = [("sessionFleetSpawn", "「セッションからのセッション起動」"), ("peerMessaging", "「セッション間メッセージ」"),
          ("sessionSearch", "「過去セッションの検索」"), ("agentMemory", "「エージェントメモリ」"),
          ("imageGeneration", "「画像生成」")]
out, seen = [], set()
cur = None
for line in src.splitlines():
    m = re.match(r"^### (2\.\d+)", line)
    if m:
        cur = m.group(1); sub = 0
        if GROUP_JA.get(cur):
            out.append(f"\n## {GROUP_JA[cur]}\n")
        continue
    if line.startswith("Memory snapshots") and cur == "2.8":
        out.append("\n### エージェント自身のメモリの履歴\n"); continue
    if not cur or not GROUP_JA.get(cur) or not line.startswith("| ") or line.startswith("| Tool") or line.startswith("|---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 5 or not cells[3]:
        continue
    tool, routes, gate, purpose, params = cells[:5]
    if tool in seen:
        continue
    seen.add(tool)
    if not any(h.startswith("| ツール") for h in out[-3:]) and not (out and out[-1].startswith("| `")):
        out.append("| ツール | できること | 使える場所 |")
        out.append("|---|---|---|")
    r = routes
    sess = "—"
    if re.search(r"\bS\b", r):
        sess = "✓"
        for k, lab in SWITCH:
            if k in gate:
                sess = lab; break
        if "studio" in gate:
            sess = "スタジオのセッション"
        if "own children" in r or "own children" in gate:
            sess += "（自分の子だけ）" if sess != "✓" else "（自分の子だけ）"
    asst = "読み取り" if "A-R" in r else ("書き込み" if "A-W" in r else "—")
    ext = "—"
    if "CPM" in r or "CP" in r:
        ext = "管理者" if cur == "2.14" else "✓"
    p = "—" if params in ("—", "") else ", ".join(f"`{x.strip()}`" for x in re.sub(r"\(.*?\)", "", params).split(",") if x.strip() and x.strip() != "...")
    where = []
    if sess != "—":
        where.append("セッション" if sess == "✓" else f"セッション（{sess}）")
    if asst != "—":
        where.append(f"アシスタント（{asst}）")
    if ext != "—":
        where.append("外部 MCP" if ext == "✓" else f"外部 MCP（{ext}）")
    out.append(f"| `{tool}` | {purpose} | {'<br>'.join(where)} |")
print("\n".join(out))
print(len(seen), file=sys.stderr)
