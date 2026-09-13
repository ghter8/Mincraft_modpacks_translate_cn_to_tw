import json
import re

class PatchouliMasker:
    def __init__(self):
        # 保護 Patchouli 特有標記 $(...)
        self.macro_pattern = re.compile(r'\$\([^)]*\)')
        # 保護 Minecraft 標準顏色/換行符號
        self.mc_pattern = re.compile(r'(&[0-9a-fk-or]|§[0-9a-fk-or]|%\d\$s|%s|\n)')

    def mask(self, text):
        macros, mc_fmts = [], []
        
        # 1. 遮蔽 Patchouli 標記
        def repl_macro(m):
            macros.append(m.group(0))
            return f"❰MACRO_{len(macros)-1}❱"
        text_macro_masked = self.macro_pattern.sub(repl_macro, text)
        
        # 2. 遮蔽標準 MC 標記
        def repl_mc(m):
            mc_fmts.append(m.group(0))
            return f"❰FMT_{len(mc_fmts)-1}❱"
        text_fully_masked = self.mc_pattern.sub(repl_mc, text_macro_masked)
        
        return text_fully_masked, macros, mc_fmts

    def unmask(self, text, macros, mc_fmts):
        # 依照相反順序還原：先還原 MC 標記，再還原 Patchouli 標記
        for i, m in enumerate(mc_fmts):
            text = text.replace(f"❰FMT_{i}❱", m)
        for i, m in enumerate(macros):
            text = text.replace(f"❰MACRO_{i}❱", m)
        return text

class PatchouliProcessor:
    def __init__(self):
        self.masker = PatchouliMasker()
        # 精確鎖定的白名單
        self.whitelist = {"name", "description", "text", "title"}

    def mock_translate(self, text):
        """模擬 OpenCC 轉換，將簡體與特定詞彙轉為繁體"""
        return text.replace("魔灵罐", "魔靈罐").replace("收容罐", "收容罐").replace("自动化", "自動化").replace("神秘学", "神秘學").replace("碎矿者魔灵", "碎礦者魔靈").replace("清洁工", "清潔工")

    def process_json(self, data):
        """遞迴遍歷並處理白名單內的字串"""
        def traverse(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in self.whitelist and isinstance(v, str):
                        # 1. 雙重遮罩
                        masked_text, macros, mc_fmts = self.masker.mask(v)
                        
                        # 2. 執行翻譯
                        translated_text = self.mock_translate(masked_text)
                        
                        # 3. 還原遮罩
                        final_text = self.masker.unmask(translated_text, macros, mc_fmts)
                        
                        # 4. 寫回 JSON 節點
                        node[k] = final_text
                    elif isinstance(v, (dict, list)):
                        traverse(v)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
                    
        traverse(data)
        return data

# --- 測試區塊 ---
if __name__ == "__main__":
    with open(r"..\resourcepacks\BBSMC汉化包\assets\ars_nouveau\patchouli_books\worn_notebook\zh_cn\entries\spirit_jar.json", 'r', encoding='utf-8') as f:
        test_data = json.load(f)
        
        processor = PatchouliProcessor()
        processed_data = processor.process_json(test_data)
        
        print("【處理完成的 JSON 結構】")
        print(json.dumps(processed_data, ensure_ascii=False, indent=2))