# 使用celery
from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/0')

file = "test.txt"
@app.task
def add(a, b):
    c = a+ b
    print(c)
    with open(file, 'w') as f:
        f.write(c)