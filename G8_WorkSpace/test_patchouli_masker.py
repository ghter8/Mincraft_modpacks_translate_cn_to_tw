import re

class PatchouliMasker:
    def __init__(self):
        # 匹配 Patchouli 的特有標記，例如 $(l:machines/mob_jar), $(thing), $(), $(br2)
        # 正規表達式解釋：匹配 $( 開頭，中間是非括號字元，接著是 ) 結尾
        self.macro_pattern = re.compile(r'\$\([^)]*\)')

    def mask(self, text):
        matches = []
        def repl(m):
            matches.append(m.group(0))
            return f"❰MACRO_{len(matches)-1}❱"
        
        masked_text = self.macro_pattern.sub(repl, text)
        return masked_text, matches

    def unmask(self, text, matches):
        for i, m in enumerate(matches):
            text = text.replace(f"❰MACRO_{i}❱", m)
        return text

# --- 測試區塊 ---
if __name__ == "__main__":
    with open(r"C:\Users\etyet\Downloads\All of Create - Aeronautics-v2.5_task_faf972e0_汉化补丁\resourcepacks\BBSMC汉化包\assets\ars_nouveau\patchouli_books\worn_notebook\zh_cn\entries\spirit_jar.json", 'r', encoding='utf-8') as f:
        test_text = f.read()

        masker = PatchouliMasker()
        
        print("【原始文本】\n", test_text, "\n" + "="*40)
        
        masked, tokens = masker.mask(test_text)
        print("【遮罩後文本】\n", masked, "\n" + "="*40)
        
        print("【受保護的標記集合】")
        for i, token in enumerate(tokens):
            print(f"❰MACRO_{i}❱ : {token}")