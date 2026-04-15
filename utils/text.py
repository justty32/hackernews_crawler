import re

def clean_html(text):
    """清理 HTML 標籤"""
    if not text:
        return ""
    text = text.replace('<p>', '\n').replace('</p>', '')
    text = text.replace('<i>', '').replace('</i>', '')
    text = re.sub(r'<a href="(.*?)".*?>(.*?)</a>', r'\2 (\1)', text)
    return text

def truncate_text(text, limit=8000, marker="\n- "):
    """智慧截斷文字，儘量保持在區塊邊界"""
    if len(text) <= limit:
        return text
    
    break_point = text[:limit].rfind(marker)
    if break_point != -1:
        return text[:break_point] + f"\n\n(Part of content truncated for length limit...)"
    return text[:limit]
