#!/usr/bin/env python3
"""
自動Xアカウント発見システムのテスト版
WebDriverを使わずに検索パターン生成と信頼度スコア算出をテスト
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SearchCandidate:
    """検索候補アカウント"""
    username: str
    display_name: str
    bio: str
    url: str
    confidence_score: float
    match_reasons: List[str]

@dataclass
class DiscoveryResult:
    """発見結果"""
    member_name: str
    found_account: Optional[SearchCandidate]
    search_queries_used: List[str]
    total_candidates: int
    processing_time: float

class EnhancedSearchPatterns:
    """拡張検索パターン生成クラス"""
    
    @staticmethod
    def generate_enhanced_queries(member: Dict, municipality_info: Dict) -> List[str]:
        """拡張検索クエリを生成"""
        name = member['氏名']
        name_no_space = name.replace('　', '')
        reading = member['よみ'].replace('　', '').replace(' ', '')
        party = member.get('所属', '')
        muni_name = municipality_info['name']
        muni_type = municipality_info['type']
        
        queries = []
        
        queries.extend([
            f'"{name}" {muni_type}議 -RT',
            f'"{name}" {muni_name} 議員',
            f'{name_no_space} プロフィール {muni_type}議',
        ])
        
        queries.extend([
            f'{name} {muni_name} イベント',
            f'{name} {muni_name} 祭り',
            f'{name} {muni_name} 地域活動',
            f'{name} 市民相談',
        ])
        
        queries.extend([
            f'{name} 一般質問',
            f'{name} 議会報告',
            f'{name} 市政報告',
            f'{name} 議会だより',
        ])
        
        queries.extend([
            f'{name} インタビュー',
            f'{name} 取材',
            f'{name} 新聞',
            f'{name} 記事',
        ])
        
        queries.extend([
            f'#{muni_name}議会 {name}',
            f'#{muni_name} {name}',
            f'{name} 当選',
            f'{name} 選挙',
        ])
        
        if party and party != '無所属':
            queries.extend([
                f'{party} {muni_name} {name}',
                f'{party} {name}',
            ])
        
        return queries

class ProfileVerifier:
    """プロフィール検証クラス"""
    
    @staticmethod
    def calculate_confidence_score(candidate: Dict, member: Dict, municipality_info: Dict) -> Tuple[float, List[str]]:
        """信頼度スコアを算出"""
        score = 0.0
        reasons = []
        
        name = member['氏名']
        name_no_space = name.replace('　', '')
        reading = member['よみ'].replace('　', '').replace(' ', '')
        party = member.get('所属', '')
        muni_name = municipality_info['name']
        
        display_name = candidate.get('display_name', '').lower()
        bio = candidate.get('bio', '').lower()
        username = candidate.get('username', '').lower()
        
        if name_no_space.lower() in display_name:
            score += 0.4
            reasons.append('表示名に氏名が含まれる')
        elif any(part in display_name for part in name.split('　')):
            score += 0.2
            reasons.append('表示名に名前の一部が含まれる')
        
        political_keywords = ['議員', '市議', '町議', '村議', '議会', '市政', '町政', '村政']
        for keyword in political_keywords:
            if keyword in bio:
                score += 0.15
                reasons.append(f'プロフィールに「{keyword}」が含まれる')
                break
        
        if muni_name in bio:
            score += 0.2
            reasons.append(f'プロフィールに「{muni_name}」が含まれる')
        
        if party and party != '無所属' and party in bio:
            score += 0.15
            reasons.append(f'プロフィールに「{party}」が含まれる')
        
        name_parts = name.split('　')
        if len(name_parts) >= 2:
            family, given = name_parts[0], name_parts[1]
            username_patterns = [
                f'{family}{given[:1]}',
                f'{family}_{given}',
                f'{given}{family[:1]}',
                reading[:6]
            ]
            for pattern in username_patterns:
                if pattern.lower() in username:
                    score += 0.1
                    reasons.append(f'ユーザー名にパターン「{pattern}」が含まれる')
                    break
        
        return min(score, 1.0), reasons

def test_search_patterns():
    """検索パターン生成をテスト"""
    print("=== 検索パターン生成テスト ===")
    
    test_member = {
        '氏名': '前田　善信',
        'よみ': 'まえだ よしのぶ',
        '所属': '公明党'
    }
    
    municipality_info = {
        'name': '武蔵村山市',
        'type': '市',
        'code': '132233'
    }
    
    queries = EnhancedSearchPatterns.generate_enhanced_queries(test_member, municipality_info)
    
    print(f"議員: {test_member['氏名']} ({test_member['所属']})")
    print(f"自治体: {municipality_info['name']}")
    print(f"生成された検索クエリ数: {len(queries)}")
    print("\n検索クエリ一覧:")
    for i, query in enumerate(queries, 1):
        print(f"{i:2d}. {query}")
    
    return queries

def test_confidence_scoring():
    """信頼度スコア算出をテスト"""
    print("\n=== 信頼度スコア算出テスト ===")
    
    test_member = {
        '氏名': '前田　善信',
        'よみ': 'まえだ よしのぶ',
        '所属': '公明党'
    }
    
    municipality_info = {
        'name': '武蔵村山市',
        'type': '市',
        'code': '132233'
    }
    
    test_candidates = [
        {
            'username': 'maeda_yoshinobu',
            'display_name': '前田善信',
            'bio': '武蔵村山市議会議員。公明党所属。市民の皆様のために頑張ります。',
            'url': 'https://x.com/maeda_yoshinobu'
        },
        {
            'username': 'yoshinobu_m',
            'display_name': '前田よしのぶ',
            'bio': '武蔵村山市在住。地域活動に参加しています。',
            'url': 'https://x.com/yoshinobu_m'
        },
        {
            'username': 'maeda123',
            'display_name': 'まえだ',
            'bio': '政治に興味があります。',
            'url': 'https://x.com/maeda123'
        }
    ]
    
    print(f"議員: {test_member['氏名']} ({test_member['所属']})")
    print(f"自治体: {municipality_info['name']}")
    print("\n候補アカウントの信頼度スコア:")
    
    for i, candidate in enumerate(test_candidates, 1):
        score, reasons = ProfileVerifier.calculate_confidence_score(
            candidate, test_member, municipality_info
        )
        
        print(f"\n{i}. @{candidate['username']}")
        print(f"   表示名: {candidate['display_name']}")
        print(f"   プロフィール: {candidate['bio']}")
        print(f"   信頼度スコア: {score:.2f}")
        print(f"   マッチ理由: {', '.join(reasons) if reasons else 'なし'}")
        print(f"   閾値(0.6)以上: {'✅' if score >= 0.6 else '❌'}")

def test_municipality_processing():
    """自治体データ処理をテスト"""
    print("\n=== 自治体データ処理テスト ===")
    
    json_path = Path('data/processed/13_東京都/議員リスト_132233_武蔵村山市.json')
    
    if not json_path.exists():
        print(f"エラー: ファイルが見つかりません - {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 自治体情報を解析
    filename = json_path.stem
    match = re.search(r'議員リスト_(\d+)_(.+)', filename)
    if not match:
        print("ファイル名の解析に失敗しました")
        return
    
    muni_name = match.group(2)
    muni_type = '市' if muni_name.endswith('市') else '町' if muni_name.endswith('町') else '村'
    
    municipality_info = {
        'name': muni_name,
        'type': muni_type,
        'code': match.group(1)
    }
    
    without_account = [m for m in data if not m.get('X（旧Twitter）')]
    with_account = [m for m in data if m.get('X（旧Twitter）')]
    
    print(f"自治体: {muni_name} (コード: {municipality_info['code']})")
    print(f"総議員数: {len(data)}")
    print(f"Xアカウント登録済み: {len(with_account)}")
    print(f"Xアカウント未登録: {len(without_account)}")
    print(f"未登録率: {len(without_account)/len(data)*100:.1f}%")
    
    print("\n未登録議員一覧:")
    for i, member in enumerate(without_account, 1):
        print(f"{i:2d}. {member['氏名']} ({member['所属']})")
    
    if without_account:
        print(f"\n=== {without_account[0]['氏名']} の検索パターン例 ===")
        queries = EnhancedSearchPatterns.generate_enhanced_queries(
            without_account[0], municipality_info
        )
        for i, query in enumerate(queries[:5], 1):  # 最初の5つのみ表示
            print(f"{i}. {query}")
        print(f"... 他 {len(queries)-5} パターン")

def main():
    """メイン関数"""
    print("自動Xアカウント発見システム - テスト版")
    print("=" * 50)
    
    test_search_patterns()
    test_confidence_scoring()
    test_municipality_processing()
    
    print("\n" + "=" * 50)
    print("✅ 全テスト完了")
    print("\n次のステップ:")
    print("1. WebDriverの設定を修正")
    print("2. 実際のX検索機能を実装")
    print("3. バッチ処理機能を追加")

if __name__ == "__main__":
    main()
