import re
from typing import List

from docx.oxml.text import paragraph


class TextSplitter:
    """文本分割器，按段落、句子或固定长度分割"""
    def __init__(self, chunk_size: int = 500, chunk_overlap:int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text:str) -> list[str]:
        """
        将文本分割为多个块
        优先按段落分割，若段落过长再按句子分割
        """
        # 1. 按段落分割（\n\n）
        paragraph = re.split(r'\n\*s\n', text)
        chunks = []

        for para in paragraph:
            para = para.strip()
            if not para: continue

            if len(para) <= self.chunk_size:
                chunks.append(para)
            else:
                # 段落过长，按句子分割
                sentences = re.split(r'!,.。，？！', para)
                current_chunk = ""

                for sent in sentences:
                    if len(current_chunk)+len(sent) <= self.chunk_size :
                        current_chunk += sent +"。"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sent+"。"
                if current_chunk : chunks.append(current_chunk)

        # 2. 处理重叠（简单的滑动窗口）
        if self.chunk_overlap > 0 and len(chunks) > 1:
            over_chunks = []
            for i, chunk in enumerate(chunks):
                if i == 0: continue

                # 与前一个块重叠
                pre_txt = chunks[i-1];
                overlap_txt = pre_txt[-self.chunk_overlap:] if len(pre_txt) > self.chunk_overlap else pre_txt
                over_chunk = overlap_txt + chunk
                chunk = over_chunk
                over_chunks.append(chunk)
            chunks = over_chunks

        return chunks

# 全局单例
splitter = TextSplitter()