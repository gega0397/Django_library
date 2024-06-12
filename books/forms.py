from django import forms
from django.conf import settings
from django.utils import timezone

from books.models import Borrow, Reserve


class BookForm(forms.Form):
    query = forms.CharField(label='Search books',
                            required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Search books...'}))

class GenreForm(forms.Form):
    genre = forms.CharField(label='Search genres',
                            required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Search genres...'}))

class BorrowAdminForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get("due_date")
        if not due_date:
            cleaned_data["due_date"] = timezone.now() + settings.BORROW_TIME_LIMIT
        return cleaned_data


class ReserveAdminForm(forms.ModelForm):
    class Meta:
        model = Reserve
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get("due_date")
        if not due_date:
            cleaned_data["due_date"] = timezone.now() + settings.RESERVE_TIME_LIMIT
        return cleaned_data