#!/usr/bin/env python3
"""
小金井市議員のXアカウント発見テスト
Test X account discovery for Koganei City council members
"""

import json
from pathlib import Path
import sys
import os

sys.path.append(str(Path(__file__).parent))

from test_automated_discovery import EnhancedSearchPatterns, ProfileVerifier, SearchCandidate

def load_koganei_data():
    """小金井市の議員データを読み込み"""
    koganei_json_path = Path("data/processed/13_東京都/議員リスト_132101_小金井市.json")
    
    if koganei_json_path.exists():
        with open(koganei_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    koganei_members = [
        {"氏名": "太田　浩典", "所属": "小金井市政会"},
        {"氏名": "中井　れい子", "所属": "小金井市政会"},
        {"氏名": "水谷　貴子", "所属": "市民自治"},
        {"氏名": "長取　太郎", "所属": "市民自治"},
        {"氏名": "安田　桂子", "所属": "市民ネットワーク"},
        {"氏名": "小林　正樹", "所属": "小金井市政会"},
        {"氏名": "河野　麻美", "所属": "公明党"},
        {"氏名": "沖浦　篤", "所属": "人新会"},
        {"氏名": "木蘭　典子", "所属": "人新会"},
        {"氏名": "村上　洋介", "所属": "あいそ"},
        {"氏名": "藤川　健二", "所属": "市政"},
        {"氏名": "田渕　久崇", "所属": "日本共産党"}
    ]
    
    return koganei_members

def test_koganei_discovery():
    """小金井市議員のXアカウント発見テスト"""
    print("小金井市議員 Xアカウント自動発見テスト")
    print("=" * 50)
    
    members = load_koganei_data()
    municipality_info = {
        'name': '小金井市',
        'type': '市',
        'code': '132101'
    }
    
    total_queries = 0
    
    for i, member in enumerate(members, 1):
        print(f"\n[{i}/12] {member['氏名']} ({member['所属']})")
        print("-" * 40)
        
        queries = EnhancedSearchPatterns.generate_enhanced_queries(member, municipality_info)
        total_queries += len(queries)
        
        print(f"生成された検索クエリ数: {len(queries)}")
        print("主要な検索パターン:")
        
        for j, query in enumerate(queries[:5], 1):
            print(f"  {j}. {query}")
        
        if len(queries) > 5:
            print(f"  ... 他 {len(queries) - 5} 件")
        
        print("\n信頼度スコア算出例:")
        
        name_parts = member['氏名'].replace('　', ' ').split()
        if len(name_parts) >= 2:
            family_name = name_parts[0]
            given_name = name_parts[1]
            
            test_candidates = [
                {
                    'username': f"{family_name.lower()}_{given_name.lower()}",
                    'display_name': member['氏名'],
                    'bio': f"小金井市議会議員。{member['所属']}所属。地域のために活動しています。"
                },
                {
                    'username': f"{given_name.lower()}_{family_name[0].lower()}",
                    'display_name': f"{given_name} {family_name[0]}",
                    'bio': "小金井市在住。政治に関心があります。"
                },
                {
                    'username': f"koganei_{family_name.lower()}",
                    'display_name': f"{family_name}さん",
                    'bio': "東京都在住。趣味は読書です。"
                }
            ]
            
            for k, candidate in enumerate(test_candidates, 1):
                score, reasons = ProfileVerifier.calculate_confidence_score(
                    candidate, member, municipality_info
                )
                status = "✅" if score >= 0.6 else "❌"
                print(f"  {k}. @{candidate['username']} - 信頼度スコア: {score:.2f} {status}")
                if reasons:
                    print(f"     理由: {', '.join(reasons)}")
    
    print(f"\n" + "=" * 50)
    print(f"総検索クエリ数: {total_queries}")
    print(f"平均クエリ数/議員: {total_queries/len(members):.1f}")
    print(f"対象議員数: {len(members)}")
    
    print(f"\n手動検証用検索URL生成中...")
    
    search_urls = []
    for member in members:
        queries = EnhancedSearchPatterns.generate_enhanced_queries(member, municipality_info)
        member_urls = []
        
        for query in queries[:10]:  # Top 10 queries per member
            search_url = f"https://x.com/search?q={query.replace(' ', '%20')}&f=user"
            member_urls.append(search_url)
        
        search_urls.append({
            'name': member['氏名'],
            'party': member['所属'],
            'urls': member_urls
        })
    
    output_path = Path("data/koganei_discovery_urls.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(search_urls, f, ensure_ascii=False, indent=2)
    
    print(f"検索URL保存完了: {output_path}")
    
    return search_urls

if __name__ == "__main__":
    test_koganei_discovery()
