import re

class ImmersiveManualMasker:
    def __init__(self):
        # 1. 精確匹配 IE 手冊的連結格式 <link;target;顯示文字;anchor>
        # Group 1: <link;...; (前綴)
        # Group 2: 顯示文字 (需要暴露出來翻譯的部分)
        # Group 3: ;...> (後綴)
        self.link_pattern = re.compile(r'(<link;[^;]+;)(.*?)(;[^>]*>)')
        
        # 2. 匹配其餘所有常規的 <...> 標記
        self.tag_pattern = re.compile(r'<[^>]+>')

    def mask(self, text):
        link_matches = []
        def mask_link(m):
            link_matches.append((m.group(1), m.group(3)))
            idx = len(link_matches) - 1
            # 只遮蔽前後，把 m.group(2) 夾在中間暴露出來
            return f"❰IE_PRE_{idx}❱{m.group(2)}❰IE_SUF_{idx}❱"
            
        text_link_masked = self.link_pattern.sub(mask_link, text)

        tag_matches = []
        def mask_tag(m):
            tag_matches.append(m.group(0))
            return f"❰IE_TAG_{len(tag_matches)-1}❱"
            
        text_fully_masked = self.tag_pattern.sub(mask_tag, text_link_masked)
        
        return text_fully_masked, link_matches, tag_matches

    def unmask(self, text, link_matches, tag_matches):
        for i, m in enumerate(tag_matches):
            text = text.replace(f"❰IE_TAG_{i}❱", m)
        for i, (pre, suf) in enumerate(link_matches):
            text = text.replace(f"❰IE_PRE_{i}❱", pre)
            text = text.replace(f"❰IE_SUF_{i}❱", suf)
        return text

# --- 測試區塊 ---
if __name__ == "__main__":
    test_text = """适用方块
嗯⋯⋯挑哪个呢⋯⋯
 1 目录页
 2 <link;immersiveposts:posts;§1防腐木§r;treated>
 3 <link;immersiveposts:posts;§1铝§r;aluminium>
 4 <link;immersiveposts:posts;§1钢§r;steel>

<&aluminium>铝。<np>
由于§o稳定性§r问题，2格长横臂§l不§r会上下翻转。最长<config;i;maxTrussLength>格。"""

    masker = ImmersiveManualMasker()
    print("【原始文本】\n", test_text, "\n" + "="*40)
    
    masked, links, tags = masker.mask(test_text)
    print("【遮罩後文本】\n", masked, "\n" + "="*40)
    
    print("【受保護的標記集合】")
    for i, (pre, suf) in enumerate(links):
        print(f"❰IE_PRE_{i}❱ : {pre} | ❰IE_SUF_{i}❱ : {suf}")
    for i, tag in enumerate(tags):
        print(f"❰IE_TAG_{i}❱ : {tag}")