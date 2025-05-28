#!/usr/bin/env python3
"""
包括的Xアカウント発見システム
複数の戦略を組み合わせて議員のXアカウントを効率的に発見する

戦略:
1. 直接検索（名前、読み、所属）
2. フォロー関係分析（既知アカウントのフォロー/フォロワー）
3. リスト分析（議会公式アカウントのリスト）
4. ハッシュタグ分析（地域の選挙関連タグ）
5. メンション分析（議会関連アカウントへのメンション）
"""

import json
import re
import csv
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import urllib.parse

class ComprehensiveXDiscovery:
    """包括的Xアカウント発見クラス"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.known_accounts = self.load_all_known_accounts()
        self.municipality_graph = self.build_municipality_graph()
        
    def load_all_known_accounts(self) -> Dict[str, Dict]:
        """全自治体の既知Xアカウントを読み込み"""
        known = {}
        
        for json_file in self.base_path.glob("**/議員リスト_*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            muni_name = json_file.stem.split('_')[-1]
            
            for member in data:
                if member.get('X（旧Twitter）'):
                    known[member['X（旧Twitter）']] = {
                        'name': member['氏名'],
                        'municipality': muni_name,
                        'party': member.get('所属', ''),
                        'reading': member.get('よみ', '')
                    }
        
        return known
    
    def build_municipality_graph(self) -> Dict[str, Set[str]]:
        """自治体間の関係グラフを構築（同じ政党、近隣など）"""
        graph = defaultdict(set)
        
        # 都道府県別にグループ化
        prefecture_groups = defaultdict(list)
        
        for json_file in self.base_path.glob("**/議員リスト_*.json"):
            # 都道府県コードを抽出
            prefecture_match = re.search(r'/(\d{2}_[^/]+)/', str(json_file))
            if prefecture_match:
                prefecture = prefecture_match.group(1)
                muni_name = json_file.stem.split('_')[-1]
                prefecture_groups[prefecture].append(muni_name)
        
        # 同じ都道府県内の自治体を関連付け
        for prefecture, municipalities in prefecture_groups.items():
            for i, muni1 in enumerate(municipalities):
                for muni2 in municipalities[i+1:]:
                    graph[muni1].add(muni2)
                    graph[muni2].add(muni1)
        
        return dict(graph)
    
    def generate_search_strategies(self, member: Dict, municipality_info: Dict) -> List[Dict]:
        """メンバーごとの検索戦略を生成"""
        strategies = []
        
        name = member['氏名']
        name_no_space = name.replace('　', '')
        reading = member['よみ'].replace('　', '').replace(' ', '')
        party = member.get('所属', '')
        muni_name = municipality_info['name']
        muni_type = municipality_info['type']
        
        # 1. 基本検索戦略
        strategies.append({
            'type': 'direct_search',
            'queries': [
                f'"{name}" {muni_type}議 -RT',
                f'"{name}" {muni_name} 議員',
                f'{name_no_space} プロフィール {muni_type}議',
            ],
            'priority': 'high'
        })
        
        # 2. ユーザー名パターン
        name_parts = name.split('　')
        if len(name_parts) >= 2:
            family = name_parts[0]
            given = name_parts[1]
            
            strategies.append({
                'type': 'username_patterns',
                'patterns': [
                    f'@{family}{given[:1]}',  # 姓+名の1文字
                    f'@{family}_{given}',     # 姓_名
                    f'@{reading[:6]}',        # 読みの最初6文字
                    f'@{given}{family[:1]}',  # 名+姓の1文字
                ],
                'priority': 'medium'
            })
        
        # 3. 所属政党関連
        if party and party != '無所属':
            strategies.append({
                'type': 'party_search',
                'queries': [
                    f'{party} {muni_name} {family}',
                    f'"{party}" メンバー {name}',
                ],
                'priority': 'medium'
            })
        
        # 4. 選挙関連検索
        strategies.append({
            'type': 'election_search',
            'queries': [
                f'{name} 当選 {muni_name}',
                f'#{muni_name}選挙 {name}',
                f'{name} 選挙ポスター',
            ],
            'priority': 'low'
        })
        
        # 5. リレーション検索（既知アカウントとの関連）
        if self.known_accounts:
            related_accounts = self.find_related_accounts(member, municipality_info)
            if related_accounts:
                strategies.append({
                    'type': 'relation_search',
                    'accounts': related_accounts,
                    'priority': 'high'
                })
        
        return strategies
    
    def find_related_accounts(self, member: Dict, municipality_info: Dict) -> List[str]:
        """関連する既知アカウントを検索"""
        related = []
        muni_name = municipality_info['name']
        party = member.get('所属', '')
        
        for account_url, info in self.known_accounts.items():
            # 同じ自治体
            if info['municipality'] == muni_name:
                related.append(account_url)
            # 同じ政党（異なる自治体）
            elif party and party != '無所属' and info['party'] == party:
                related.append(account_url)
            # 近隣自治体
            elif muni_name in self.municipality_graph and info['municipality'] in self.municipality_graph[muni_name]:
                related.append(account_url)
        
        return related[:10]  # 最大10件
    
    def generate_discovery_plan(self, json_path: Path) -> Dict:
        """自治体の発見計画を生成"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 自治体情報を解析
        filename = json_path.stem
        match = re.search(r'議員リスト_(\d+)_(.+)', filename)
        if not match:
            return {}
        
        muni_name = match.group(2)
        muni_type = '市' if muni_name.endswith('市') else '町' if muni_name.endswith('町') else '村'
        
        municipality_info = {
            'name': muni_name,
            'type': muni_type,
            'code': match.group(1)
        }
        
        # アカウント未登録の議員を抽出
        without_account = [m for m in data if not m.get('X（旧Twitter）')]
        
        plan = {
            'municipality': municipality_info,
            'total_members': len(data),
            'without_account': len(without_account),
            'strategies': []
        }
        
        # 各議員の検索戦略を生成
        for member in without_account:
            member_strategies = self.generate_search_strategies(member, municipality_info)
            plan['strategies'].append({
                'member': member,
                'search_strategies': member_strategies
            })
        
        return plan
    
    def export_search_urls(self, plan: Dict, output_path: Path):
        """検索URLをCSV形式でエクスポート"""
        rows = []
        
        for strategy in plan['strategies']:
            member = strategy['member']
            member_name = member['氏名']
            
            for search_strategy in strategy['search_strategies']:
                if search_strategy['type'] in ['direct_search', 'party_search', 'election_search']:
                    for query in search_strategy.get('queries', []):
                        encoded = urllib.parse.quote(query)
                        url = f"https://x.com/search?q={encoded}&f=user"
                        rows.append({
                            'member_name': member_name,
                            'strategy_type': search_strategy['type'],
                            'priority': search_strategy['priority'],
                            'query': query,
                            'url': url
                        })
        
        # CSV出力
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['member_name', 'strategy_type', 'priority', 'query', 'url'])
            writer.writeheader()
            writer.writerows(rows)
    
    def generate_comprehensive_report(self, plans: List[Dict]) -> str:
        """包括的な発見レポートを生成"""
        report = []
        report.append("# 包括的Xアカウント発見レポート")
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 全体統計
        total_municipalities = len(plans)
        total_members = sum(p['total_members'] for p in plans)
        total_without = sum(p['without_account'] for p in plans)
        
        report.append("## 全体統計")
        report.append(f"- 対象自治体数: {total_municipalities}")
        report.append(f"- 総議員数: {total_members}")
        report.append(f"- Xアカウント未登録: {total_without} ({total_without/total_members*100:.1f}%)")
        report.append("")
        
        # 既知アカウントの分析
        report.append("## 既知アカウント分析")
        report.append(f"- 既知アカウント総数: {len(self.known_accounts)}")
        
        # 政党別統計
        party_counts = defaultdict(int)
        for info in self.known_accounts.values():
            party_counts[info['party']] += 1
        
        report.append("\n### 政党別既知アカウント数")
        for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"- {party}: {count}")
        
        # 優先対象自治体
        report.append("\n## 優先対象自治体（未登録率が高い）")
        priority_munis = sorted(plans, key=lambda p: p['without_account']/p['total_members'] if p['total_members'] > 0 else 0, reverse=True)[:10]
        
        report.append("| 自治体名 | 総数 | 未登録 | 未登録率 |")
        report.append("|----------|------|--------|----------|")
        
        for plan in priority_munis:
            muni_name = plan['municipality']['name']
            total = plan['total_members']
            without = plan['without_account']
            rate = without/total*100 if total > 0 else 0
            report.append(f"| {muni_name} | {total} | {without} | {rate:.1f}% |")
        
        return '\n'.join(report)

def discover_all_prefectures(base_path: Path):
    """全都道府県の発見計画を生成"""
    discoverer = ComprehensiveXDiscovery(base_path)
    
    all_plans = []
    csv_dir = base_path.parent / 'discovery_plans'
    csv_dir.mkdir(exist_ok=True)
    
    # 都道府県ごとに処理
    for pref_dir in sorted(base_path.glob("*")):
        if not pref_dir.is_dir() or not re.match(r'\d{2}_', pref_dir.name):
            continue
        
        print(f"\n{pref_dir.name} を処理中...")
        
        pref_plans = []
        for json_file in sorted(pref_dir.glob("議員リスト_*.json")):
            print(f"  - {json_file.stem}")
            plan = discoverer.generate_discovery_plan(json_file)
            
            if plan and plan['without_account'] > 0:
                pref_plans.append(plan)
                
                # CSV出力
                csv_path = csv_dir / f"{json_file.stem}_search_urls.csv"
                discoverer.export_search_urls(plan, csv_path)
        
        all_plans.extend(pref_plans)
    
    # 全体レポート生成
    report = discoverer.generate_comprehensive_report(all_plans)
    report_path = base_path.parent / 'discovery_plans' / f"comprehensive_report_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.write_text(report, encoding='utf-8')
    
    print(f"\n\n発見計画生成完了!")
    print(f"レポート: {report_path}")
    print(f"検索URL CSV: {csv_dir}")
    
    return all_plans

def analyze_single_municipality(json_path: Path):
    """単一自治体の詳細分析"""
    discoverer = ComprehensiveXDiscovery(json_path.parent.parent)
    plan = discoverer.generate_discovery_plan(json_path)
    
    if not plan:
        print("分析に失敗しました")
        return
    
    print(f"\n# {plan['municipality']['name']} 分析結果")
    print(f"総議員数: {plan['total_members']}")
    print(f"X未登録: {plan['without_account']}")
    
    # 優先度別に戦略を整理
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for member_strategy in plan['strategies']:
        member = member_strategy['member']
        for strategy in member_strategy['search_strategies']:
            if strategy['priority'] == 'high':
                high_priority.append((member, strategy))
            elif strategy['priority'] == 'medium':
                medium_priority.append((member, strategy))
            else:
                low_priority.append((member, strategy))
    
    print(f"\n## 検索戦略統計")
    print(f"- 高優先度: {len(high_priority)}")
    print(f"- 中優先度: {len(medium_priority)}")
    print(f"- 低優先度: {len(low_priority)}")
    
    # CSV出力
    output_path = json_path.parent / f"{json_path.stem}_discovery_urls.csv"
    discoverer.export_search_urls(plan, output_path)
    print(f"\n検索URL保存: {output_path}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  1. 全都道府県分析: python comprehensive_x_discovery.py --all")
        print("  2. 単一自治体分析: python comprehensive_x_discovery.py <JSONファイル>")
        print("")
        print("例:")
        print("  python comprehensive_x_discovery.py --all")
        print("  python comprehensive_x_discovery.py data/processed/13_東京都/議員リスト_132233_武蔵村山市.json")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        base_path = Path('data/processed')
        if not base_path.exists():
            print(f"エラー: {base_path} が見つかりません")
            sys.exit(1)
        discover_all_prefectures(base_path)
    else:
        json_path = Path(sys.argv[1])
        if not json_path.exists():
            print(f"エラー: {json_path} が見つかりません")
            sys.exit(1)
        analyze_single_municipality(json_path)

if __name__ == "__main__":
    main()