import io
from typing import List, Tuple
import pdfplumber
from docx import Document
from pypdf import PdfReader
from utils.logger import default_logger
from utils.text_splitter import splitter
"""文档解析器：提取文本内容并分块"""

class DocumentParser:
    @staticmethod
    def parse_pdf(file_bytes:bytes)->str:
        """解析 PDF 文件，返回纯文本"""
        try:
            reader = PdfReader(io.BytesIOf(file_bytes))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text: text += page_text + "\n"
            return text
        except Exception as e:
            default_logger.error(f"PDF解析失败：{e}")
            try:
                # 降级使用 pdfplumber
               with pdfplumber.open(io.BytesIOf(file_bytes)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text: text += page_text + "\n"
                    return text
            except Exception as e2:
                default_logger.error(f"pdfplumber解析失败：{e2}")
                return ""

    @staticmethod
    def parse_docx(file_bytes:bytes)->str:
        """解析 DOCX 文件，返回纯文本"""
        try:
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            default_logger.error(f"Document解析失败：{e}")
            return ""


    @staticmethod
    def parse_and_split(file_bytes:bytes, filename:str)->Tuple[str, List[str]]:
        """解析文件并返回原始文本和分块列表"""
        if filename.lower().endswith('.pdf'):
            raw_text = DocumentParser.parse_pdf(file_bytes)
        elif filename.lower().endswith('.docx'):
            raw_text = DocumentParser.parse_docx(file_bytes)
        else:
            # 假设是纯文本
            raw_text = file_bytes.decode('utf-8', errors='ignore')
        chunks = splitter.split_text(raw_text)
        return raw_text, chunks