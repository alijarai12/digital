from celery import shared_task
from .models import User

# from celery.decorators import task


@shared_task(max_retires=3, soft_time_limit=60)
def add(x, y):
    a = x + y
    u = User.objects.filter(id=2).update(is_deleted=True)
    return a


@shared_task(max_retires=3, soft_time_limit=60)
def test():
    u = User.objects.filter(id=2).update(is_deleted=True)
    return u
