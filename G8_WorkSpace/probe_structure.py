import os
import json

def probe_folder_structure(target_dir):
    print(f"\n🔍 探測目標: {target_dir}\n" + "="*50)
    
    if not os.path.exists(target_dir):
        print(f"找不到目錄: {target_dir}")
        return

    for root, dirs, files in os.walk(target_dir):
        # 計算縮排層級
        level = root.replace(target_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}📂 {os.path.basename(root)}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            
            if ext == '.json':
                try:
                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        keys = list(data.keys())[:5] # 只抓取前 5 個 key 供分析
                        key_str = f"Keys: {keys}..." if isinstance(data, dict) else "陣列結構 (Array)"
                        print(f"{sub_indent}📄 {f}  -> [JSON 結構: {key_str}]")
                except Exception as e:
                    print(f"{sub_indent}📄 {f}  -> [JSON 解析失敗: {e}]")
            else:
                print(f"{sub_indent}📄 {f}")

if __name__ == "__main__":
    # 請將路徑替換為你本地端 ae2 或 advanced_ae 的 ae2guide 路徑
    # 建議先測試 advanced_ae 
    TARGET = r"C:\Users\etyet\Downloads\All of Create - Aeronautics-v2.5_task_faf972e0_汉化补丁\resourcepacks\BBSMC汉化包\assets\immersiveposts"
    probe_folder_structure(TARGET)