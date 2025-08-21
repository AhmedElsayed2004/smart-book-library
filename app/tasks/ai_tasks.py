from .celery_app import celery_app
from app.services.ai_service import add_book_to_vector_stores


@celery_app.task
def embed_book_task(url: str, slug: str):
    add_book_to_vector_stores(url, slug)

