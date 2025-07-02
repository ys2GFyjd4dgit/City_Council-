#!/usr/bin/env python3
"""
自動Xアカウント発見システム
Selenium WebDriverを使用して議員のXアカウントを自動的に発見・検証する

機能:
1. 拡張検索戦略（地域イベント、議会活動、メディア関連）
2. Selenium WebDriverによる自動検索
3. プロフィール自動照合と信頼度スコア算出
4. バッチ処理による効率的な発見
"""

import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

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

class AutomatedXAccountFinder:
    """自動Xアカウント発見クラス"""
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        self.headless = headless
        self.delay = delay
        self.driver = None
        self.confidence_threshold = 0.6
        
    def setup_driver(self):
        """WebDriverをセットアップ"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def search_x_accounts(self, query: str) -> List[Dict]:
        """X検索を実行してアカウント候補を取得"""
        if not self.driver:
            self.setup_driver()
        
        candidates = []
        
        try:
            search_url = f"https://x.com/search?q={query}&f=user"
            self.driver.get(search_url)
            
            time.sleep(self.delay)
            
            try:
                account_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserCell"]')
                
                for element in account_elements[:5]:  # 上位5件のみ
                    try:
                        username_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="UserName"] a')
                        username = username_elem.get_attribute('href').split('/')[-1]
                        
                        display_name_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="UserName"] span')
                        display_name = display_name_elem.text
                        
                        try:
                            bio_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="UserDescription"]')
                            bio = bio_elem.text
                        except NoSuchElementException:
                            bio = ""
                        
                        candidates.append({
                            'username': username,
                            'display_name': display_name,
                            'bio': bio,
                            'url': f'https://x.com/{username}'
                        })
                        
                    except Exception as e:
                        continue
                        
            except TimeoutException:
                pass
                
        except Exception as e:
            print(f"検索エラー: {e}")
        
        return candidates
    
    def find_account_for_member(self, member: Dict, municipality_info: Dict) -> DiscoveryResult:
        """議員のアカウントを発見"""
        start_time = time.time()
        
        queries = EnhancedSearchPatterns.generate_enhanced_queries(member, municipality_info)
        
        all_candidates = []
        queries_used = []
        
        for query in queries[:10]:  # 最初の10クエリのみ使用
            candidates = self.search_x_accounts(query)
            all_candidates.extend(candidates)
            queries_used.append(query)
            
            time.sleep(self.delay)
        
        unique_candidates = {}
        for candidate in all_candidates:
            username = candidate['username']
            if username not in unique_candidates:
                unique_candidates[username] = candidate
        
        scored_candidates = []
        for candidate in unique_candidates.values():
            score, reasons = ProfileVerifier.calculate_confidence_score(
                candidate, member, municipality_info
            )
            
            if score >= self.confidence_threshold:
                scored_candidates.append(SearchCandidate(
                    username=candidate['username'],
                    display_name=candidate['display_name'],
                    bio=candidate['bio'],
                    url=candidate['url'],
                    confidence_score=score,
                    match_reasons=reasons
                ))
        
        best_candidate = None
        if scored_candidates:
            best_candidate = max(scored_candidates, key=lambda x: x.confidence_score)
        
        processing_time = time.time() - start_time
        
        return DiscoveryResult(
            member_name=member['氏名'],
            found_account=best_candidate,
            search_queries_used=queries_used,
            total_candidates=len(unique_candidates),
            processing_time=processing_time
        )
    
    def discover_accounts_for_municipality(self, json_path: Path) -> List[DiscoveryResult]:
        """自治体の全未登録議員のアカウントを発見"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 自治体情報を解析
        filename = json_path.stem
        match = re.search(r'議員リスト_(\d+)_(.+)', filename)
        if not match:
            return []
        
        muni_name = match.group(2)
        muni_type = '市' if muni_name.endswith('市') else '町' if muni_name.endswith('町') else '村'
        
        municipality_info = {
            'name': muni_name,
            'type': muni_type,
            'code': match.group(1)
        }
        
        without_account = [m for m in data if not m.get('X（旧Twitter）')]
        
        results = []
        
        print(f"\n{muni_name} の自動発見を開始...")
        print(f"対象議員数: {len(without_account)}")
        
        for i, member in enumerate(without_account, 1):
            print(f"[{i}/{len(without_account)}] {member['氏名']} を検索中...")
            
            result = self.find_account_for_member(member, municipality_info)
            results.append(result)
            
            if result.found_account:
                print(f"  ✅ 発見: @{result.found_account.username} (信頼度: {result.found_account.confidence_score:.2f})")
            else:
                print(f"  ❌ 未発見")
        
        return results
    
    def close(self):
        """WebDriverを終了"""
        if self.driver:
            self.driver.quit()

def save_discovery_results(results: List[DiscoveryResult], output_path: Path):
    """発見結果をJSONファイルに保存"""
    output_data = []
    
    for result in results:
        result_data = {
            'member_name': result.member_name,
            'found_account': None,
            'search_queries_used': result.search_queries_used,
            'total_candidates': result.total_candidates,
            'processing_time': result.processing_time
        }
        
        if result.found_account:
            result_data['found_account'] = {
                'username': result.found_account.username,
                'display_name': result.found_account.display_name,
                'bio': result.found_account.bio,
                'url': result.found_account.url,
                'confidence_score': result.found_account.confidence_score,
                'match_reasons': result.found_account.match_reasons
            }
        
        output_data.append(result_data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

def generate_discovery_report(results: List[DiscoveryResult]) -> str:
    """発見レポートを生成"""
    total_members = len(results)
    found_accounts = [r for r in results if r.found_account]
    found_count = len(found_accounts)
    
    report = []
    report.append("# 自動Xアカウント発見レポート")
    report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("## 発見結果サマリー")
    report.append(f"- 対象議員数: {total_members}")
    report.append(f"- 発見アカウント数: {found_count}")
    report.append(f"- 発見率: {found_count/total_members*100:.1f}%")
    report.append("")
    
    if found_accounts:
        report.append("## 発見されたアカウント")
        for result in found_accounts:
            account = result.found_account
            report.append(f"### {result.member_name}")
            report.append(f"- **アカウント**: [@{account.username}]({account.url})")
            report.append(f"- **表示名**: {account.display_name}")
            report.append(f"- **信頼度スコア**: {account.confidence_score:.2f}")
            report.append(f"- **マッチ理由**: {', '.join(account.match_reasons)}")
            if account.bio:
                report.append(f"- **プロフィール**: {account.bio}")
            report.append("")
    
    if results:
        avg_processing_time = sum(r.processing_time for r in results) / len(results)
        avg_candidates = sum(r.total_candidates for r in results) / len(results)
        
        report.append("## 処理統計")
        report.append(f"- 平均処理時間: {avg_processing_time:.2f}秒")
        report.append(f"- 平均候補数: {avg_candidates:.1f}")
        report.append("")
    
    return '\n'.join(report)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python automated_x_discovery.py <議員リストJSONファイル>")
        print("")
        print("例:")
        print("  python automated_x_discovery.py data/processed/13_東京都/議員リスト_132233_武蔵村山市.json")
        sys.exit(1)
    
    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"エラー: ファイルが見つかりません - {json_path}")
        sys.exit(1)
    
    output_dir = Path('data/automated_discovery')
    output_dir.mkdir(exist_ok=True)
    
    finder = AutomatedXAccountFinder(headless=True, delay=3.0)
    
    try:
        results = finder.discover_accounts_for_municipality(json_path)
        
        municipality_name = json_path.stem.split('_')[-1]
        results_path = output_dir / f"{municipality_name}_discovery_results.json"
        save_discovery_results(results, results_path)
        
        report = generate_discovery_report(results)
        report_path = output_dir / f"{municipality_name}_discovery_report.md"
        report_path.write_text(report, encoding='utf-8')
        
        print(f"\n✅ 発見処理完了!")
        print(f"結果ファイル: {results_path}")
        print(f"レポート: {report_path}")
        
        found_count = len([r for r in results if r.found_account])
        print(f"\n📊 発見サマリー:")
        print(f"対象議員数: {len(results)}")
        print(f"発見アカウント数: {found_count}")
        print(f"発見率: {found_count/len(results)*100:.1f}%")
        
    finally:
        finder.close()

if __name__ == "__main__":
    main()
