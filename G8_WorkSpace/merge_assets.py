import os
import shutil

def merge_extracted_assets(source_root, target_assets_dir):
    print(f"🚀 開始掃描並整合命名空間...\n目標資料夾: {target_assets_dir}\n" + "="*50)
    
    # 確保目標 assets 資料夾存在
    os.makedirs(target_assets_dir, exist_ok=True)
    
    merge_count = 0
    
    # 遍歷來源目錄
    for root, dirs, files in os.walk(source_root):
        # 嚴格條件：只鎖定名稱正好為 "assets" 的資料夾
        if os.path.basename(root) == 'assets':
            
            # assets 的直接下一個層級即為命名空間
            for namespace in dirs:
                source_namespace_dir = os.path.join(root, namespace)
                target_namespace_dir = os.path.join(target_assets_dir, namespace)
                
                print(f"📦 發現命名空間: '{namespace}'")
                print(f"   來源路徑: {source_namespace_dir}")
                
                try:
                    # 執行複製與合併。dirs_exist_ok=True 確保遇到同名命名空間時會合併內容而非報錯
                    shutil.copytree(source_namespace_dir, target_namespace_dir, dirs_exist_ok=True)
                    merge_count += 1
                    print(f"   ✅ 已成功合併至: {target_namespace_dir}\n")
                except Exception as e:
                    print(f"   ❌ 合併失敗: {e}\n")
                    
    print("="*50)
    print(f"🎉 整合完成！共提取並合併了 {merge_count} 個命名空間資料夾。")

if __name__ == "__main__":
    # 來源目錄：請將這裡指向你存放「解包並翻譯好的模組」的根目錄
    # 腳本會自動往下挖，尋找裡面所有的 assets 資料夾
    SOURCE_DIRECTORY = r"C:\Users\etyet\Downloads\All of Create - Aeronautics-v2.5_task_faf972e0_汉化补丁\G8_WorkSpace\NoZhTW_zh_tw"
    
    # 目標目錄：最終要匯整過去的總 assets 資料夾路徑
    TARGET_DIRECTORY = r"./assets"
    
    merge_extracted_assets(SOURCE_DIRECTORY, TARGET_DIRECTORY)