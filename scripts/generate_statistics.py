#!/usr/bin/env python3
"""
統計情報を生成してMarkdown形式で出力するスクリプト
"""

import json
import glob
from collections import defaultdict
from datetime import datetime

def generate_statistics_markdown():
    """統計情報のMarkdownを生成"""
    stats = defaultdict(lambda: {"total": 0, "with_x": 0, "parties": defaultdict(int)})
    
    json_files = glob.glob("data/processed/*.json")
    
    for filepath in sorted(json_files):
        filename = filepath.split("/")[-1]
        parts = filename.split("_")
        code = parts[1]
        municipality = parts[2].replace(".json", "")
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for member in data:
            stats[municipality]["total"] += 1
            stats[municipality]["code"] = code
            
            if member.get("X（旧Twitter）"):
                stats[municipality]["with_x"] += 1
            
            party = member.get("所属", "不明")
            stats[municipality]["parties"][party] += 1
    
    # Markdown生成
    output = []
    output.append("# 議員データ統計レポート")
    output.append(f"\n生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    
    # 全体統計
    total_municipalities = len(stats)
    total_members = sum(s["total"] for s in stats.values())
    total_with_x = sum(s["with_x"] for s in stats.values())
    
    output.append("\n## 全体統計")
    output.append(f"- 収集自治体数: {total_municipalities}")
    output.append(f"- 総議員数: {total_members}名")
    output.append(f"- X登録議員数: {total_with_x}名 ({total_with_x/total_members*100:.1f}%)")
    
    # 会派統計
    all_parties = defaultdict(int)
    for muni_stats in stats.values():
        for party, count in muni_stats["parties"].items():
            all_parties[party] += count
    
    output.append("\n## 会派別統計")
    output.append("| 会派名 | 議員数 | 割合 |")
    output.append("|--------|--------|------|")
    
    for party, count in sorted(all_parties.items(), key=lambda x: x[1], reverse=True)[:10]:
        output.append(f"| {party} | {count} | {count/total_members*100:.1f}% |")
    
    # X登録率ランキング
    output.append("\n## X登録率ランキング")
    
    # TOP 10
    output.append("\n### TOP 10（登録率が高い自治体）")
    output.append("| 順位 | 自治体名 | 登録率 | 登録数/総数 |")
    output.append("|------|----------|--------|-------------|")
    
    ranked = sorted(
        [(m, s["with_x"]/s["total"]*100 if s["total"] > 0 else 0, s) for m, s in stats.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    for i, (muni, rate, s) in enumerate(ranked[:10], 1):
        output.append(f"| {i} | {muni} | {rate:.1f}% | {s['with_x']}/{s['total']} |")
    
    # BOTTOM 10（0%を除く）
    output.append("\n### 改善が必要な自治体（登録率が低い、0%を除く）")
    output.append("| 順位 | 自治体名 | 登録率 | 登録数/総数 |")
    output.append("|------|----------|--------|-------------|")
    
    low_ranked = [x for x in ranked if x[1] > 0][-10:]
    for i, (muni, rate, s) in enumerate(low_ranked, 1):
        output.append(f"| {i} | {muni} | {rate:.1f}% | {s['with_x']}/{s['total']} |")
    
    # 登録率0%の自治体
    zero_x = [x for x in ranked if x[1] == 0]
    if zero_x:
        output.append(f"\n### X登録率0%の自治体（{len(zero_x)}自治体）")
        output.append(", ".join([x[0] for x in zero_x]))
    
    return "\n".join(output)

if __name__ == "__main__":
    print(generate_statistics_markdown())