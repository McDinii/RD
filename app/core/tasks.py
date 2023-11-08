from celery import shared_task
from django.core.mail import EmailMessage
import qrcode
from celery.schedules import crontab
from django.utils.crypto import get_random_string
from .models import Node
import random
from django.db.models import F
from django.contrib import messages
from decimal import Decimal
import os
from django.conf import settings

@shared_task
def increase_debt():
    for node in Node.objects.all():
        debt_increase = Decimal(random.uniform(5.00, 500.00))
        node.debt += debt_increase
        node.save()

@shared_task
def decrease_debt():
    for node in Node.objects.all():
        debt_decrease = Decimal(random.uniform(100.00, 10000.00))
        if node.debt - debt_decrease < 0:
            node.debt = 0.00
        else:
            node.debt -= debt_decrease
        node.save()



@shared_task
def clear_debt_async(queryset_ids):
    queryset = Node.objects.filter(pk__in=queryset_ids)
    queryset.update(debt=0)

@shared_task
def send_email_with_qr(to_email, data):
    qr_img = qrcode.make(data)
    image_path = os.path.join(settings.MEDIA_ROOT, 'contact_info.png')
    qr_img.save(image_path)
    email = EmailMessage(
        'Ваш QR код c контактными данными обьекта сети',
        'Во вложении ваш QR код.',to=['denisnechay@gmail.com',to_email]
        # to=[to_email]
    )
    email.attach_file('contact_info.png')
    email.send()
    os.remove(image_path)
    return None
