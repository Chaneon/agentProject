from core.vector_store import init_milvus, insert_doc
from utils.logger import default_logger


def init_knowledge_base():
    """初始化知识库：插入示例法规和案例"""
    init_milvus()

    # 示例法规数据
    laws = [
        {
            "doc_id": "law_001",
            "text": "《中华人民共和国民法典》第577条规定：当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。",
            "metadata": {"type": "law", "title": "民法典第577条"}
        },
        {
            "doc_id": "law_002",
            "text": "《中华人民共和国合同法》第107条（已并入民法典）：当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。",
            "metadata": {"type": "law", "title": "合同法第107条"}
        }
    ]

    # 示例案例数据
    cases = [
        {
            "doc_id": "case_001",
            "text": "最高人民法院指导案例15号：某公司诉某公司买卖合同纠纷案。裁判要点：买受人以出卖人违反从给付义务为由拒绝履行主给付义务，人民法院不予支持。",
            "metadata": {"type": "case", "title": "指导案例15号"}
        }
    ]

    all_docs = laws + cases
    insert_doc(all_docs)
    default_logger.info("知识库初始化完成")

if __name__ == "__main__":
    init_knowledge_base()