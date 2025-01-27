from django.db import models
from django.shortcuts import reverse

class Item(models.Model):
    name = models.CharField(max_length=155,
                            verbose_name="Название")
    price = models.DecimalField(max_digits=8,
                                decimal_places=2,
                                verbose_name="Стоимость")

    def __str__(self):
        return f"Блюдо: {self.name}. Стоимость: {self.price}"

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено'),
    ]

    table_number = models.PositiveIntegerField(verbose_name="Номер стола",
                                               unique=True)
    total_price = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      default=0,
                                      verbose_name="Сумма заказа")
    status = models.CharField(max_length=7,
                              choices=STATUS_CHOICES,
                              default="pending", verbose_name="Статус")
    items = models.ManyToManyField(to=Item)

    def __str__(self):
        return f"Заказ #{self.id}. Статус: {self.status}"

    def get_absolute_url(self):
        return reverse("orders:order_detail", kwargs={
            "order_pk": self.pk
        })

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
