from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from orders.models import Order, Item


class BaseOrderViewSetTests(APITestCase):
    """
        Базовый класс для тестирования Order ViewSet
    """
    def setUp(self):
        # Объекты Item для тестов
        self.item_1 = Item.objects.create(name="Яичница", price=450.00)
        self.item_2 = Item.objects.create(name="Чай", price=200.00)
        self.item_3 = Item.objects.create(name="Стейк", price=2500.00)

        # Объекты Order для тестов
        self.order_1 = Order.objects.create(table_number=1)
        self.order_1.items.set([self.item_1, self.item_3])

        self.order_2 = Order.objects.create(table_number=13)
        self.order_2.items.set([self.item_1, self.item_2, self.item_3])

        self.order_3 = Order.objects.create(table_number=2, status="paid")
        self.order_3.items.set([self.item_1, self.item_2, self.item_3])

        self.order_4 = Order.objects.create(table_number=7, status="paid")
        self.order_4.items.set([self.item_1, self.item_2, self.item_3])


class OrderViewSetTests(BaseOrderViewSetTests):
    """
    Класс для тестирования OrderViewSet
    """

    def test_create_order(self):
        """
        Проверка создания заказа
        """
        orders_count_before_create = Order.objects.all().count()

        detail_url = reverse('orders:order-list')
        data = {
            "table_number": 15,
            "items": [1, 2, 3]
        }
        response = self.client.post(detail_url, data)

        # Проверка изменения количества заказов в базе
        current_orders_count = Order.objects.all().count()
        expected_orders_count = orders_count_before_create + 1
        self.assertEqual(current_orders_count, expected_orders_count)

        # Проверка ответа
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверка созданного заказа
        new_order_id = response.data.get("id")
        new_order = Order.objects.get(id=new_order_id)
        expected_total_price = sum(item.price for item in new_order.items.all())

        self.assertIsNotNone(new_order.id)
        self.assertEqual(new_order.table_number, 15)
        self.assertEqual(new_order.total_price, expected_total_price)

    def test_get_single_order(self):
        """
        Проверка получения заказа по ID
        """
        detail_url = reverse('orders:order-detail', args=[self.order_1.id])
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')

    def test_update_order(self):
        """
        Проверка изменения заказа
        """
        order_for_change = self.order_1

        detail_url = reverse('orders:order-detail', args=[self.order_1.id])
        data = {
            "table_number": order_for_change.table_number,
            "items": [item.id for item in order_for_change.items.all()],
            "status": "paid"
        }
        response = self.client.put(detail_url, data, format='json')

        # Проверяем ответ
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем изменение статуса заказа
        self.order_1.refresh_from_db()
        self.assertEqual(self.order_1.status, 'paid')

    def test_delete_order(self):
        """
        Проверка удаления заказа
        """
        order_for_delete = self.order_1
        order_for_delete_id = order_for_delete.id
        orders_count_before_delete = Order.objects.all().count()

        detail_url = reverse('orders:order-detail', args=[order_for_delete_id])
        response = self.client.delete(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверка изменения количества заказов после удаления
        current_orders_count = Order.objects.all().count()
        expected_orders_count = orders_count_before_delete - 1
        self.assertEqual(current_orders_count, expected_orders_count)

        # Проверка отсутствия заказа в базе
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(id=order_for_delete_id)
