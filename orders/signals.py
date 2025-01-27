from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from orders.models import Order


@receiver(m2m_changed, sender=Order.items.through)
def update_total_price_on_items_change(sender, instance, action, **kwargs):
    """
    Сигнал для обновления общей стоимости заказа при изменении списка блюд.
    """
    # Проверяем, что сигнал сработал после добавления, удаления или очистки блюд
    if action in ('post_add', 'post_remove', 'post_clear'):
        # Пересчитываем total_price
        instance.total_price = sum(item.price for item in instance.items.all())

        # Сохраняем заказ, но обновляем только поле total_price
        instance.save(update_fields=['total_price'])