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

# 執行測試
if __name__ == "__main__":
    try:
        extract_vaultpatcher("test_vault.json")
        extract_snbt("test_quest.snbt")
        extract_standard_lang("test_lang.json")
    except FileNotFoundError as e:
        print(f"找不到檔案，請確認檔案名稱與路徑: {e}")