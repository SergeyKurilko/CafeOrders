import json

from django.urls import reverse
from django.test import RequestFactory, TestCase
from django.db.models import Sum
from orders.views import (
    CreateOrderView, UpdateOrderView, DeleteOrderView,
    SearchOrderView, calculate_total_revenue
)
from orders.models import Order, Item


class BaseOrderViewTest(TestCase):
    """
    Базовый класс для тестирования Order views
    """
    def setUp(self):
        self.factory = RequestFactory()

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


class CreateOrderViewTest(BaseOrderViewTest):
    """
    Класс для тестирования CreateOrderView
    """
    def test_create_order_post_valid(self):
        """
        Проверка создания Order с валидными данными.
        """
        orders_count_before_create = Order.objects.all().count()
        expected_orders_count = orders_count_before_create + 1

        data = {
            "table_number": 4,
            "items": [self.item_1.id, self.item_2.id]
        }

        request = self.factory.post(reverse("orders:create_order"), data)
        response = CreateOrderView.as_view()(request)

        orders_count_after_create = Order.objects.all().count()

        self.assertEqual(orders_count_after_create, expected_orders_count)
        self.assertEqual(302, response.status_code)

    def test_create_order_post_invalid_items(self):
        """
        Проверка создания Order с невалидными данными поля items.
        """
        orders_count_before_create = Order.objects.all().count()

        data = {
            "table_number": 666,
            "items": "Some string"
        }

        request = self.factory.post(reverse("orders:create_order"), data)
        response = CreateOrderView.as_view()(request)

        orders_count_after_create = Order.objects.all().count()

        self.assertEqual(orders_count_after_create, orders_count_before_create)
        self.assertEqual(200, response.status_code)

    def test_create_order_post_not_unique_table(self):
        """
        Проверка создания Order с неуникальным table_number
        """
        orders_count_before_create = Order.objects.all().count()

        data = {
            "table_number": 7,
            "items": [self.item_1.id, self.item_2.id]
        }

        request = self.factory.post(reverse("orders:create_order"), data)
        response = CreateOrderView.as_view()(request)

        orders_count_after_create = Order.objects.all().count()

        self.assertEqual(orders_count_after_create, orders_count_before_create)
        self.assertEqual(200, response.status_code)


class UpdateOrderViewTest(BaseOrderViewTest):
    def test_update_order_status_no_status_data(self):
        """
        Проверка изменения статуса заказа с отсутствием ожидаемых данных.
        """
        order = self.order_1

        # Сохранение статуса до изменения
        original_order_status = order.status

        # Формируем случайные данные без new_status
        data = {
            "random_data": 18,
            "another": "string"
        }

        request = self.factory.patch(
            path=reverse("orders:change_order_status", args=[order.pk]),
            data=json.dumps(data),
            content_type="application/json"
        )
        response = UpdateOrderView.as_view()(request, order_pk=order.pk)

        order.refresh_from_db()
        response_content = json.loads(response.content)
        response_status = response.status_code

        # Ожидаемый контент ответа
        expected_content = {'success': False}

        # Проверяем, что статус не изменен
        self.assertEqual(order.status, original_order_status)

        # Проверяем ответ
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response_status, 400)

    def test_update_order_status_not_allowed(self):
        """
        Проверка изменения статуса заказа с недопустимым значением статуса.
        """
        order = self.order_1

        # Сохранение статуса до изменения
        original_order_status = order.status

        # Формируем данные с недопустимым new_status
        data = {
            "new_status": "destroyed",
        }

        request = self.factory.patch(
            path=reverse("orders:change_order_status", args=[order.pk]),
            data=json.dumps(data),
            content_type="application/json"
        )
        response = UpdateOrderView.as_view()(request, order_pk=order.pk)

        order.refresh_from_db()
        response_content = json.loads(response.content)
        response_status = response.status_code

        # Ожидаемый контент ответа
        expected_content = {'success': False}

        # Проверяем, что статус не изменен
        self.assertEqual(order.status, original_order_status)

        # Проверяем ответ
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response_status, 400)

    def test_update_non_exist_order_status(self):
        """
        Проверка изменения статуса у несуществующего заказа.
        """
        non_exist_order_pk = 137

        # Формируем валидные данные для изменения статуса
        data = {
            "new_status": "paid",
        }

        request = self.factory.patch(
            path=reverse("orders:change_order_status", args=[non_exist_order_pk]),
            data=json.dumps(data),
            content_type="application/json"
        )
        response = UpdateOrderView.as_view()(request, order_pk=non_exist_order_pk)

        response_content = json.loads(response.content)
        response_status = response.status_code

        # Ожидаемый контент ответа
        expected_content = {'success': False, 'message': 'Заказ не найден'}

        # Проверяем ответ
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response_status, 404)

    def test_update_order_status_valid(self):
        """
        Проверка изменения статуса заказа с валидными данными.
        """
        order = self.order_1

        # Сохранение статуса до изменения
        original_order_status = order.status

        data = {
            "new_status": "paid",
        }

        request = self.factory.patch(
            path=reverse("orders:change_order_status", args=[order.pk]),
            data=json.dumps(data),
            content_type="application/json"
        )
        response = UpdateOrderView.as_view()(request, order_pk=order.pk)


        order.refresh_from_db()
        response_content = json.loads(response.content)
        response_status = response.status_code

        # Ожидаемый контент ответа
        expected_content = {
            'success': True,
            'message': 'Статус успешно обновлен_Оплачено',
            'link': None
        }

        # Проверяем, что статус обновлен
        self.assertEqual(order.status, "paid")
        self.assertNotEquals(order.status, original_order_status)

        # Проверяем ответ
        self.assertEqual(200, response_status)
        self.assertEqual(response_content, expected_content)


class DeleteOrderViewTest(BaseOrderViewTest):
    """
    Класс для тестирования DeleteOrderView
    """
    def test_delete_non_exist_order(self):
        """
        Проверка удаления несуществующего заказа
        """
        non_exist_order_pk = 77

        request = self.factory.delete(
            path=reverse("orders:delete_order", args=[non_exist_order_pk])
        )
        response = DeleteOrderView.as_view()(request, non_exist_order_pk)

        response_content = json.loads(response.content)
        response_status = response.status_code

        expected_content = {
            "success": False,
            "message": "Заказ не найден"
        }

        # Проверяем ответ
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response_status, 404)

    def test_delete_existing_order(self):
        """
        Проверка удаления заказа.
        """

        order = self.order_1
        order_pk = order.pk
        orders_before_deletion_count = Order.objects.all().count()

        request = self.factory.delete(
            path=reverse("orders:delete_order", args=[order_pk])
        )
        response = DeleteOrderView.as_view()(request, order_pk)

        expected_orders_count = orders_before_deletion_count - 1

        # Проверка удаления объекта Order
        orders_current_count = Order.objects.all().count()

        self.assertEqual(orders_current_count, expected_orders_count)
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order.pk)

        # Проверка ответа
        expected_content = {
            "success": True,
            "message": f"Заказ №{order_pk} удален.\nСейчас вы будете перенаправлены к списку заказов.",
            "link": None
        }

        response_content = json.loads(response.content)
        response_status = response.status_code

        self.assertEqual(response_content, expected_content)
        self.assertEqual(response_status, 200)


class SearchOrderViewTest(BaseOrderViewTest):
    """
    Класс для тестирования SearchOrderView

    Args:
        url: URL для запроса
    """
    search_url = reverse("orders:search_order")

    def _request_response(self, params):
        """
        Создание запроса к view
        """
        request = self.factory.get(
            path=reverse("orders:search_order"),
            query_params=params,
        )
        response = SearchOrderView.as_view()(request)
        return response

    def test_search_order_no_params(self):
        """
        Проверка запроса без необходимых параметров
        """

        # Формируем случайный параметр
        params = {
            "some_parameter": "55"
        }


        # request = self.factory.get(
        #     path=self.search_url,
        #     query_params=params,
        # )
        #
        # response = SearchOrderView.as_view()(request)

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": "No required parameters"
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 400)

    def test_search_order_by_no_valid_id(self):
        """
        Проверка поиска заказа по невалидному ID (не числу)
        """

        # Невалидные параметры search_val для поиска заказа по ID
        params = {
            "orderSearchType": "by_id",
            "search_val": "some_string"
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": "Должно быть целым числом"
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 400)

    def test_search_order_by_valid_id(self):
        """
        Проверка поиска заказа по валидному ID
        """
        order = self.order_1

        # Валидные параметры search_val для поиска заказа по ID
        params = {
            "orderSearchType": "by_id",
            "search_val": order.pk
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": True,
            "message": f"Найден заказ №{order.pk}\n",
            "link": order.get_absolute_url()
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 200)

    def test_search_non_exist_order_by_id(self):
        """
        Проверка поиска несуществующего заказа по ID
        """
        non_exist_order_pk = 88

        params = {
            "orderSearchType": "by_id",
            "search_val": non_exist_order_pk
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": f"Заказ {non_exist_order_pk} не найден."
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 404)

    def test_search_order_by_no_valid_table(self):
        """
        Проверка поиска заказа по невалидному table_number (не числу)
        """

        # Невалидные параметры search_val для поиска заказа по table_number
        params = {
            "orderSearchType": "by_table",
            "search_val": "some_string"
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": "Должно быть целым числом"
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 400)

    def test_search_order_by_valid_table(self):
        """
        Проверка поиска заказа по валидному table_number
        """
        order = self.order_1

        # Валидные параметры search_val для поиска заказа по table_number
        params = {
            "orderSearchType": "by_table",
            "search_val": order.table_number
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": True,
            "message": f"Найден заказ №{order.pk}\n",
            "link": order.get_absolute_url()
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 200)

    def test_search_non_exist_order_by_table(self):
        """
        Проверка поиска несуществующего заказа по table_number
        """
        non_exist_table = 88

        params = {
            "orderSearchType": "by_table",
            "search_val": non_exist_table
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": f"Заказ для стола №{non_exist_table} не найден."
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 404)

    def test_search_order_by_not_allowed_status(self):
        """
        Проверка поиска заказа по недопустимому статусу.
        Параметр search_val не соответствует списку допустимых.
        Разрешенные статусы: pending, ready, paid
        """
        params = {
            "orderSearchType": "by_status",
            "search_val": "sold"
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": "Not allowed status"
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 400)

    def test_search_order_by_status_not_found(self):
        """
        Проверка поиска заказа по статусу с результатом отсутствия
        заказов с таким статусом.
        """

        # В тестовой БД нет заказов со статусом ready
        params = {
            "orderSearchType": "by_status",
            "search_val": "ready"
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": False,
            "message": "Не найдено заказов с таким статусом."
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 404)

    def test_search_order_by_status_success(self):
        """
        Проверка поиска заказов по статусу "paid"
        """
        order_status = "paid"
        paid_orders = Order.objects.filter(status=order_status)

        params = {
            "orderSearchType": "by_status",
            "search_val": order_status
        }

        response = self._request_response(params)

        response_content = json.loads(response.content)

        expected_content = {
            "success": True,
            "message": f"Найдено заказов: {paid_orders.count()}",
            "link": f"{reverse('orders:orders_list')}?status={order_status}"
        }

        # Проверка ответа
        self.assertEqual(response_content, expected_content)
        self.assertEqual(response.status_code, 200)


class CalculateTotalRevenueTest(BaseOrderViewTest):
    """
    Класс для тестирования calculate_total_revenue
    """
    def test_calculate_total_revenue(self):
        """
        Проверка рассчета общей выручки по оплаченным заказам
        """

        # Общая выручка по заказам со статусом "paid"
        orders_total_revenue = (
            Order.objects.filter(status="paid").
            aggregate(total_revenue=Sum("total_price")))["total_revenue"]

        request = self.factory.get(
            path=reverse("orders:calculate_total_revenue")
        )

        response = calculate_total_revenue(request)

        response_content = json.loads(response.content)

        expected_content = {
            'success': True,
            'message': str(orders_total_revenue),
            'link': None}

        # Проверка ответа
        self.assertEqual(response_content.get("message"), str(orders_total_revenue))
        self.assertEqual(response.status_code, 200)