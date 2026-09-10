import json
import re

def extract_vaultpatcher(file_path):
    print(f"--- 測試讀取格式 A: {file_path} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, item in enumerate(data.get("pairs", [])):
        if "value" in item:
            print(f"Index [{i}]: {item['value']}")
    print("\n")

def extract_snbt(file_path):
    print(f"--- 測試讀取格式 B: {file_path} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 quest_desc: [...] 區塊內的內容
    blocks = re.findall(r'quest_desc:\s*\[(.*?)\]', content, re.DOTALL)
    for block in blocks:
        # 提取雙引號內的字串
        strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', block)
        for s in strings:
            print(f"提取字串: {s}")
    print("\n")

def extract_standard_lang(file_path):
    print(f"--- 測試讀取格式 C: {file_path} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for key, value in data.items():
        if isinstance(value, str):
            print(f"Key [{key}]: {value}")
    print("\n")

def parse_vaultpatcher_dynamic(file_path):
    print(f"--- 處理 VaultPatcher 檔案: {file_path} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 防呆機制：確認根節點是否為列表 (如圖片所示)
    if not isinstance(data, list):
        print("錯誤：檔案根節點不是陣列 (List)。")
        return

    # 走訪陣列中的每一個區塊
    for block_idx, block in enumerate(data):
        # 如果區塊是字典，且包含 'pairs' 鍵
        if isinstance(block, dict) and "pairs" in block:
            print(f"找到注入區塊 (Index {block_idx})，Target Class: {block.get('target_class', 'Unknown')}")
            
            # 提取 pairs 陣列中的 value
            for pair_idx, pair in enumerate(block["pairs"]):
                if "value" in pair:
                    print(f"  - Key: {pair.get('key')}")
                    print(f"  - Value: {pair['value']}")
        
        # 略過包含 'name', 'desc' 的詮釋資料區塊
        elif isinstance(block, dict) and "name" in block and "desc" in block:
            print(f"略過詮釋資料區塊: {block.get('name')}")

# 執行測試
if __name__ == "__main__":
    try:
        extract_vaultpatcher("test_vault.json")
        extract_snbt("test_quest.snbt")
        extract_standard_lang("test_lang.json")
    except FileNotFoundError as e:
        print(f"找不到檔案，請確認檔案名稱與路徑: {e}")

    test_file = "amendments_dynamic.json" 
    try:
        parse_vaultpatcher_dynamic(test_file)
    except Exception as e:
        print(f"發生錯誤: {e}")