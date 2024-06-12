from django.core.mail import send_mail
from django.conf import settings


def email(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['g_kandelaki@cu.edu.ge',]
    send_mail(subject, message, email_from, recipient_list)


def email_borrow(request, email, name, due_date, book_title):
    message = (f'dear {name}, \n'
               f'You have borrowed a book from our library, for which the due borrow time is due at {due_date} \n'
               f'Please return the book "{book_title}" at your earliest convenience \n')
    subject = ' You have unriturned book from our library '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def email_reserve(request, email, name, pk, book_title):
    message = (f'dear {name}, \n'
               f'Your reservation time is over for {book_title} \n'
               f'if you wish to reserve the book again follow the link http://localhost:8000/{pk}/ \n')
    subject = ' You have unriturned book from our library '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)