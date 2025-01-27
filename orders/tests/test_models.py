from django.db import IntegrityError
from django.test import TestCase
from orders.models import Item, Order


# Test for Item model
class ItemModelTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(name="Яичница", price=450.00)

    def test_item_create(self):
        """
        Проверка создания объекта Item
        """
        # Создание объекта
        item = Item.objects.create(
            name = "Английский завтрак",
            price = 800.00
        )

        # Проверка корректного создания и записи объекта в БД
        self.assertIsNotNone(item.id)
        self.assertEqual(item.name, "Английский завтрак")
        self.assertEqual(item.price, 800.00)

    def test_item_read(self):
        """
        Проверка чтения объекта Item из БД
        """
        # Получение объекта
        item = Item.objects.get(pk=self.item.pk)

        # Ожидаемые данные
        expected_id = self.item.id
        expected_name = self.item.name
        expected_price = 450.00

        # Проверка равенства данных
        self.assertEqual(item.id, expected_id)
        self.assertEqual(item.name, expected_name)
        self.assertEqual(item.price, expected_price)

    def test_item_update(self):
        """
        Проверка обновления объекта Item
        """
        item = self.item

        # Обновление данных
        item.name = "Хлеб"
        item.price = 30.00
        item.save()

        # Проверка обновленных данных
        self.assertEqual(item.name, "Хлеб")
        self.assertEqual(item.price, 30.00)

    def test_item_delete(self):
        """
        Проверка удаления объекта Item
        """
        # Удаляем объект
        self.item.delete()

        # Проверка, что объект не существует в БД
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(id=self.item.id)

    def test_item_str_representation(self):
        item = self.item
        expected_str = "Блюдо: Яичница. Стоимость: 450.0"
        self.assertEqual(str(item), expected_str)


# Test for Order model
class OrderModelTest(TestCase):
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

    def test_order_create(self):
        # Создание нового объекта Order
        items_for_new_order = [
            self.item_1, self.item_2, self.item_3
        ]

        new_order = Order.objects.create(
            table_number = 8
        )
        new_order.items.set(items_for_new_order)

        # Проверка корректного создания и записи объекта в БД
        self.assertIsNotNone(new_order.id)
        self.assertEqual(new_order.table_number, 8)
        self.assertEqual(new_order.total_price, 3150.00)
        self.assertEqual(new_order.status, "pending")
        self.assertEqual(list(new_order.items.all()), items_for_new_order)


    def test_order_table_number_uniqueness(self):
        """
        Проверка уникальности table_number при создании Order
        """
        new_order = Order.objects.create(table_number=20)

        with self.assertRaises(IntegrityError):
            Order.objects.create(table_number=20)


    def test_order_read(self):
        """
        Проверка чтения одного объекта Order из БД
        """
        expected_items = [self.item_1, self.item_3]
        order = Order.objects.get(id=self.order_1.id)

        self.assertEqual(order.id, self.order_1.id)
        self.assertEqual(order.table_number, 1)
        self.assertEqual(list(order.items.all()), expected_items)

    def test_order_read_all(self):
        # Проверка чтения всех объектов Order из БД
        expected_orders = [self.order_1, self.order_2]
        orders = Order.objects.all()

        self.assertEqual(list(orders), expected_orders)

    def test_order_update_items(self):
        """
        Проверка добавления items в заказе
        """
        order = self.order_1
        new_item = self.item_2

        expected_new_total_price = float(order.total_price) + new_item.price

        # Проверка отсутствия нового item в Order
        self.assertNotIn(new_item, order.items.all())

        # Добавление нового item для Order
        order.items.add(new_item)
        order.refresh_from_db()


        # Проверка наличия нового item в Order
        self.assertIn(new_item, order.items.all())

        # Проверка изменения total_price у Order после добавления item
        self.assertEqual(order.total_price, expected_new_total_price)

    def test_order_delete(self):
        """
        Проверка удаления объекта Order
        """
        order = self.order_1

        # Сохранение id объекта Order
        order_id = order.id

        # Удаляем объект
        order.delete()

        # Проверка, что объект не существует в БД
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(id=order_id)

    def test_order_str_representation(self):
        order = self.order_1
        expected_str = "Заказ #1. Статус: pending"
        self.assertEqual(str(order), expected_str)













# TODO: не забудь для UPDATE написать тест для signal (total_price)








