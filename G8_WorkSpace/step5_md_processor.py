import re

class MarkdownProcessor:
    def __init__(self, translator):
        self.translator = translator # 這裡會傳入我們已經寫好的 MCTranslator 實例
        
        # 匹配整個 YAML Frontmatter 區塊 (包含開頭和結尾的 ---)
        self.yaml_block_pattern = re.compile(r'^---\n(.*?)\n---$', re.MULTILINE | re.DOTALL)
        
        # 匹配 YAML 內的 title 欄位 (支援抓取並替換其後面的中文)
        self.yaml_title_pattern = re.compile(r'^( *title: *)(.+)$', re.MULTILINE)
        
        # 匹配所有 XML/React 標籤 (例如 <Row>, <ItemImage ... />)
        self.xml_pattern = re.compile(r'<[^>]+>')
        
        # 匹配 Markdown 連結，例如 [分子装配室](molecular_assembler.md)
        # Group 1: "[", Group 2: "顯示文字", Group 3: "](連結)"
        self.md_link_pattern = re.compile(r'(\[)([^\]]+)(\]\([^)]+\))')

    def process_yaml(self, match):
        """專門處理 YAML 區塊，只翻譯 title 欄位，其餘原封不動"""
        yaml_content = match.group(1)
        
        def replace_title(m):
            prefix = m.group(1)
            raw_title = m.group(2)
            # 使用掛載的翻譯器翻譯標題
            translated_title = self.translator.translate_text(raw_title)
            return f"{prefix}{translated_title}"
            
        new_yaml = self.yaml_title_pattern.sub(replace_title, yaml_content)
        return f"---\n{new_yaml}\n---"

    def process_content(self, text):
        """處理 Markdown 內文"""
        matches = []
        
        # 1. 遮蔽所有 XML/React 標籤
        def mask_xml(m):
            matches.append(m.group(0))
            return f"❰XML_{len(matches)-1}❱"
        text_xml_masked = self.xml_pattern.sub(mask_xml, text)
        
        # 2. 遮蔽 Markdown 連結的後半段 URL，但暴露前半段的顯示文字
        def mask_link(m):
            display_text = m.group(2)
            url_part = m.group(3)
            matches.append(url_part)
            # 將顯示文字保留在外，供後續翻譯
            return f"[{display_text}❰LINK_{len(matches)-1}❱"
        text_fully_masked = self.md_link_pattern.sub(mask_link, text_xml_masked)
        
        # 3. 將遮蔽好的整份文本丟給主翻譯器 (包含 OpenCC 轉換)
        translated_text = self.translator.translate_text(text_fully_masked)
        
        # 4. 還原遮蔽的標籤與連結
        for i, m in enumerate(matches):
            if m.startswith(']('):
                translated_text = translated_text.replace(f"❰LINK_{i}❱", m)
            else:
                translated_text = translated_text.replace(f"❰XML_{i}❱", m)
                
        return translated_text

    def process_file(self, content):
        """處理單一 Markdown 檔案的完整流程"""
        # 第一步：分離並翻譯 YAML 區塊 (如果存在)
        if content.startswith('---'):
            # 找到第一個和第二個 --- 之間的位置
            parts = self.yaml_block_pattern.split(content, maxsplit=1)
            if len(parts) >= 3:
                # parts[0] 是空字串 (因為開頭匹配)
                # parts[1] 是 yaml 內容
                # parts[2] 是剩下的 markdown 內文
                
                # 手動重建一個假的 match 物件來重用 process_yaml
                class MockMatch:
                    def group(self, n): return parts[1]
                
                processed_yaml = self.process_yaml(MockMatch())
                processed_content = self.process_content(parts[2])
                return f"{processed_yaml}{processed_content}"
        
        # 如果沒有 YAML，就直接處理全部內文
        return self.process_content(content)

# --- 模擬器測試 ---
if __name__ == "__main__":
    # 建立一個簡單的 Mock 翻譯器來模擬主程式
    class MockTranslator:
        def translate_text(self, text):
            # 簡單模擬簡轉繁與術語替換
            return text.replace("分子装配室", "分子裝配室").replace("合成", "合成").replace("升级", "升級").replace("系统", "系統")
            
    translator = MockTranslator()
    processor = MarkdownProcessor(translator)
    
    # 擷取 molecular_assembler.md 的一個片段進行測試
    test_md = """---
navigation:
  parent: items-blocks-machines/items-blocks-machines-index.md
  title: 分子装配室
  icon: molecular_assembler
---

# 分子装配室

<BlockImage id="molecular_assembler" scale="8" />

下述装配室装有一个“1x 橡木原木 = 4x 橡木木板”的样板。

## 升级

分子装配室支持以下[升级](upgrade_cards.md)：

*   <ItemLink id="speed_card" />"""

    print("【轉換結果】\n")
    print(processor.process_file(test_md))