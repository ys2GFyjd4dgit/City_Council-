#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

def load_json_file(file_path):
    """JSONファイルを読み込む"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_municipality_info(json_path):
    """ファイル名から自治体情報を取得"""
    # ファイル名: 議員リスト_自治体コード_自治体名.json
    filename = json_path.stem
    parts = filename.split('_')
    
    if len(parts) >= 3:
        code = parts[1]
        municipality_name = parts[2]
        
        # 都道府県コードから都道府県名を取得
        prefecture_code = code[:2]
        prefecture_map = {
            "11": "埼玉県",
            "13": "東京都"
        }
        prefecture = prefecture_map.get(prefecture_code, f"{prefecture_code}_不明")
        
        return prefecture, municipality_name
    
    return "不明", "不明"

def main():
    # データディレクトリのパス
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    output_file = Path(__file__).parent.parent / "manual_search" / "x未登録議員一覧.txt"
    
    # 都道府県別・自治体別にデータを整理
    unregistered_by_location = defaultdict(lambda: defaultdict(list))
    total_members = 0
    total_unregistered = 0
    
    # すべてのJSONファイルを処理
    for json_file in sorted(data_dir.glob("**/議員リスト_*.json")):
        # CSVファイルをスキップ
        if json_file.suffix != '.json':
            continue
            
        data = load_json_file(json_file)
        
        # 自治体情報を取得
        prefecture, municipality_name = get_municipality_info(json_file)
        
        # 議員データを処理（dataはリスト形式）
        for member in data:
            total_members += 1
            
            # X_accountが未登録の議員を抽出
            x_account = member.get("X（旧Twitter）", "")
            if not x_account or x_account == "null":
                total_unregistered += 1
                
                # 議員情報を整理
                name = member.get("氏名", "")
                reading = member.get("よみ", "")
                party = member.get("所属", "無所属")
                
                member_info = f"{name}（{reading}） - {party}"
                unregistered_by_location[prefecture][municipality_name].append(member_info)
    
    # ファイルに出力
    with open(output_file, 'w', encoding='utf-8') as f:
        # ヘッダー情報
        f.write("X未登録議員一覧\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"総議員数: {total_members}名\n")
        f.write(f"X未登録議員数: {total_unregistered}名\n")
        if total_members > 0:
            f.write(f"未登録率: {total_unregistered/total_members*100:.1f}%\n")
        f.write("\n" + "=" * 80 + "\n\n")
        
        # 都道府県別に出力
        for prefecture in sorted(unregistered_by_location.keys()):
            f.write(f"【{prefecture}】\n")
            f.write("-" * 40 + "\n\n")
            
            # 自治体別に出力
            for city in sorted(unregistered_by_location[prefecture].keys()):
                members = unregistered_by_location[prefecture][city]
                f.write(f"■ {city} （{len(members)}名）\n")
                
                # 議員リストを出力
                for member in sorted(members):
                    f.write(f"  ・{member}\n")
                
                f.write("\n")
            
            f.write("\n")
    
    print(f"X未登録議員一覧を作成しました: {output_file}")
    print(f"総議員数: {total_members}名")
    print(f"X未登録議員数: {total_unregistered}名 ({total_unregistered/total_members*100:.1f}%)")

if __name__ == "__main__":
    main()