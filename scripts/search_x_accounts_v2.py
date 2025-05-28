#!/usr/bin/env python3
"""
Xアカウント検索支援ツール v2.0
市町村議会議員のXアカウントを効率的に検索するための強化版ヘルパースクリプト

主な改善点:
- 市議会だけでなく町議会・村議会にも対応
- 並列処理による高速化
- より多様な検索戦略
- 検索結果の自動保存とレポート生成
"""

import json
import sys
import re
import time
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import webbrowser
import urllib.parse

class XAccountSearcher:
    """Xアカウント検索クラス"""
    
    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.data = self.load_council_data()
        self.municipality_info = self.parse_municipality_info()
        
    def load_council_data(self) -> List[Dict]:
        """議員リストJSONを読み込む"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_municipality_info(self) -> Dict:
        """ファイル名から自治体情報を解析"""
        filename = self.json_path.stem
        match = re.search(r'議員リスト_(\d+)_(.+)', filename)
        if match:
            code = match.group(1)
            name = match.group(2)
            
            # 自治体タイプを判定
            if name.endswith('市'):
                mtype = '市'
                mtype_full = '市議会'
            elif name.endswith('町'):
                mtype = '町'
                mtype_full = '町議会'
            elif name.endswith('村'):
                mtype = '村'
                mtype_full = '村議会'
            else:
                mtype = '区'
                mtype_full = '区議会'
            
            return {
                'code': code,
                'name': name,
                'type': mtype,
                'type_full': mtype_full
            }
        return {}
    
    def generate_search_queries(self, member: Dict) -> List[Dict]:
        """議員情報から多様な検索クエリを生成"""
        name = member['氏名']
        name_no_space = name.replace('　', '')
        yomi = member['よみ']
        reading = yomi.replace('　', '').replace(' ', '')
        party = member.get('所属', '')
        
        muni = self.municipality_info
        muni_name = muni.get('name', '')
        muni_type = muni.get('type', '市')
        muni_type_full = muni.get('type_full', '市議会')
        
        # 姓と名を分離
        parts = name.split('　')
        family_name = parts[0] if parts else ''
        given_name = parts[1] if len(parts) > 1 else ''
        
        # 読みから姓名を分離
        yomi_parts = yomi.split('　')
        family_yomi = yomi_parts[0] if yomi_parts else ''
        given_yomi = yomi_parts[1] if len(yomi_parts) > 1 else ''
        
        queries = []
        
        # 1. 基本的な検索クエリ
        queries.extend([
            {'query': f'"{name}" {muni_type}議 site:x.com', 'priority': 'high'},
            {'query': f'"{name}" {muni_type_full}', 'priority': 'high'},
            {'query': f'"{name}" {muni_name}', 'priority': 'high'},
            {'query': f'{name_no_space} {muni_type}議', 'priority': 'medium'},
        ])
        
        # 2. 所属政党を含む検索
        if party and party != '無所属':
            queries.extend([
                {'query': f'"{name}" {party}', 'priority': 'medium'},
                {'query': f'{family_name} {party} {muni_type}議', 'priority': 'low'},
            ])
        
        # 3. ユーザー名検索（@で始まる）
        # 読みベース
        queries.extend([
            {'query': f'@{reading[:6]}', 'priority': 'low'},  # 読みの最初6文字
            {'query': f'@{family_yomi}{given_yomi[:2]}', 'priority': 'low'},  # 姓の読み+名の最初2文字
            {'query': f'@{given_yomi}{family_yomi[:2]}', 'priority': 'low'},  # 名の読み+姓の最初2文字
        ])
        
        # 漢字ベース
        queries.extend([
            {'query': f'@{family_name}{given_name[:1]}', 'priority': 'low'},  # 姓+名の1文字
            {'query': f'@{name_no_space}', 'priority': 'low'},  # フルネーム
        ])
        
        # 4. プロフィール検索
        queries.extend([
            {'query': f'{muni_name}{muni_type_full}議員 {family_name}', 'priority': 'medium'},
            {'query': f'{muni_name} 議員 {name}', 'priority': 'medium'},
        ])
        
        # 5. 選挙関連の検索
        queries.extend([
            {'query': f'{name} 選挙 {muni_name}', 'priority': 'low'},
            {'query': f'{name} 当選', 'priority': 'low'},
        ])
        
        return queries
    
    def check_existing_accounts(self) -> Tuple[List[Dict], List[Dict]]:
        """既存のXアカウント情報を確認"""
        with_account = []
        without_account = []
        
        for member in self.data:
            if member.get('X（旧Twitter）'):
                with_account.append(member)
            else:
                without_account.append(member)
        
        return with_account, without_account
    
    def generate_batch_search_url(self, members: List[Dict], max_members: int = 5) -> List[str]:
        """複数議員をまとめて検索するURLを生成"""
        urls = []
        muni_name = self.municipality_info.get('name', '')
        muni_type_full = self.municipality_info.get('type_full', '市議会')
        
        for i in range(0, len(members), max_members):
            batch = members[i:i+max_members]
            names = ' OR '.join([f'"{m["氏名"]}"' for m in batch])
            query = f'{names} {muni_name}{muni_type_full}'
            encoded_query = urllib.parse.quote(query)
            url = f"https://x.com/search?q={encoded_query}&f=user"
            urls.append(url)
        
        return urls
    
    def generate_report(self, output_path: Optional[Path] = None):
        """検索レポートを生成"""
        with_account, without_account = self.check_existing_accounts()
        muni_info = self.municipality_info
        
        report = []
        report.append(f"# Xアカウント検索レポート")
        report.append(f"## {muni_info.get('name', '')} {muni_info.get('type_full', '')}議員")
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 統計情報
        report.append(f"### 統計")
        report.append(f"- 総議員数: {len(self.data)}")
        report.append(f"- Xアカウント登録済み: {len(with_account)} ({len(with_account)/len(self.data)*100:.1f}%)")
        report.append(f"- 未登録: {len(without_account)} ({len(without_account)/len(self.data)*100:.1f}%)")
        report.append("")
        
        # 登録済みアカウント
        if with_account:
            report.append("### Xアカウント登録済み議員")
            report.append("| 氏名 | 所属 | Xアカウント |")
            report.append("|------|------|-------------|")
            for member in sorted(with_account, key=lambda x: x['よみ']):
                url = member['X（旧Twitter）']
                username = url.split('/')[-1] if url else ''
                report.append(f"| {member['氏名']} | {member['所属']} | [@{username}]({url}) |")
            report.append("")
        
        # 未登録議員の検索戦略
        if without_account:
            report.append("### Xアカウント未登録議員")
            report.append("")
            
            # バッチ検索URL
            batch_urls = self.generate_batch_search_url(without_account)
            report.append("#### 一括検索URL（5名ずつ）")
            for i, url in enumerate(batch_urls, 1):
                report.append(f"{i}. [バッチ{i}検索]({url})")
            report.append("")
            
            # 個別検索
            report.append("#### 個別検索クエリ")
            for member in sorted(without_account, key=lambda x: x['よみ']):
                report.append(f"\n**{member['氏名']} ({member['よみ']}) - {member['所属']}**")
                queries = self.generate_search_queries(member)
                
                # 優先度別に整理
                high_queries = [q for q in queries if q['priority'] == 'high']
                medium_queries = [q for q in queries if q['priority'] == 'medium']
                
                report.append("- 優先検索:")
                for q in high_queries[:3]:  # 上位3つ
                    encoded = urllib.parse.quote(q['query'])
                    url = f"https://x.com/search?q={encoded}&f=user"
                    report.append(f"  - [{q['query']}]({url})")
                
                if medium_queries:
                    report.append("- 追加検索:")
                    for q in medium_queries[:2]:  # 上位2つ
                        encoded = urllib.parse.quote(q['query'])
                        url = f"https://x.com/search?q={encoded}&f=user"
                        report.append(f"  - [{q['query']}]({url})")
        
        # レポートの保存
        report_text = '\n'.join(report)
        
        if output_path:
            output_path.write_text(report_text, encoding='utf-8')
        else:
            # デフォルトの出力先
            output_dir = self.json_path.parent.parent.parent / 'reports'
            output_dir.mkdir(exist_ok=True)
            filename = f"x_search_{muni_info.get('name', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            output_path = output_dir / filename
            output_path.write_text(report_text, encoding='utf-8')
        
        return output_path, report_text
    
    def open_searches_in_browser(self, max_tabs: int = 5):
        """ブラウザで検索を開く（タブ数制限付き）"""
        _, without_account = self.check_existing_accounts()
        
        if not without_account:
            print("すべての議員のXアカウントが登録済みです。")
            return
        
        print(f"\n未登録議員数: {len(without_account)}")
        print(f"最初の{min(max_tabs, len(without_account))}名の検索をブラウザで開きます...")
        
        for i, member in enumerate(without_account[:max_tabs]):
            queries = self.generate_search_queries(member)
            # 最優先のクエリを開く
            if queries:
                query = queries[0]['query']
                encoded = urllib.parse.quote(query)
                url = f"https://x.com/search?q={encoded}&f=user"
                webbrowser.open(url)
                time.sleep(0.5)  # タブが開きすぎないよう遅延
        
        print(f"\n検索タブを開きました。結果を確認してください。")

def parallel_search_all_municipalities(prefecture_dir: Path, max_workers: int = 4):
    """都道府県内の全自治体を並列で処理"""
    json_files = list(prefecture_dir.glob("議員リスト_*.json"))
    
    if not json_files:
        print(f"{prefecture_dir} にJSONファイルが見つかりません。")
        return
    
    print(f"{len(json_files)}個の自治体を処理します...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_municipality, json_file): json_file 
            for json_file in json_files
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            json_file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                print(f"✓ {json_file.stem} 処理完了")
            except Exception as exc:
                print(f"✗ {json_file.stem} エラー: {exc}")
    
    # 統合レポートの生成
    generate_prefecture_report(prefecture_dir, results)

def process_municipality(json_path: Path) -> Dict:
    """単一自治体の処理"""
    searcher = XAccountSearcher(json_path)
    with_account, without_account = searcher.check_existing_accounts()
    
    return {
        'path': json_path,
        'name': searcher.municipality_info.get('name', ''),
        'total': len(searcher.data),
        'with_account': len(with_account),
        'without_account': len(without_account),
        'percentage': len(with_account) / len(searcher.data) * 100 if searcher.data else 0
    }

def generate_prefecture_report(prefecture_dir: Path, results: List[Dict]):
    """都道府県レベルの統合レポート生成"""
    report = []
    report.append(f"# {prefecture_dir.name} Xアカウント収集状況")
    report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 統計
    total_members = sum(r['total'] for r in results)
    total_with_account = sum(r['with_account'] for r in results)
    
    report.append("## 統計サマリー")
    report.append(f"- 自治体数: {len(results)}")
    report.append(f"- 総議員数: {total_members}")
    report.append(f"- Xアカウント登録済み: {total_with_account} ({total_with_account/total_members*100:.1f}%)")
    report.append("")
    
    # 自治体別詳細
    report.append("## 自治体別詳細")
    report.append("| 自治体名 | 議員数 | X登録数 | 登録率 | 未登録数 |")
    report.append("|----------|--------|---------|--------|----------|")
    
    # 登録率でソート
    sorted_results = sorted(results, key=lambda x: x['percentage'], reverse=True)
    
    for r in sorted_results:
        report.append(
            f"| {r['name']} | {r['total']} | {r['with_account']} | "
            f"{r['percentage']:.1f}% | {r['without_account']} |"
        )
    
    # 保存
    output_path = prefecture_dir.parent.parent / 'reports' / f"{prefecture_dir.name}_summary_{datetime.now().strftime('%Y%m%d')}.md"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text('\n'.join(report), encoding='utf-8')
    print(f"\n統合レポート保存: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  1. 単一ファイル: python search_x_accounts_v2.py <議員リストJSONファイル>")
        print("  2. 都道府県一括: python search_x_accounts_v2.py --prefecture <都道府県ディレクトリ>")
        print("  3. ブラウザ検索: python search_x_accounts_v2.py --browser <議員リストJSONファイル>")
        print("")
        print("例:")
        print("  python search_x_accounts_v2.py data/processed/13_東京都/議員リスト_132233_武蔵村山市.json")
        print("  python search_x_accounts_v2.py --prefecture data/processed/13_東京都")
        print("  python search_x_accounts_v2.py --browser data/processed/11_埼玉県/議員リスト_112089_所沢市.json")
        sys.exit(1)
    
    if sys.argv[1] == '--prefecture' and len(sys.argv) > 2:
        # 都道府県一括処理モード
        prefecture_dir = Path(sys.argv[2])
        if not prefecture_dir.exists():
            print(f"エラー: ディレクトリが見つかりません - {prefecture_dir}")
            sys.exit(1)
        parallel_search_all_municipalities(prefecture_dir)
    
    elif sys.argv[1] == '--browser' and len(sys.argv) > 2:
        # ブラウザ検索モード
        json_path = Path(sys.argv[2])
        if not json_path.exists():
            print(f"エラー: ファイルが見つかりません - {json_path}")
            sys.exit(1)
        searcher = XAccountSearcher(json_path)
        searcher.open_searches_in_browser()
    
    else:
        # 単一ファイル処理モード
        json_path = Path(sys.argv[1])
        if not json_path.exists():
            print(f"エラー: ファイルが見つかりません - {json_path}")
            sys.exit(1)
        
        searcher = XAccountSearcher(json_path)
        output_path, report = searcher.generate_report()
        
        print(f"\nレポート生成完了: {output_path}")
        print("\n" + "="*60)
        print(report)

if __name__ == "__main__":
    main()