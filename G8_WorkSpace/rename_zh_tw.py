import os

def rename_zh_cn_to_zh_tw(target_dir):
    print(f"🚀 開始執行重新命名任務: {target_dir}\n" + "="*50)
    
    if not os.path.exists(target_dir):
        print(f"❌ 找不到目標目錄: {target_dir}")
        return

    rename_count = 0
    
    # 關鍵：topdown=False 會先遍歷最深層的子目錄，再往上回到父目錄
    # 這樣可以確保子檔案/資料夾改名時，父目錄的路徑還是有效的
    for root, dirs, files in os.walk(target_dir, topdown=False):
        
        # 1. 重新命名檔案 (例如 zh_cn.json -> zh_tw.json)
        for file in files:
            if 'zh_cn' in file:
                old_file_path = os.path.join(root, file)
                new_file_name = file.replace('zh_cn', 'zh_tw')
                new_file_path = os.path.join(root, new_file_name)
                
                try:
                    os.rename(old_file_path, new_file_path)
                    print(f"📄 [檔案改名] {file}  ->  {new_file_name}")
                    rename_count += 1
                except Exception as e:
                    print(f"❌ [錯誤] 無法重新命名檔案 {old_file_path}: {e}")

        # 2. 重新命名資料夾 (例如 _zh_cn -> _zh_tw)
        for d in dirs:
            if 'zh_cn' in d:
                old_dir_path = os.path.join(root, d)
                new_dir_name = d.replace('zh_cn', 'zh_tw')
                new_dir_path = os.path.join(root, new_dir_name)
                
                try:
                    os.rename(old_dir_path, new_dir_path)
                    print(f"📁 [目錄改名] {d}  ->  {new_dir_name}")
                    rename_count += 1
                except Exception as e:
                    print(f"❌ [錯誤] 無法重新命名目錄 {old_dir_path}: {e}")

    print("="*50)
    print(f"✅ 重新命名完成！共成功修改了 {rename_count} 個檔案與目錄。")

if __name__ == "__main__":
    # ⚠️ 建議設定為你透過整合腳本「輸出」的那個 translated 資料夾
    # 避免不小心改到原始備份的檔案
    TARGET_DIRECTORY = r"C:\Users\etyet\Downloads\All of Create - Aeronautics-v2.5_task_faf972e0_汉化补丁\G8_WorkSpace\NoZhTW_zh_tw" 
    
    rename_zh_cn_to_zh_tw(TARGET_DIRECTORY)