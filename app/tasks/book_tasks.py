from .celery_app import celery_app


@celery_app.task
def delete_book_embedding(book_id: int):
    pass
