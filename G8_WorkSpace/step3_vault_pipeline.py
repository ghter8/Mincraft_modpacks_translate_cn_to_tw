import json
import re
import os

class FormatMasker:
    def __init__(self):
        # 擴充了正規表達式，現在也將 \n 視為需要保護的特殊符號
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

def process_vaultpatcher_file(input_path, output_path):
    print(f"開始處理: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("錯誤：檔案格式不符，預期為陣列 (List)。")
        return

    masker = FormatMasker()
    processed_count = 0

    # 走訪並直接在原資料結構上修改 (In-place modification)
    for block in data:
        if isinstance(block, dict) and "pairs" in block:
            for pair in block["pairs"]:
                if "value" in pair:
                    original_text = pair["value"]

                    # 1. 套用遮罩保護特殊符號與顏色碼
                    masked_text, matches = masker.mask(original_text)

                    # 2. 模擬翻譯 (先用簡單的字串替換測試，確認寫回邏輯正常)
                    translated_mock = masked_text.replace("模组", "模組").replace("文件", "檔案").replace("游戏", "遊戲")

                    # 3. 還原遮罩
                    final_text = masker.unmask(translated_mock, matches)

                    # 4. 覆寫回原本的字典中
                    pair["value"] = final_text
                    processed_count += 1

    # 輸出保留原本完整結構的 JSON，ensure_ascii=False 確保中文正常顯示
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"處理完成！共替換了 {processed_count} 個字串。")
    print(f"已輸出至: {output_path}")

if __name__ == "__main__":
    # 將這裡的 input_file 替換為你的實際測試檔案路徑
    input_file = "amendments_dynamic.json"
    output_file = "amendments_dynamic_tw.json" 
    
    try:
        process_vaultpatcher_file(input_file, output_file)
    except FileNotFoundError:
        print(f"找不到檔案: {input_file}")