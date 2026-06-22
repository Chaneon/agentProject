import re
from typing import List

"""
文本分割工具 - 将长文本切分为适合向量化的段落
"""
class TextSplitter:
    """文本分割器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        将文本分割为多个块
        优先按段落分割，若段落过长再按句子分割
        """
        if not text or not text.strip():
            return []

        # 1. 按段落分割（\n\n）
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(para) <= self.chunk_size:
                chunks.append(para)
            else:
                # 段落过长，按句子分割
                sentences = re.split(r'[。！？；]', para)
                current = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current) + len(sent) + 1 <= self.chunk_size:
                        current += ("。" + sent) if current else sent
                    else:
                        if current:
                            chunks.append(current + "。")
                        current = sent
                if current:
                    chunks.append(current + "。")

        # 重叠处理
        if self.chunk_overlap > 0 and len(chunks) > 1:
            overlapped = []
            for i, chunk in enumerate(chunks):
                if i > 0 and len(chunks[i-1]) > self.chunk_overlap:
                    # 与前一个块重叠
                    chunk = chunks[i-1][-self.chunk_overlap:] + chunk
                overlapped.append(chunk)
            chunks = overlapped

        return chunks


splitter = TextSplitter()