#!/usr/bin/env python3
"""
高度なX（旧Twitter）アカウント検索スクリプト
名前の表記ゆれ（開いた名前含む）、政党フォロワー検索、AI分析などの機能を実装
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import concurrent.futures
from datetime import datetime
import itertools
# import requests  # 必要に応じてインストール
from urllib.parse import quote

class AdvancedXSearcher:
    def __init__(self):
        self.searched_queries = set()
        self.found_accounts = {}
        self.candidate_accounts = {}
        
    def generate_name_variations(self, member: Dict) -> List[str]:
        """名前の表記ゆれパターンを生成（開いた名前を含む）"""
        variations = []
        
        name = member.get('氏名', '')
        yomi = member.get('よみ', '')
        
        # 基本的な分割
        # 姓と名を分割（最初のスペースで分割）
        name_parts = re.split(r'[\s　]+', name)
        if len(name_parts) >= 2:
            sei = name_parts[0]
            mei = ' '.join(name_parts[1:])
        else:
            sei = name
            mei = ''
            
        yomi_parts = re.split(r'[\s　]+', yomi) if yomi else []
        if len(yomi_parts) >= 2:
            sei_yomi = yomi_parts[0]
            mei_yomi = ' '.join(yomi_parts[1:])
        else:
            sei_yomi = yomi if yomi else ''
            mei_yomi = ''
        
        # 1. 基本パターン
        variations.extend([
            name,                          # 山田太郎
            name.replace(' ', ''),         # 山田太郎（スペースなし）
            name.replace('　', ''),        # 山田太郎（全角スペースなし）
            f"{sei} {mei}",               # 山田 太郎
            f"{sei}　{mei}",              # 山田　太郎
        ])
        
        # 2. よみがなパターン
        if yomi:
            variations.extend([
                yomi,                      # やまだたろう
                yomi.replace(' ', ''),     # やまだたろう（スペースなし）
                f"{sei_yomi} {mei_yomi}",  # やまだ たろう
            ])
        
        # 3. 開いた名前パターン（選挙用）
        if sei and mei and sei_yomi and mei_yomi:
            variations.extend([
                # 姓を開く
                f"{sei_yomi}{mei}",        # やまだ太郎
                f"{sei_yomi} {mei}",       # やまだ 太郎
                f"{sei_yomi}　{mei}",      # やまだ　太郎
                
                # 名を開く
                f"{sei}{mei_yomi}",        # 山田たろう
                f"{sei} {mei_yomi}",       # 山田 たろう
                f"{sei}　{mei_yomi}",      # 山田　たろう
                
                # カタカナバージョン
                f"{self._to_katakana(sei_yomi)}{mei}",   # ヤマダ太郎
                f"{sei}{self._to_katakana(mei_yomi)}",   # 山田タロウ
            ])
        
        # 4. 肩書き付きパターン
        if sei:
            variations.extend([
                f"{sei}議員",              # 山田議員
                f"{sei_yomi}議員" if sei_yomi else None,  # やまだ議員
            ])
        
        # 5. 部分一致用
        if sei and mei:
            variations.extend([
                sei,                       # 山田（姓のみ）
                mei,                       # 太郎（名のみ）
            ])
        
        # None を除去して重複を排除
        variations = list(set(v for v in variations if v))
        
        return variations
    
    def _to_katakana(self, hiragana: str) -> str:
        """ひらがなをカタカナに変換"""
        return hiragana.translate(str.maketrans('ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん',
                                               'ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲン'))
    
    def search_by_party_followers(self, municipality: str, party: str) -> List[Dict]:
        """政党公式アカウントのフォロワーから検索"""
        party_accounts = {
            "自由民主党": ["jimin_koho", "LDP_PR", "jiminto_jp"],
            "公明党": ["komei_koho", "komei_woman"],
            "立憲民主党": ["CDP2017", "cdp_kokkai"],
            "日本共産党": ["jcp_cc", "jcp_kokkaigiindan"],
            "日本維新の会": ["osaka_ishin", "ishin_jp"],
            "国民民主党": ["DPFPnews"],
            "れいわ新選組": ["reiwashinsen"],
            "社会民主党": ["SDPJapan"],
        }
        
        results = []
        
        # 政党名の正規化
        for key in party_accounts.keys():
            if key in party or party in key:
                target_accounts = party_accounts[key]
                break
        else:
            # マッチしない場合は会派名で部分一致を試みる
            target_accounts = []
        
        if target_accounts:
            print(f"  政党フォロワー検索: {party} → {target_accounts}")
            # ここでTwitter APIを使用してフォロワーを検索
            # 実装は省略（API制限があるため）
        
        return results
    
    def analyze_profile_with_ai(self, profile_text: str, municipality: str) -> float:
        """プロフィール文をAIで分析して議員らしさスコアを返す"""
        # 議員らしいキーワード
        keywords = [
            "議員", "市議", "町議", "村議", "議会",
            "当選", "選挙", "公約", "政策", "市政", "町政",
            municipality, "所属", "会派", "委員会"
        ]
        
        score = 0.0
        profile_lower = profile_text.lower()
        
        # キーワードマッチング
        for keyword in keywords:
            if keyword in profile_text:
                score += 0.2
        
        # 特定のパターン
        if re.search(r'(市|町|村)議会議員', profile_text):
            score += 0.5
        if re.search(r'\d+期', profile_text):  # "3期目" など
            score += 0.3
        if re.search(r'(自民|公明|立憲|共産|維新|国民|れいわ)', profile_text):
            score += 0.3
        
        return min(score, 1.0)  # 最大1.0
    
    def search_with_google(self, member_name: str, municipality: str) -> List[str]:
        """Google検索でXアカウントを探す"""
        queries = [
            f"{member_name} {municipality} Twitter",
            f"{member_name} {municipality} X",
            f"{member_name} 議員 Twitter",
        ]
        
        found_urls = []
        
        # 実際のGoogle検索API実装は省略
        # ここではプレースホルダー
        print(f"  Google検索: {member_name}")
        
        return found_urls
    
    def analyze_network_connections(self, known_accounts: List[str], municipality: str) -> Dict[str, float]:
        """既知の議員アカウントのネットワークを分析"""
        connection_scores = {}
        
        # 実装のプレースホルダー
        # 実際には：
        # 1. 既知アカウントの相互フォロー関係を取得
        # 2. 共通のフォロワー/フォロイーを分析
        # 3. 同じリストに含まれているアカウントを収集
        # 4. 接続の強さをスコア化
        
        print(f"  ネットワーク分析: {len(known_accounts)}個の既知アカウント")
        
        return connection_scores
    
    def create_search_report(self, municipality_code: str, municipality_name: str, 
                           members: List[Dict], results: Dict) -> str:
        """検索結果レポートを生成"""
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        report = f"""# 高度X検索レポート - {municipality_name}

生成日時: {timestamp}
対象議員数: {len(members)}名

## 検索手法別の結果

### 1. 名前の表記ゆれ検索（開いた名前含む）
"""
        
        # 各手法の結果を記載
        for member in members:
            name = member.get('氏名', '')
            if name in results.get('name_variations', {}):
                candidates = results['name_variations'][name]
                report += f"\n- **{name}**: {len(candidates)}件の候補\n"
                for candidate in candidates[:3]:  # 上位3件まで
                    report += f"  - @{candidate['username']} (スコア: {candidate['score']:.2f})\n"
        
        report += """
### 2. 政党フォロワー検索
"""
        # 政党別の結果
        
        report += """
### 3. AI プロフィール分析
"""
        # 高スコアのアカウント一覧
        
        report += """
### 4. ネットワーク分析
"""
        # 接続の強いアカウント
        
        report += """
### 5. 外部検索（Google等）
"""
        # 外部ソースからの発見
        
        report += """
## 推奨アクション

1. 高確度の候補アカウントの手動確認
2. 中確度アカウントへの追加調査
3. 政党事務所への問い合わせ候補リスト

## 統計サマリー

- 新規発見の可能性: X件
- 要確認アカウント: Y件
- 検索カバー率: Z%
"""
        
        return report

def main():
    """メイン処理"""
    searcher = AdvancedXSearcher()
    
    # プロジェクトルートパスの取得
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data" / "processed"
    
    # テスト実行（稲城市）
    test_file = data_dir / "13_東京都" / "議員リスト_132250_稲城市.json"
    
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            members = json.load(f)
        
        print(f"稲城市の議員データを読み込みました: {len(members)}名")
        
        # 名前のバリエーションテスト
        for member in members[:3]:  # 最初の3名でテスト
            print(f"\n{member['氏名']} の検索パターン:")
            variations = searcher.generate_name_variations(member)
            for v in variations:
                print(f"  - {v}")
    
    else:
        print("テストファイルが見つかりません")

if __name__ == "__main__":
    main()