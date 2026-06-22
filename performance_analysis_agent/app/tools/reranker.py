from typing import List, Any, Dict

import torch.cuda
from transformers import AutoTokenizer, AutoModelForSequenceClassification, PreTrainedTokenizerBase

from app.utils.logger import default_logger

"""
重排序工具：使用 Cross-Encoder(交叉编码器) 模型对候选文档进行精细打分。
模型：Qwen/Qwen3-Reranker-0.6B（参数量 0.6B，轻量高效）

输入：query + candidates（[doc1, doc2, doc3, doc4, doc5]）
                ↓
        构造 (query, doc) 对
                ↓
        模型给每个对打分
                ↓
    doc1: 0.85, doc2: 0.32, doc3: 0.91, doc4: 0.67, doc5: 0.44
                ↓
        按分数从高到低排序
                ↓
        取 Top-3（假设 top_k=3）
                ↓
输出：[doc3(0.91), doc1(0.85), doc4(0.67)]
"""
class Reranker:
    def __init__(self, model_name: str, device: str=None):
        """
       :param model_name: HuggingFace 模型名称或本地路径
       :param device: 运行设备，None 表示自动检测 GPU
       """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        default_logger.info(f"加载重排序模型{model_name}， 设备：{self.device}")
        # AutoTokenizer：把文本转换成模型能理解的数字 ID
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # AutoModelForSequenceClassification：加载用于文本分类/排序的模型（输出一个相关性分数）
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        # to(self.device)：把模型加载到 GPU 或 CPU
        self.model.to(self.device)
        # eval()：切换到评估模式（关闭 Dropout 等训练专用层）
        self.model.eval()

    def rerank(self, query:str, candidates:List[Dict[str, Any]], top_k:int =3)->List[Dict[str, Any]]:
        """
        对候选文档进行重排序
        :param query: 用户问题
        :param candidates: 候选文档列表，每个元素需包含 'text' 字段
        :param top_k: 最终返回的文档数量
        :return: 排序后的前 top_k 个文档（每个文档会添加 rerank_score 字段）
        """
        if not candidates:
            return []
        """
            构建 [query, doc_text] 对,把每个候选文档和问题配对，生成一个列表。
            例如：candidates = [{"text": "文档1内容..."}, {"text": "文档2内容..."}]
            生成 pairs = [["什么是RAG？", "文档1内容..."], ["什么是RAG？", "文档2内容..."]]
        """
        pairs = [[query, doc['text']] for doc in candidates]
        # 批量分词，将文本对转换成模型能理解的数字 ID 矩阵。填充到相同长度，截断到512 token


        inputs = self.tokenizer(
            pairs,
            padding = True,             # 把短句子补齐到相同长度
            truncation = True,          # 超长则截断
            return_tensors ='pt',       # 返回 PyTorch 张量, PyTorch 张量是 PyTorch 中的核心数据结构，可以把它理解为“能跑在 GPU 上的 NumPy 数组”。
            max_length=512              # 最大长度 512 token
        )
        # 将数据移到 GPU/CPU
        inputs = {k: v.to(self.device) for k,v in inputs.items()}
        # 模型推理（计算相关性分数）
        with torch.no_grad():    # 不计算梯度（只推理，不训练）
            """
                self.model(**inputs)：模型前向传播，输出原始分数（logits）
                .logits：取出分数
                .view(-1,)：展平成一维张量，如 [0.85, 0.32, 0.91]
                .float()：转为浮点数
            """
            scores = self.model(**inputs).logits.view(-1,).float()

        for i,doc in enumerate(candidates):
            doc['rerank_score'] = scores[i].item()
        return sorted(candidates, key = lambda x:x['rerank_score'], reverse=True)[top_k]