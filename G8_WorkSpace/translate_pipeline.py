import json
import re
import os
import opencc

class FormatMasker:
    def __init__(self):
        self.pattern = re.compile(r'(&[0-9a-fk-or]|§[0-9a-fk-or]|%\d\$s|%s|\n)')

    def mask(self, text):
        matches = []
        def repl(m):
            matches.append(m.group(0))
            return f"❰FMT_{len(matches)-1}❱"
        masked_text = self.pattern.sub(repl, text)
        return masked_text, matches

    def unmask(self, text, matches):
        for i, m in enumerate(matches):
            text = text.replace(f"❰FMT_{i}❱", m)
        return text

class MCTranslator:
    def __init__(self, dict_files=None):
        self.converter = opencc.OpenCC('s2twp.json')
        self.custom_terms = {}
        
        merged_terms = {}
        
        # 定義預設載入順序（優先級由低到高，後者覆蓋前者）
        default_files = [
            "mc_terms.json",      # 1. 原版官譯 (權重低)
            "create_terms.json",  # 2. 模組官譯 (權重中)
            "custom_terms.json"   # 3. 手動自訂 (權重最高)
        ]
        
        target_files = dict_files if dict_files else default_files

        # 依序載入並合併
        for file_path in target_files:
            if os.path.exists(file_path):
                print(f"正在載入術語字典: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    merged_terms.update(data) # 相同 Key 會被後載入的高權重項目覆蓋

        # 關鍵：合併後，全體重新依照字串長度「由長到短」重新排序
        sorted_keys = sorted(merged_terms.keys(), key=len, reverse=True)
        self.custom_terms = {k: merged_terms[k] for k in sorted_keys}
        
        print(f"術語庫合併完成，有效規則共 {len(self.custom_terms)} 筆")
        self.masker = FormatMasker()

def process_vaultpatcher_file(translator, input_path, output_path):
    print(f"開始處理 VaultPatcher: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("跳過：非 VaultPatcher 陣列格式")
        return

    processed_count = 0
    for block in data:
        if isinstance(block, dict) and "pairs" in block:
            for pair in block["pairs"]:
                if "value" in pair:
                    pair["value"] = translator.translate_text(pair["value"])
                    processed_count += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"完成！共轉換 {processed_count} 個字串，輸出至 {output_path}")

# 執行區塊
if __name__ == "__main__":
    # 初始化翻譯器，掛載自訂字典
    translator = MCTranslator()
    
    # 設定輸入與輸出路徑
    input_file = "amendments_dynamic.json"
    output_file = "amendments_dynamic_tw.json"
    
    if os.path.exists(input_file):
        process_vaultpatcher_file(translator, input_file, output_file)
    else:
        print(f"找不到測試檔案: {input_file}")