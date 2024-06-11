from django.core.management import BaseCommand
from django.utils.timezone import now
from rest_framework.utils import json

from books.models import Reserve


class Command(BaseCommand):
    help = 'Check reserves'

    def handle(self, *args, **options):
        today = now().date()
        reserves_due = Reserve.objects.filter(due_date=today).select_related('user', 'book')

        reserves_list = []

        for reserve in reserves_due:
            reserves_list.append({
                'id': reserve.id,
                'user': {
                    'id': reserve.user.id,
                    'name': reserve.user.get_full_name(),
                    'email': reserve.user.email,
                },
                'book': {
                    'id': reserve.book.id,
                    'title': reserve.book.title,
                },
                'due_date': str(reserve.due_date)
            })

        reserves_json = json.dumps(reserves_list, indent=4)
        self.stdout.write(reserves_json)