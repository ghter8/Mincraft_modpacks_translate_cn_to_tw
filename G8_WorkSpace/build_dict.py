import json

def build_mc_dict(cn_path, tw_path, output_path):
    print("正在讀取官方語言檔...")
    with open(cn_path, 'r', encoding='utf-8') as f:
        cn_data = json.load(f)
    with open(tw_path, 'r', encoding='utf-8') as f:
        tw_data = json.load(f)

    raw_dict = {}
    
    # 進行交集比對
    for key, cn_text in cn_data.items():
        tw_text = tw_data.get(key)
        # 確保兩邊都有該鍵，且文字不同、不為空
        if tw_text and cn_text != tw_text and len(cn_text.strip()) > 0:
            raw_dict[cn_text] = tw_text

    # 關鍵：依照簡體中文字串長度「由長到短」排序
    sorted_keys = sorted(raw_dict.keys(), key=len, reverse=True)
    sorted_dict = {k: raw_dict[k] for k in sorted_keys}

    # 輸出為我們的管線字典
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_dict, f, ensure_ascii=False, indent=2)

    print(f"成功萃取 {len(sorted_dict)} 筆官方譯名對照！")
    print(f"已儲存至: {output_path}")
    print("前 3 筆最長的對照範例：")
    for k in sorted_keys[:3]:
        print(f"  {k} -> {sorted_dict[k]}")

if __name__ == "__main__":
    # 請確保檔名與你實際獲取的官方檔名一致
    build_mc_dict("zh_cn.json", "zh_tw.json", "mc_terms.json")