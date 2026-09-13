import json
import re
import os
import opencc

# ==========================================
# 核心遮罩器與翻譯引擎
# ==========================================
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

        terms = "./terms/"
        
        default_files = [
            terms + "mc_terms.json",
            terms + "create_terms.json",
            terms + "create_aquatic_ambitions_terms.json",
            terms + "create_connected_terms.json",
            terms + "createaddition_terms.json",
            terms + "createdieselgenerators_terms.json",
            terms + "custom_terms.json"
        ]
        target_files = dict_files if dict_files else default_files

        for file_path in target_files:
            if os.path.exists(file_path):
                print(f"📦 載入術語字典: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    merged_terms.update(json.load(f))

        sorted_keys = sorted(merged_terms.keys(), key=len, reverse=True)
        self.custom_terms = {k: merged_terms[k] for k in sorted_keys}
        
        self.masker = FormatMasker()
        self.zh_pattern = re.compile(r'[\u4e00-\u9fa5]')

    def translate_text(self, text):
        if not text or not isinstance(text, str) or not self.zh_pattern.search(text):
            return text

        masked_text, matches = self.masker.mask(text)

        protected_terms = []
        for cn_term, tw_term in self.custom_terms.items():
            if cn_term in masked_text:
                protected_token = f"❰TERM_{len(protected_terms)}❱"
                protected_terms.append(tw_term)
                masked_text = masked_text.replace(cn_term, protected_token)

        translated = self.converter.convert(masked_text)

        for i, term in enumerate(protected_terms):
            translated = translated.replace(f"❰TERM_{i}❱", term)
        final_text = self.masker.unmask(translated, matches)
        
        return final_text

# ==========================================
# 特化格式處理器
# ==========================================
class VaultPatcherProcessor:
    def __init__(self, translator):
        self.translator = translator

    def is_target(self, data):
        """特徵探測：陣列結構，且內部字典含有 'pairs'"""
        if not isinstance(data, list):
            return False
        for item in data:
            if isinstance(item, dict) and "pairs" in item:
                return True
        return False

    def process(self, data):
        count = 0
        for block in data:
            if isinstance(block, dict) and "pairs" in block:
                for pair in block["pairs"]:
                    if "value" in pair and isinstance(pair["value"], str):
                        original = pair["value"]
                        pair["value"] = self.translator.translate_text(pair["value"])
                        if original != pair["value"]: 
                            count += 1
        return count

class PatchouliProcessor:
    def __init__(self, translator):
        self.translator = translator
        self.macro_pattern = re.compile(r'\$\([^)]*\)')
        self.whitelist = {"name", "description", "text", "title", "flavour_text", "subtitle"}

    def process(self, data):
        count = 0
        def traverse(node):
            nonlocal count
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in self.whitelist and isinstance(v, str) and self.translator.zh_pattern.search(v):
                        macros = []
                        def repl_macro(m):
                            macros.append(m.group(0))
                            return f"❰MACRO_{len(macros)-1}❱"
                        macro_masked = self.macro_pattern.sub(repl_macro, v)
                        translated = self.translator.translate_text(macro_masked)
                        
                        for i, m in enumerate(macros):
                            translated = translated.replace(f"❰MACRO_{i}❱", m)
                            
                        if v != translated:
                            node[k] = translated
                            count += 1
                    elif isinstance(v, (dict, list)):
                        traverse(v)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        traverse(data)
        return count

class ModopediaProcessor:
    def __init__(self, translator):
        self.translator = translator
        # 根據探測結果，精確鎖定的白名單
        self.whitelist = {"header", "landing_text", "text", "title"}

    def process(self, data):
        count = 0
        def traverse(node):
            nonlocal count
            if isinstance(node, dict):
                for k, v in node.items():
                    # 條件：Key 在白名單內、是字串，且包含中文字元
                    if k in self.whitelist and isinstance(v, str) and self.translator.zh_pattern.search(v):
                        original = v
                        # 直接交給主引擎翻譯（已包含 MC 樣式與換行保護）
                        translated = self.translator.translate_text(v)
                        
                        if original != translated:
                            node[k] = translated
                            count += 1
                    elif isinstance(v, (dict, list)):
                        traverse(v)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
                    
        traverse(data)
        return count

class MarkdownProcessor:
    def __init__(self, translator):
        self.translator = translator
        self.yaml_block_pattern = re.compile(r'^---\n(.*?)\n---$', re.MULTILINE | re.DOTALL)
        self.yaml_title_pattern = re.compile(r'^( *title: *)(.+)$', re.MULTILINE)
        self.xml_pattern = re.compile(r'<[^>]+>')
        self.md_link_pattern = re.compile(r'(\[)([^\]]+)(\]\([^)]+\))')

    def process_content(self, text):
        matches = []
        def mask_xml(m):
            matches.append(m.group(0))
            return f"❰XML_{len(matches)-1}❱"
        def mask_link(m):
            matches.append(m.group(3))
            return f"[{m.group(2)}❰LINK_{len(matches)-1}❱"
            
        masked = self.md_link_pattern.sub(mask_link, self.xml_pattern.sub(mask_xml, text))
        translated = self.translator.translate_text(masked)
        
        for i, m in enumerate(matches):
            if m.startswith(']('):
                translated = translated.replace(f"❰LINK_{i}❱", m)
            else:
                translated = translated.replace(f"❰XML_{i}❱", m)
        return translated

    def process_file(self, content):
        if content.startswith('---'):
            parts = self.yaml_block_pattern.split(content, maxsplit=1)
            if len(parts) >= 3:
                yaml_content = parts[1]
                def replace_title(m):
                    return f"{m.group(1)}{self.translator.translate_text(m.group(2))}"
                new_yaml = f"---\n{self.yaml_title_pattern.sub(replace_title, yaml_content)}\n---"
                return f"{new_yaml}{self.process_content(parts[2])}"
        return self.process_content(content)

class ImmersiveManualProcessor:
    def __init__(self, translator):
        self.translator = translator
        self.link_pattern = re.compile(r'(<link;[^;]+;)(.*?)(;[^>]*>)')
        self.tag_pattern = re.compile(r'<[^>]+>')

    def process_content(self, text):
        link_matches = []
        def mask_link(m):
            link_matches.append((m.group(1), m.group(3)))
            idx = len(link_matches) - 1
            return f"❰IE_PRE_{idx}❱{m.group(2)}❰IE_SUF_{idx}❱"
            
        text_link_masked = self.link_pattern.sub(mask_link, text)

        tag_matches = []
        def mask_tag(m):
            tag_matches.append(m.group(0))
            return f"❰IE_TAG_{len(tag_matches)-1}❱"
            
        text_fully_masked = self.tag_pattern.sub(mask_tag, text_link_masked)

        # 交給主引擎翻譯 (處理 § 顏色代碼與簡繁轉換)
        translated = self.translator.translate_text(text_fully_masked)

        # 還原
        for i, m in enumerate(tag_matches):
            translated = translated.replace(f"❰IE_TAG_{i}❱", m)
        for i, (pre, suf) in enumerate(link_matches):
            translated = translated.replace(f"❰IE_PRE_{i}❱", pre)
            translated = translated.replace(f"❰IE_SUF_{i}❱", suf)
            
        return translated

# ==========================================
# 檔案路由器與遍歷控制器 (無損輸出模式)
# ==========================================
def run_pipeline(target_dir, output_dir):
    translator = MCTranslator()
    patchouli_processor = PatchouliProcessor(translator)
    modopedai_processor = ModopediaProcessor(translator)
    md_processor = MarkdownProcessor(translator)
    vault_processor = VaultPatcherProcessor(translator)
    ie_manual_processor = ImmersiveManualProcessor(translator)

    print(f"\n🚀 開始掃描專案: {target_dir}")
    print(f"📁 輸出目錄設定為: {output_dir}\n")
    
    unhandled_files = []

    for root, _, files in os.walk(target_dir):
        path_parts = os.path.normpath(root).split(os.sep)
        
        # 建立對應的輸出子目錄結構
        rel_path = os.path.relpath(root, target_dir)
        current_out_dir = os.path.join(output_dir, rel_path)
        
        for file in files:
            file_path = os.path.join(root, file)
            out_file_path = os.path.join(current_out_dir, file)
            ext = os.path.splitext(file)[1].lower()

            try:
                # -------------------------
                # JSON 路由分發
                # -------------------------
                if ext == ".json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    count = 0
                    
                    # 判斷 1: VaultPatcher (最高優先級，透過結構特徵判斷)
                    if vault_processor.is_target(data):
                        count = vault_processor.process(data)
                        
                    # 判斷 2: 標準 Lang 檔案 (限定路徑包含 lang)
                    elif "lang" in path_parts:
                        if isinstance(data, dict):
                            for k, v in data.items():
                                if isinstance(v, str) and translator.zh_pattern.search(v):
                                    original = v
                                    data[k] = translator.translate_text(v)
                                    if original != data[k]: count += 1
                        
                    # 判斷 3: Patchouli 說明書
                    elif "patchouli_books" in path_parts:
                        count = patchouli_processor.process(data)

                    elif "modopedia" in path_parts:
                        count = modopedai_processor.process(data)
                                        
                    # 未定義的 JSON 格式
                    else:
                        unhandled_files.append(file_path)
                        continue # 直接跳過，不寫入輸出目錄

                    # 若有修改，確保輸出資料夾存在並寫入
                    if count > 0:
                        os.makedirs(current_out_dir, exist_ok=True)
                        with open(out_file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"✅ [JSON] 替換 {count} 處 -> {rel_path}\\{file}")

                # -------------------------
                # Markdown 路由
                # -------------------------
                elif ext == ".md":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = md_processor.process_file(content)
                    if new_content != content:
                        os.makedirs(current_out_dir, exist_ok=True)
                        with open(out_file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"✅ [ Markdown ] 處理完成 -> {rel_path}\\{file}")

                # -------------------------
                # SNBT 路由
                # -------------------------
                elif ext == ".snbt":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    def repl_snbt(match):
                        return f'"{translator.translate_text(match.group(1))}"'
                    new_content = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', repl_snbt, content)
                    if new_content != content:
                        os.makedirs(current_out_dir, exist_ok=True)
                        with open(out_file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"✅ [ SNBT ] 處理完成 -> {rel_path}\\{file}")

                # -------------------------
                # TXT 路由
                # -------------------------
                elif ext == ".txt":
                    if "manual" in path_parts:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        new_content = ie_manual_processor.process_content(content)
                        
                        if new_content != content:
                            os.makedirs(current_out_dir, exist_ok=True)
                            with open(out_file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"✅ [ TXT Manual ] 處理完成 -> {rel_path}\\{file}")

            except Exception as e:
                print(f"❌ [錯誤] 無法處理 {file_path}: {e}")

    # 輸出未處理的檔案報告
    if unhandled_files:
        print("\n" + "="*50)
        print(f"⚠️ 發現 {len(unhandled_files)} 個未定義的 JSON 檔案，已跳過處理並保留於清單中：")
        for f in unhandled_files:
            print(f"   - {f}")
        print("="*50)
        print("💡 請將上方未定義的檔案清單（或其中代表性的幾個）貼給我，我們來進行下一階段的分析。")

if __name__ == "__main__":
    # 輸入目錄：原始的 resourcepacks/BBSMC汉化包/assets
    TARGET_DIR = r"C:\Users\etyet\Downloads\All of Create - Aeronautics-v2.5_task_faf972e0_汉化补丁\G8_WorkSpace\NoZhTW"
    
    # 輸出目錄：會在當前腳本目錄下建立一個 _translated 結尾的新資料夾
    OUTPUT_DIR = TARGET_DIR + "_zh_tw"
    
    run_pipeline(TARGET_DIR, OUTPUT_DIR)