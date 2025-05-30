#!/usr/bin/env python3
"""
強化版X（旧Twitter）アカウント発見システム
Web検索とプロフィール分析を組み合わせた包括的な検索
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import webbrowser
from urllib.parse import quote, urlparse

class EnhancedXDiscovery:
    def __init__(self):
        self.results = {}
        self.candidates = {}
        self.search_urls = []
        
    def generate_search_urls(self, member: Dict, municipality: str) -> List[Dict]:
        """各種検索エンジンでの検索URLを生成"""
        name = member.get('氏名', '')
        yomi = member.get('よみ', '')
        
        # 名前の分割
        name_parts = re.split(r'[\s　]+', name)
        sei = name_parts[0] if name_parts else name
        
        urls = []
        
        # 1. Google検索
        google_queries = [
            f'"{name}" {municipality} site:twitter.com OR site:x.com',
            f'"{name}" 議員 Twitter OR X',
            f'"{sei}" {municipality}議会議員 Twitter',
        ]
        
        for query in google_queries:
            urls.append({
                'type': 'Google',
                'query': query,
                'url': f"https://www.google.com/search?q={quote(query)}"
            })
        
        # 2. X内検索
        x_queries = [
            f"{name} {municipality}",
            f"{name} 議員",
            f"from:{sei}* {municipality}",  # ユーザー名検索
        ]
        
        for query in x_queries:
            urls.append({
                'type': 'X検索',
                'query': query,
                'url': f"https://x.com/search?q={quote(query)}&f=user"
            })
        
        # 3. 政党サイト検索（所属が分かる場合）
        party = member.get('所属', '')
        if '自民' in party:
            urls.append({
                'type': '政党サイト',
                'query': f"{name} 自民党",
                'url': f"https://www.jimin.jp/search/?q={quote(name)}"
            })
        
        return urls
    
    def analyze_candidate_profile(self, profile_data: Dict, member: Dict, municipality: str) -> float:
        """候補アカウントのプロフィールを分析してスコアを算出"""
        score = 0.0
        
        profile_text = profile_data.get('description', '').lower()
        username = profile_data.get('username', '').lower()
        display_name = profile_data.get('name', '').lower()
        
        # 1. 名前の一致度
        member_name = member.get('氏名', '').lower()
        member_yomi = member.get('よみ', '').lower()
        
        if member_name in display_name or member_name in username:
            score += 0.3
        elif any(part in display_name or part in username for part in member_name.split()):
            score += 0.2
        
        # 2. プロフィールのキーワード
        keywords = {
            '議員': 0.3,
            '市議': 0.3,
            '町議': 0.3,
            '村議': 0.3,
            municipality: 0.2,
            '議会': 0.2,
            '選挙': 0.1,
            '当選': 0.1,
        }
        
        for keyword, weight in keywords.items():
            if keyword in profile_text:
                score += weight
        
        # 3. 所属政党の一致
        party = member.get('所属', '').lower()
        party_keywords = {
            '自民': ['自民党', '自由民主党', 'ldp', 'jimin'],
            '公明': ['公明党', 'komei'],
            '立憲': ['立憲民主党', '立憲', 'cdp'],
            '共産': ['日本共産党', '共産党', 'jcp'],
            '維新': ['日本維新の会', '維新', 'ishin'],
        }
        
        for party_key, party_variations in party_keywords.items():
            if party_key in party:
                if any(var in profile_text for var in party_variations):
                    score += 0.2
                    break
        
        # 4. 場所の一致
        location = profile_data.get('location', '').lower()
        if municipality in location or '東京' in location:
            score += 0.1
        
        return min(score, 1.0)
    
    def generate_candidate_review_html(self, municipality_code: str, municipality_name: str, 
                                     candidates: Dict[str, List[Dict]]) -> str:
        """候補アカウント確認用のHTMLを生成"""
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{municipality_name} - X候補アカウント確認</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .member-section {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .member-name {{ font-size: 20px; font-weight: bold; color: #333; margin-bottom: 15px; }}
        .candidates {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }}
        .candidate {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: #fafafa; }}
        .candidate.high-score {{ border-color: #4CAF50; background: #f1f8f4; }}
        .candidate.medium-score {{ border-color: #FF9800; background: #fff8f1; }}
        .profile-img {{ width: 48px; height: 48px; border-radius: 50%; float: left; margin-right: 10px; }}
        .profile-info {{ overflow: hidden; }}
        .username {{ font-weight: bold; color: #1DA1F2; }}
        .score {{ float: right; padding: 2px 8px; border-radius: 3px; font-size: 12px; }}
        .score.high {{ background: #4CAF50; color: white; }}
        .score.medium {{ background: #FF9800; color: white; }}
        .score.low {{ background: #9E9E9E; color: white; }}
        .description {{ margin-top: 10px; font-size: 14px; color: #666; }}
        .action-buttons {{ margin-top: 10px; }}
        .btn {{ padding: 5px 15px; margin-right: 5px; border: none; border-radius: 3px; cursor: pointer; }}
        .btn-correct {{ background: #4CAF50; color: white; }}
        .btn-wrong {{ background: #f44336; color: white; }}
        .btn-unsure {{ background: #9E9E9E; color: white; }}
        .search-links {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee; }}
        .search-link {{ margin-right: 10px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{municipality_name} - X候補アカウント確認</h1>
        <p>生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
        
"""
        
        for member_name, member_candidates in candidates.items():
            if not member_candidates:
                continue
                
            html += f"""
        <div class="member-section">
            <div class="member-name">{member_name}</div>
            <div class="candidates">
"""
            
            # スコア順にソート
            sorted_candidates = sorted(member_candidates, key=lambda x: x.get('score', 0), reverse=True)
            
            for candidate in sorted_candidates[:6]:  # 上位6件まで表示
                score = candidate.get('score', 0)
                score_class = 'high' if score >= 0.7 else 'medium' if score >= 0.4 else 'low'
                candidate_class = 'high-score' if score >= 0.7 else 'medium-score' if score >= 0.4 else ''
                
                html += f"""
                <div class="candidate {candidate_class}">
                    <img src="https://via.placeholder.com/48" class="profile-img" alt="Profile">
                    <div class="profile-info">
                        <span class="username">@{candidate.get('username', 'unknown')}</span>
                        <span class="score {score_class}">{score:.2f}</span>
                        <div class="description">{candidate.get('description', '(プロフィールなし)')[:100]}...</div>
                    </div>
                    <div class="action-buttons">
                        <button class="btn btn-correct" onclick="markCorrect('{member_name}', '{candidate.get('username')}')">正しい</button>
                        <button class="btn btn-wrong" onclick="markWrong('{member_name}', '{candidate.get('username')}')">違う</button>
                        <button class="btn btn-unsure" onclick="markUnsure('{member_name}', '{candidate.get('username')}')">不明</button>
                    </div>
                </div>
"""
            
            html += """
            </div>
            <div class="search-links">
                <strong>追加検索:</strong>
"""
            
            # 検索リンクを追加
            search_queries = [
                ('Google', f'https://www.google.com/search?q={quote(member_name + " " + municipality_name + " Twitter")}'),
                ('X検索', f'https://x.com/search?q={quote(member_name)}&f=user'),
            ]
            
            for label, url in search_queries:
                html += f'<a href="{url}" target="_blank" class="search-link">{label}</a>'
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <script>
        function markCorrect(memberName, username) {
            console.log('正しい:', memberName, username);
            // TODO: 結果を保存
            alert('「' + memberName + '」のアカウント @' + username + ' を正しいと記録しました');
        }
        
        function markWrong(memberName, username) {
            console.log('違う:', memberName, username);
            // TODO: 結果を保存
        }
        
        function markUnsure(memberName, username) {
            console.log('不明:', memberName, username);
            // TODO: 結果を保存
        }
    </script>
</body>
</html>
"""
        
        return html
    
    def save_review_html(self, municipality_code: str, municipality_name: str, 
                        candidates: Dict[str, List[Dict]]) -> Path:
        """確認用HTMLファイルを保存"""
        output_dir = Path(__file__).parent.parent / "data" / "reports" / "x_candidates"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"candidates_{municipality_code}_{municipality_name}.html"
        
        html_content = self.generate_candidate_review_html(
            municipality_code, municipality_name, candidates
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file

def main():
    """メイン処理（デモ）"""
    discovery = EnhancedXDiscovery()
    
    # テストデータ
    test_member = {
        '氏名': '山田太郎',
        'よみ': 'やまだ たろう',
        '所属': '自由民主党'
    }
    
    # 検索URL生成のデモ
    urls = discovery.generate_search_urls(test_member, '稲城市')
    
    print("生成された検索URL:")
    for url_data in urls:
        print(f"\n[{url_data['type']}] {url_data['query']}")
        print(f"  → {url_data['url']}")
    
    # 候補アカウントの例（デモ用）
    demo_candidates = {
        '山田太郎': [
            {
                'username': 'yamada_taro',
                'description': '稲城市議会議員の山田太郎です。自民党所属。市民の声を市政に！',
                'score': 0.9
            },
            {
                'username': 'taro_yamada2023',
                'description': '東京都在住。政治に興味があります。',
                'score': 0.3
            }
        ]
    }
    
    # HTML生成のデモ
    html_file = discovery.save_review_html('132250', '稲城市', demo_candidates)
    print(f"\n確認用HTMLを生成しました: {html_file}")
    
    # ブラウザで開く
    # webbrowser.open(f"file://{html_file.absolute()}")

if __name__ == "__main__":
    main()