import os

def scan_assets_directory(assets_path):
    print(f"開始掃描資源包目錄: {assets_path}\n" + "="*50)
    
    special_mods = {}
    total_mods = 0
    
    if not os.path.exists(assets_path):
        print(f"找不到目錄: {assets_path}")
        return

    for mod_name in os.listdir(assets_path):
        mod_path = os.path.join(assets_path, mod_name)
        
        # 確保是資料夾
        if not os.path.isdir(mod_path):
            continue
            
        total_mods += 1
        contents = os.listdir(mod_path)
        
        # 判斷條件：如果目錄下的內容「等於且僅等於」 ['lang']，則為標準模組，跳過。
        if contents == ['lang']:
            continue
            
        # 只要走到這裡，就是包含特殊格式的模組
        special_mods[mod_name] = {
            'special_dirs': [d for d in contents if d != 'lang' and os.path.isdir(os.path.join(mod_path, d))],
            'extensions': set()
        }
        
        # 遍歷該模組底下的所有檔案，收集副檔名
        for root, _, files in os.walk(mod_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    special_mods[mod_name]['extensions'].add(ext)

    # 輸出報告
    print(f"掃描完成！共檢查了 {total_mods} 個模組資料夾。")
    print(f"發現 {len(special_mods)} 個包含非標準格式的模組：\n")

    with open("資料夾名單.txt", "w", encoding='utf-8') as f:
        f.write("")
    
    for mod, data in special_mods.items():
        dirs_str = ", ".join(data['special_dirs']) if data['special_dirs'] else "無"
        exts_str = ", ".join(data['extensions']) if data['extensions'] else "無"
        print(f"📦 【{mod}】")
        print(f"   ┣ 異常資料夾: {dirs_str}")
        print(f"   ┗ 包含副檔名: {exts_str}\n")
        with open("資料夾名單.txt", "a", encoding='utf-8') as f:
            f.write(f"📦 【{mod}】\n   ┣ 異常資料夾: {dirs_str}\n   ┗ 包含副檔名: {exts_str}\n\n")

if __name__ == "__main__":
    # 請替換為你實際的 assets 目錄路徑
    # 根據圖片，路徑應該類似 "./resourcepacks/BBSMC汉化包/assets"
    TARGET_ASSETS_DIR = r"C:\\Users\\etyet\\Downloads\\All of Create - Aeronautics-v2.5_task_faf972e0_汉化补丁\\resourcepacks\\BBSMC汉化包\\assets" 
    scan_assets_directory(TARGET_ASSETS_DIR)