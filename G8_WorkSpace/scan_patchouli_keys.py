import os
import json
import re

def scan_translatable_keys(target_dir):
    with open("scan_patchouli_keys_outputs.txt", 'w', encoding='utf-8') as out:
        out.write('')

    with open("scan_patchouli_keys_outputs.txt", 'a', encoding='utf-8') as out:
        print(f"🔍 開始掃描目錄，尋找包含中文的 JSON Keys: {target_dir}\n")
        out.write(f"🔍 開始掃描目錄，尋找包含中文的 JSON Keys: {target_dir}\n\n")
        
        zh_pattern = re.compile(r'[\u4e00-\u9fa5]')
        key_statistics = set()
        
        if not os.path.exists(target_dir):
            print("找不到目標目錄，請確認路徑。")
            out.write("找不到目標目錄，請確認路徑。\n")
            return

        # 遞迴檢查 JSON 節點
        def check_node(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, str) and zh_pattern.search(v):
                        key_statistics.add(k)
                    elif isinstance(v, (dict, list)):
                        check_node(v)
            elif isinstance(node, list):
                for item in node:
                    check_node(item)

        # 遍歷資料夾
        file_count = 0
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".json"):
                    file_count += 1
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            check_node(data)
                    except Exception as e:
                        print(f"讀取錯誤 {file}: {e}")
                        out.write(f"讀取錯誤 {file}: {e}\n")

        print(f"✅ 掃描完成！共檢查了 {file_count} 個 JSON 檔案。")
        out.write(f"✅ 掃描完成！共檢查了 {file_count} 個 JSON 檔案。\n")
        print(f"🎯 發現包含中文的 Keys 如下 (請將此名單提供給我做白名單)：")
        out.write(f"🎯 發現包含中文的 Keys 如下 (請將此名單提供給我做白名單)：\n")
        for key in sorted(list(key_statistics)):
            print(f"   - {key}")
            out.write(f"   - {key}\n")

if __name__ == "__main__":
    # 請將路徑指向 ars_nouveau 模組，或者整個包含 patchouli_books 的目錄
    TARGET_DIR = r"../resourcepacks/BBSMC汉化包/assets/enchanted/modopedia"
    scan_translatable_keys(TARGET_DIR)