from sqlalchemy.orm import Session

from app.models.mysql import Product, Faq
from app.core.embedding import embedding_model
from app.core.milvus_client import milvus_client
from app.core.config import settings
from app.utils.logger import log

"""
数据同步服务 - 从主系统同步商品和FAQ到Milvus
"""
class SyncService:
    """数据同步服务"""

    @staticmethod
    async def sync_products(db: Session) -> Dict:
        """同步商品到Milvus"""
        products = db.query(Product).filter(Product.enabled == True).all()
        if not products:
            return {"synced": 0}

        items = []
        for p in products:
            text = f"{p.name} {p.selling_points or ''} {p.specs or ''}"
            embedding = embedding_model.encode(text)
            items.append({
                "doc_id": f"product_{p.product_id}",
                "text": text,
                "embedding": embedding,
                "metadata": {"product_id": p.product_id, "name": p.name, "price": p.price}
            })

        milvus_client.delete_by_filter(settings.MILVUS_PRODUCT_COLLECTION, 'doc_id like "product_%"')
        milvus_client.insert_batch(settings.MILVUS_PRODUCT_COLLECTION, items)
        log.info(f"商品同步完成: {len(items)}条")
        return {"synced": len(items)}

    @staticmethod
    async def sync_faqs(db: Session) -> Dict:
        """同步FAQ到Milvus"""
        faqs = db.query(Faq).filter(Faq.enabled == True).all()
        if not faqs:
            return {"synced": 0}

        items = []
        for f in faqs:
            text = f"{f.question} {f.answer}"
            if f.keywords:
                text += " " + " ".join(f.keywords)
            embedding = embedding_model.encode(text)
            items.append({
                "doc_id": f"faq_{f.faq_id}",
                "text": text,
                "embedding": embedding,
                "metadata": {"faq_id": f.faq_id, "question": f.question}
            })

        milvus_client.delete_by_filter(settings.MILVUS_FAQ_COLLECTION, 'doc_id like "faq_%"')
        milvus_client.insert_batch(settings.MILVUS_FAQ_COLLECTION, items)
        log.info(f"FAQ同步完成: {len(items)}条")
        return {"synced": len(items)}


sync_service = SyncService()