from django import forms
from django.core.exceptions import ValidationError

from orders.models import Order, Item


class CreateOrderForm(forms.ModelForm):
    items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={
            'required': 'Заказ не может быть пустым.',  # Кастомное сообщение
        }
    )

    class Meta:
        model = Order
        fields = ["table_number", "items"]
        widgets = {
            "table_number": forms.NumberInput(attrs={
                'class': 'form-control w-25',
                'placeholder': 'Номер стола'
            }),
        }
