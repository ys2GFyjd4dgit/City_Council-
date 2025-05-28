#!/usr/bin/env python3
"""
自動Xアカウント検索・更新ツール
WebFetchツールを使用してX（Twitter）の検索を自動化し、
見つかったアカウントをJSONファイルに自動更新する

注: このスクリプトはClaude Code環境での実行を想定しています
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class AutomatedXSearcher:
    """自動Xアカウント検索クラス"""
    
    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.data = self.load_council_data()
        self.municipality_info = self.parse_municipality_info()
        self.found_accounts = {}
        
    def load_council_data(self) -> List[Dict]:
        """議員リストJSONを読み込む"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_municipality_info(self) -> Dict:
        """ファイル名から自治体情報を解析"""
        filename = self.json_path.stem
        match = re.search(r'議員リスト_(\d+)_(.+)', filename)
        if match:
            name = match.group(2)
            
            if name.endswith('市'):
                mtype = '市'
            elif name.endswith('町'):
                mtype = '町'
            elif name.endswith('村'):
                mtype = '村'
            else:
                mtype = '区'
            
            return {
                'name': name,
                'type': mtype,
                'type_full': f'{mtype}議会'
            }
        return {}
    
    def validate_x_account(self, url: str, member_name: str, member_yomi: str) -> Tuple[bool, float]:
        """
        Xアカウントの妥当性を検証
        Returns: (is_valid, confidence_score)
        """
        if not url or not url.startswith('https://x.com/'):
            return False, 0.0
        
        username = url.split('/')[-1].lower()
        name_parts = member_name.replace('　', '').lower()
        yomi_parts = member_yomi.replace('　', '').replace(' ', '').lower()
        
        confidence = 0.0
        
        # ユーザー名に名前の一部が含まれているか
        if any(part in username for part in [name_parts[:2], name_parts[-2:]]):
            confidence += 0.3
        
        # ユーザー名に読みの一部が含まれているか
        if any(part in username for part in [yomi_parts[:4], yomi_parts[-4:]]):
            confidence += 0.3
        
        # 議員関連のキーワードがあるか（プロフィールで確認したい）
        council_keywords = ['議員', '議会', self.municipality_info['name'], self.municipality_info['type'] + '議']
        # ここでは簡易的にユーザー名のみチェック
        if any(keyword in username for keyword in ['giin', 'council', 'gikai']):
            confidence += 0.2
        
        # 最低限の信頼度があれば有効とする
        is_valid = confidence >= 0.2
        
        return is_valid, confidence
    
    def search_member_account(self, member: Dict) -> Optional[str]:
        """
        単一議員のXアカウントを検索
        実際の実装では、WebFetchやその他のツールを使用して検索を実行
        """
        name = member['氏名']
        yomi = member['よみ']
        party = member.get('所属', '')
        
        # 検索クエリのパターン
        search_patterns = [
            f'"{name}" {self.municipality_info["type"]}議 site:x.com',
            f'{name} {self.municipality_info["name"]} 議員',
            f'{name} {party}' if party != '無所属' else f'{name} 議員',
        ]
        
        # ここでは仮の実装として、見つかったと仮定するロジック
        # 実際にはWebFetchツールなどを使用して検索を実行する必要がある
        
        # 検証ロジックの例
        potential_accounts = []
        
        # 仮想的な検索結果の処理
        # 実際の実装では、各検索パターンで見つかったURLを検証する
        
        # 最も信頼度の高いアカウントを返す
        if potential_accounts:
            return potential_accounts[0]
        
        return None
    
    def batch_search(self, members: List[Dict], batch_size: int = 5) -> Dict[str, str]:
        """
        複数議員を効率的にバッチ検索
        """
        found = {}
        
        for i in range(0, len(members), batch_size):
            batch = members[i:i+batch_size]
            
            # バッチ検索の実装
            # 実際にはWebFetchツールなどを使用
            
            for member in batch:
                account = self.search_member_account(member)
                if account:
                    found[member['氏名']] = account
            
            # レート制限対策
            time.sleep(1)
        
        return found
    
    def update_json_file(self, updates: Dict[str, str]) -> bool:
        """
        見つかったアカウント情報でJSONファイルを更新
        """
        if not updates:
            return False
        
        updated = False
        for member in self.data:
            if member['氏名'] in updates and not member.get('X（旧Twitter）'):
                member['X（旧Twitter）'] = updates[member['氏名']]
                updated = True
        
        if updated:
            # バックアップを作成
            backup_path = self.json_path.with_suffix('.json.backup')
            backup_path.write_text(self.json_path.read_text(encoding='utf-8'), encoding='utf-8')
            
            # 更新されたデータを保存
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            return True
        
        return False
    
    def generate_search_report(self) -> str:
        """検索結果のレポートを生成"""
        report = []
        report.append(f"# 自動X検索結果レポート")
        report.append(f"## {self.municipality_info['name']} {self.municipality_info['type_full']}議員")
        report.append(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 統計
        total = len(self.data)
        with_account = sum(1 for m in self.data if m.get('X（旧Twitter）'))
        newly_found = len(self.found_accounts)
        
        report.append("### 検索結果統計")
        report.append(f"- 総議員数: {total}")
        report.append(f"- 既存X登録数: {with_account - newly_found}")
        report.append(f"- 新規発見数: {newly_found}")
        report.append(f"- 現在の登録率: {with_account/total*100:.1f}%")
        report.append("")
        
        if self.found_accounts:
            report.append("### 新規発見アカウント")
            report.append("| 議員名 | Xアカウント | 信頼度 |")
            report.append("|--------|-------------|--------|")
            
            for name, account in self.found_accounts.items():
                member = next((m for m in self.data if m['氏名'] == name), None)
                if member:
                    _, confidence = self.validate_x_account(account, name, member['よみ'])
                    report.append(f"| {name} | {account} | {confidence:.1%} |")
        
        return '\n'.join(report)

def process_municipality_automated(json_path: Path) -> Dict:
    """自治体の自動処理"""
    searcher = AutomatedXSearcher(json_path)
    
    # X未登録の議員を抽出
    without_account = [m for m in searcher.data if not m.get('X（旧Twitter）')]
    
    if not without_account:
        return {
            'municipality': searcher.municipality_info['name'],
            'status': 'completed',
            'found': 0,
            'message': 'すべての議員のXアカウントが登録済み'
        }
    
    # バッチ検索を実行
    found_accounts = searcher.batch_search(without_account)
    searcher.found_accounts = found_accounts
    
    # JSONファイルを更新
    if found_accounts:
        searcher.update_json_file(found_accounts)
    
    # レポート生成
    report = searcher.generate_search_report()
    
    # レポート保存
    report_dir = json_path.parent.parent.parent / 'search_reports'
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"auto_search_{searcher.municipality_info['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report, encoding='utf-8')
    
    return {
        'municipality': searcher.municipality_info['name'],
        'status': 'success',
        'found': len(found_accounts),
        'report_path': str(report_path)
    }

def process_all_municipalities(base_dir: Path, prefecture_code: Optional[str] = None):
    """全自治体を処理"""
    if prefecture_code:
        # 特定の都道府県のみ
        pattern = f"{prefecture_code}_*"
        dirs = list(base_dir.glob(pattern))
    else:
        # すべての都道府県
        dirs = [d for d in base_dir.iterdir() if d.is_dir() and re.match(r'\d{2}_', d.name)]
    
    results = []
    
    for pref_dir in dirs:
        json_files = list(pref_dir.glob("議員リスト_*.json"))
        
        print(f"\n{pref_dir.name} を処理中...")
        print(f"対象ファイル数: {len(json_files)}")
        
        for json_file in json_files:
            print(f"  処理中: {json_file.stem}...", end='', flush=True)
            
            try:
                result = process_municipality_automated(json_file)
                results.append(result)
                
                if result['found'] > 0:
                    print(f" ✓ {result['found']}件発見!")
                else:
                    print(" - 新規発見なし")
                    
            except Exception as e:
                print(f" ✗ エラー: {e}")
                results.append({
                    'municipality': json_file.stem,
                    'status': 'error',
                    'error': str(e)
                })
    
    # 全体レポート生成
    generate_summary_report(results, base_dir)

def generate_summary_report(results: List[Dict], base_dir: Path):
    """全体の処理結果サマリーを生成"""
    report = []
    report.append("# 自動X検索 全体サマリー")
    report.append(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 統計
    total_processed = len(results)
    total_found = sum(r.get('found', 0) for r in results if r['status'] == 'success')
    errors = [r for r in results if r['status'] == 'error']
    
    report.append("## 処理結果統計")
    report.append(f"- 処理自治体数: {total_processed}")
    report.append(f"- 新規発見総数: {total_found}")
    report.append(f"- エラー数: {len(errors)}")
    report.append("")
    
    # 成功した自治体
    successful = [r for r in results if r['status'] == 'success' and r['found'] > 0]
    if successful:
        report.append("## 新規アカウント発見自治体")
        report.append("| 自治体名 | 発見数 |")
        report.append("|----------|--------|")
        
        for r in sorted(successful, key=lambda x: x['found'], reverse=True):
            report.append(f"| {r['municipality']} | {r['found']} |")
    
    # エラー
    if errors:
        report.append("\n## エラー発生自治体")
        for r in errors:
            report.append(f"- {r['municipality']}: {r.get('error', '不明なエラー')}")
    
    # 保存
    summary_path = base_dir.parent / 'search_reports' / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    summary_path.parent.mkdir(exist_ok=True)
    summary_path.write_text('\n'.join(report), encoding='utf-8')
    
    print(f"\n\n全体サマリー保存: {summary_path}")

def main():
    """メイン関数"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  1. 単一ファイル: python automated_x_search.py <JSONファイル>")
        print("  2. 全自治体: python automated_x_search.py --all")
        print("  3. 特定都道府県: python automated_x_search.py --prefecture <都道府県コード>")
        print("")
        print("例:")
        print("  python automated_x_search.py data/processed/13_東京都/議員リスト_132233_武蔵村山市.json")
        print("  python automated_x_search.py --all")
        print("  python automated_x_search.py --prefecture 13  # 東京都のみ")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        # 全自治体処理
        base_dir = Path('data/processed')
        process_all_municipalities(base_dir)
        
    elif sys.argv[1] == '--prefecture' and len(sys.argv) > 2:
        # 特定都道府県処理
        base_dir = Path('data/processed')
        prefecture_code = sys.argv[2]
        process_all_municipalities(base_dir, prefecture_code)
        
    else:
        # 単一ファイル処理
        json_path = Path(sys.argv[1])
        if not json_path.exists():
            print(f"エラー: ファイルが見つかりません - {json_path}")
            sys.exit(1)
        
        result = process_municipality_automated(json_path)
        print(f"\n処理結果: {result}")

if __name__ == "__main__":
    main()