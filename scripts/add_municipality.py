#!/usr/bin/env python3
"""
新しい自治体を追加するための対話型スクリプト
"""

import os
import json
import subprocess
from datetime import datetime

def get_municipality_info():
    """自治体情報を対話的に取得"""
    print("=== 新規自治体追加ウィザード ===\n")
    
    prefecture = input("都道府県名（例: 埼玉県）: ")
    municipality = input("市町村名（例: 所沢市）: ")
    code = input("自治体コード（6桁）: ")
    url = input("議員名簿のURL: ")
    
    return {
        "prefecture": prefecture,
        "municipality": municipality,
        "code": code,
        "url": url,
        "date": datetime.now().strftime("%Y%m%d")
    }

def create_directories(info):
    """必要なディレクトリを作成"""
    raw_dir = f"data/raw/{info['municipality']}/{info['date']}"
    os.makedirs(raw_dir, exist_ok=True)
    print(f"✅ ディレクトリ作成: {raw_dir}")
    return raw_dir

def download_html(info, raw_dir):
    """HTMLをダウンロード"""
    output_path = os.path.join(raw_dir, "source.html")
    
    print(f"\nダウンロード中: {info['url']}")
    result = subprocess.run(
        ["curl", "-s", info['url'], "-o", output_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ ダウンロード完了: {output_path}")
        return output_path
    else:
        print(f"❌ ダウンロード失敗: {result.stderr}")
        return None

def create_json_template(info):
    """JSONテンプレートを作成"""
    json_path = f"data/processed/議員リスト_{info['code']}_{info['municipality']}.json"
    
    template = [
        {
            "氏名": "山田　太郎",
            "登録名": "山田　太郎",
            "よみ": "やまだ　たろう",
            "X（旧Twitter）": None,
            "所属": "○○党"
        }
    ]
    
    print(f"\nJSONテンプレート作成: {json_path}")
    response = input("テンプレートを作成しますか？ (y/n): ")
    
    if response.lower() == 'y':
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"✅ テンプレート作成: {json_path}")
        return json_path
    
    return None

def update_readme_template(info):
    """README更新用のテンプレートを表示"""
    print("\n=== README.md 更新用テンプレート ===")
    print(f"| {info['municipality']} | {info['code']} | 未収集 | - | - | - | - |")
    print("\n後で以下の情報で更新してください:")
    print(f"| {info['municipality']} | {info['code']} | 校正中 | XX | X | {datetime.now().strftime('%Y-%m-%d')} | [議員リスト](data/processed/議員リスト_{info['code']}_{info['municipality']}.json) |")

def main():
    """メイン処理"""
    info = get_municipality_info()
    
    # 確認
    print(f"\n以下の内容で作成します:")
    print(f"- 都道府県: {info['prefecture']}")
    print(f"- 市町村: {info['municipality']}")
    print(f"- コード: {info['code']}")
    print(f"- URL: {info['url']}")
    
    response = input("\n続行しますか？ (y/n): ")
    if response.lower() != 'y':
        print("キャンセルしました")
        return
    
    # ディレクトリ作成
    raw_dir = create_directories(info)
    
    # HTMLダウンロード
    html_path = download_html(info, raw_dir)
    
    # JSONテンプレート作成
    json_path = create_json_template(info)
    
    # README更新用テンプレート表示
    update_readme_template(info)
    
    print("\n=== 次のステップ ===")
    print("1. HTMLファイルから議員情報を抽出")
    print("2. JSONファイルを編集")
    print("3. Xアカウントを検索")
    print("4. README.mdを更新")
    print("5. プルリクエストを作成")

if __name__ == "__main__":
    main()