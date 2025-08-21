from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks.book_tasks", "app.tasks.ai_tasks"]
)

celery_app.conf.task_routes = {
    "app.tasks.book_tasks.*": {"queue": "books"},
    "app.tasks.ai_tasks.*": {"queue": "ai"}
}