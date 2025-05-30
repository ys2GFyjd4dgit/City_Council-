#!/usr/bin/env python3
"""
統合X（旧Twitter）アカウント検索システム
複数の検索手法を組み合わせて議員のXアカウントを効率的に発見
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import webbrowser
from urllib.parse import quote
import concurrent.futures
import sys

# 既存のスクリプトから必要な機能をインポート
sys.path.append(str(Path(__file__).parent))
from advanced_x_search import AdvancedXSearcher
from enhanced_x_discovery import EnhancedXDiscovery

class IntegratedXSearchSystem:
    def __init__(self):
        self.advanced_searcher = AdvancedXSearcher()
        self.discovery_system = EnhancedXDiscovery()
        self.search_results = {}
        self.new_accounts_found = {}
        
    def search_municipality(self, json_path: Path) -> Dict:
        """自治体のすべての議員を検索"""
        # JSONファイルを読み込む
        with open(json_path, 'r', encoding='utf-8') as f:
            members = json.load(f)
        
        # ファイル名から自治体情報を取得
        filename = json_path.stem
        parts = filename.split('_')
        municipality_code = parts[1] if len(parts) > 1 else 'unknown'
        municipality_name = parts[2] if len(parts) > 2 else 'unknown'
        
        print(f"\n{'='*60}")
        print(f"{municipality_name} ({municipality_code}) の検索を開始")
        print(f"議員数: {len(members)}名")
        print(f"{'='*60}\n")
        
        # X未登録の議員のみを対象とする
        unregistered_members = [m for m in members if not m.get('X（旧Twitter）')]
        print(f"X未登録議員数: {len(unregistered_members)}名")
        
        results = {
            'municipality': municipality_name,
            'code': municipality_code,
            'total_members': len(members),
            'unregistered_count': len(unregistered_members),
            'search_results': {},
            'candidates': {},
            'search_urls': {}
        }
        
        # 各議員を検索
        for i, member in enumerate(unregistered_members):
            member_name = member.get('氏名', '')
            print(f"\n[{i+1}/{len(unregistered_members)}] {member_name} を検索中...")
            
            # 1. 名前のバリエーションを生成
            name_variations = self.advanced_searcher.generate_name_variations(member)
            print(f"  → {len(name_variations)}個の名前パターンを生成")
            
            # 2. 検索URLを生成
            search_urls = self.discovery_system.generate_search_urls(member, municipality_name)
            results['search_urls'][member_name] = search_urls
            
            # 3. 候補アカウントを収集（実際のAPI実装は省略）
            candidates = self._mock_search_candidates(member, name_variations, municipality_name)
            
            if candidates:
                print(f"  → {len(candidates)}個の候補アカウントを発見")
                results['candidates'][member_name] = candidates
            else:
                print(f"  → 候補アカウントなし")
        
        # 結果を保存
        self._save_results(results, municipality_code, municipality_name)
        
        return results
    
    def _mock_search_candidates(self, member: Dict, name_variations: List[str], 
                              municipality: str) -> List[Dict]:
        """候補アカウントの模擬検索（実際のAPI実装の代わり）"""
        # 実際の実装では、Twitter APIやWebスクレイピングを使用
        # ここではデモ用の模擬データを返す
        
        candidates = []
        
        # 名前の一部が含まれる場合、候補として追加
        member_name = member.get('氏名', '')
        name_parts = re.split(r'[\s　]+', member_name)
        
        # デモ: 10%の確率で候補を見つける
        import random
        if random.random() < 0.1:
            sei = name_parts[0] if name_parts else member_name
            candidates.append({
                'username': f"{sei.lower()}_council",
                'display_name': member_name,
                'description': f'{municipality}議会議員',
                'score': 0.8,
                'source': 'mock_search'
            })
        
        return candidates
    
    def _save_results(self, results: Dict, municipality_code: str, municipality_name: str):
        """検索結果を保存"""
        # レポートディレクトリ
        report_dir = Path(__file__).parent.parent / "data" / "reports" / "integrated_search"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. JSON形式で保存
        json_file = report_dir / f"results_{municipality_code}_{municipality_name}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 2. Markdownレポートを生成
        report_file = report_dir / f"report_{municipality_code}_{municipality_name}.md"
        report_content = self._generate_report(results)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 3. 候補確認用HTMLを生成
        if results.get('candidates'):
            html_file = self.discovery_system.save_review_html(
                municipality_code, municipality_name, results['candidates']
            )
            print(f"\n候補確認用HTML: {html_file}")
        
        print(f"\n検索結果を保存しました:")
        print(f"  - JSON: {json_file}")
        print(f"  - レポート: {report_file}")
    
    def _generate_report(self, results: Dict) -> str:
        """検索結果のMarkdownレポートを生成"""
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        report = f"""# 統合X検索レポート - {results['municipality']}

生成日時: {timestamp}

## 概要

- 総議員数: {results['total_members']}名
- X未登録議員数: {results['unregistered_count']}名
- 候補アカウント発見数: {len(results.get('candidates', {}))}名

## 候補アカウント一覧

"""
        
        # 候補アカウントをリスト
        candidates = results.get('candidates', {})
        if candidates:
            for member_name, member_candidates in candidates.items():
                report += f"### {member_name}\n\n"
                
                for candidate in sorted(member_candidates, key=lambda x: x.get('score', 0), reverse=True):
                    report += f"- **@{candidate['username']}** (スコア: {candidate.get('score', 0):.2f})\n"
                    report += f"  - 表示名: {candidate.get('display_name', 'N/A')}\n"
                    report += f"  - プロフィール: {candidate.get('description', 'N/A')[:100]}...\n"
                    report += f"  - ソース: {candidate.get('source', 'unknown')}\n\n"
        else:
            report += "*候補アカウントは見つかりませんでした。*\n\n"
        
        report += """## 検索URL一覧

以下のURLで手動検索を行うことができます:

"""
        
        # 検索URLをリスト（最初の5名分のみ）
        search_urls = results.get('search_urls', {})
        for i, (member_name, urls) in enumerate(list(search_urls.items())[:5]):
            report += f"### {member_name}\n\n"
            for url_data in urls[:3]:  # 各議員につき3つまで
                report += f"- [{url_data['type']}]({url_data['url']})\n"
            report += "\n"
        
        if len(search_urls) > 5:
            report += f"*他 {len(search_urls) - 5}名の検索URLは省略*\n\n"
        
        report += """## 推奨アクション

1. 候補アカウントの確認用HTMLを開いて手動確認
2. 高スコアの候補から優先的に確認
3. 確認済みアカウントをJSONファイルに反映
4. 低スコアや候補なしの議員は手動検索URLを使用

## 統計情報

- 名前バリエーション生成: 完了
- 検索URL生成: 完了
- 候補発見率: {:.1f}%
""".format(len(candidates) / results['unregistered_count'] * 100 if results['unregistered_count'] > 0 else 0)
        
        return report
    
    def batch_search(self, prefecture_dir: Path, max_municipalities: int = None):
        """都道府県内の複数自治体を一括検索"""
        json_files = list(prefecture_dir.glob("議員リスト_*.json"))
        
        if max_municipalities:
            json_files = json_files[:max_municipalities]
        
        print(f"\n{len(json_files)}個の自治体を検索します")
        
        all_results = []
        
        for json_file in json_files:
            try:
                results = self.search_municipality(json_file)
                all_results.append(results)
                
                # レート制限対策
                time.sleep(2)
                
            except Exception as e:
                print(f"\nエラー: {json_file.name} - {e}")
                continue
        
        # サマリーレポートを生成
        self._generate_summary_report(all_results, prefecture_dir.name)
        
        return all_results
    
    def _generate_summary_report(self, all_results: List[Dict], prefecture: str):
        """複数自治体の検索結果サマリーを生成"""
        report_dir = Path(__file__).parent.parent / "data" / "reports" / "integrated_search"
        summary_file = report_dir / f"summary_{prefecture}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        total_unregistered = sum(r['unregistered_count'] for r in all_results)
        total_candidates = sum(len(r.get('candidates', {})) for r in all_results)
        
        summary = f"""# 統合X検索サマリー - {prefecture}

生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 全体統計

- 検索自治体数: {len(all_results)}
- 総X未登録議員数: {total_unregistered}名
- 総候補アカウント発見数: {total_candidates}名
- 平均発見率: {total_candidates / total_unregistered * 100:.1f}%

## 自治体別結果

| 自治体 | 未登録数 | 候補発見数 | 発見率 |
|--------|----------|-----------|--------|
"""
        
        for result in sorted(all_results, key=lambda x: len(x.get('candidates', {})), reverse=True):
            candidates = len(result.get('candidates', {}))
            unregistered = result['unregistered_count']
            rate = candidates / unregistered * 100 if unregistered > 0 else 0
            
            summary += f"| {result['municipality']} | {unregistered} | {candidates} | {rate:.1f}% |\n"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\nサマリーレポート: {summary_file}")

def main():
    """メイン処理"""
    system = IntegratedXSearchSystem()
    
    # コマンドライン引数の処理
    import argparse
    parser = argparse.ArgumentParser(description='統合X検索システム')
    parser.add_argument('target', nargs='?', help='検索対象（JSONファイルパスまたは都道府県ディレクトリ）')
    parser.add_argument('--batch', action='store_true', help='バッチ処理モード')
    parser.add_argument('--max', type=int, help='バッチ処理の最大自治体数')
    
    args = parser.parse_args()
    
    if args.target:
        target_path = Path(args.target)
        
        if target_path.is_file() and target_path.suffix == '.json':
            # 単一ファイルの検索
            system.search_municipality(target_path)
        elif target_path.is_dir() and args.batch:
            # バッチ処理
            system.batch_search(target_path, args.max)
        else:
            print("エラー: 有効なJSONファイルまたはディレクトリを指定してください")
    else:
        # デモ実行
        print("使用方法:")
        print("  python integrated_x_search.py [JSONファイル]")
        print("  python integrated_x_search.py [都道府県ディレクトリ] --batch")
        print("\nデモ: 稲城市を検索")
        
        demo_file = Path(__file__).parent.parent / "data" / "processed" / "13_東京都" / "議員リスト_132250_稲城市.json"
        if demo_file.exists():
            system.search_municipality(demo_file)
        else:
            print(f"デモファイルが見つかりません: {demo_file}")

if __name__ == "__main__":
    main()