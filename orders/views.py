import json
from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, QueryDict
from django.http.response import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Sum
from orders.models import Order
from orders.forms import CreateOrderForm
from orders.ajax_responses import ajax_response


def home_page(request: HttpRequest):
    """
    Отображает главную страницу приложения.

    Args:
        request (HttpRequest): Объект запроса Django.

    Returns:
        HttpResponse: Рендер шаблона главной страницы.
        HttpResponseNotAllowed: Если метод запроса не GET.
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(permitted_methods=["GET"])

    return render(request, "orders/home_page.html")


class BaseOrderView(View):
    """
    Базовый класс для views, работающих с заказами

    Attributes:
        model: Модель, с которой работает View (Order)
        form_class: Класс формы для создания нового заказа
        template_name (str): Имя шаблона для рендера (определяется в дочерних классах)
    """
    model = Order
    form_class = CreateOrderForm
    template_name = None

    def get_context_data(self, **kwargs):
        """
        Возвращает контекст для шаблонов

        Args:
            **kwargs: Дополнительные данные для контекста.

        Returns:
            dict: Контекст для шаблона.
        """
        return kwargs


class OrderListView(BaseOrderView):
    """
    View для отображения списка заказов

    Attributes:
        template_name (str): Имя шаблона для отображения списка заказов.
    """
    template_name = "orders/orders_list.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения списка заказов.

        Если в запросе передан параметр 'status', возвращает заказы с указанным статусом.

        Args:
            request (HttpRequest): Объект запроса Django.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Рендер шаблона с контекстом, содержащим список заказов.

        """
        status = request.GET.get("status")
        if status:
            orders = self.model.objects.filter(status=status)
            status = dict(Order.STATUS_CHOICES).get(status)
        else:
            orders = self.model.objects.all()

        context = self.get_context_data(orders=orders, status=status)

        return render(request, self.template_name, context=context)


class OrderDetailView(BaseOrderView):
    """
    View для отображения деталей конкретного заказа.

    Attributes:
        template_name (str): Имя шаблона для отображения деталей заказа.
    """
    template_name = "orders/order_detail.html"

    def get(self, request: HttpRequest, order_pk: int, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения деталей заказа.

        Args:
            request (HttpRequest): Объект запроса Django.
            order_pk (int): ID заказа.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Рендер шаблона с контекстом, содержащим данные заказа и URL для изменения статуса.
        """
        order = get_object_or_404(
            klass=self.model, pk=order_pk
        )

        context = self.get_context_data(
            order=order,
            url_for_change_order_status=reverse(
                "orders:change_order_status", args=[order.pk]
            )
        )
        return render(request,
                      self.template_name,
                      context=context
                      )


class CreateOrderView(BaseOrderView):
    """
    View для создания нового заказа.

    Attributes:
        template_name (str): Имя шаблона для отображения формы создания заказа.
    """
    template_name = "orders/order_create.html"

    def get(self, request: HttpRequest):
        """
        Обрабатывает GET-запрос для отображения формы создания заказа.

        Args:
            request (HttpRequest): Объект запроса Django.

        Returns:
            HttpResponse: Рендер шаблона с формой создания заказа.
        """
        form = self.form_class()
        context = self.get_context_data(
            form=form
        )
        return render(request,
                      self.template_name,
                      context=context
                      )

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Обрабатывает POST-запрос для создания нового заказа.

        Если данные формы валидны, создает заказ и перенаправляет на его детальную страницу.
        Иначе возвращает форму с ошибками.

        Args:
            request (HttpRequest): Объект запроса Django.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponseRedirect: Перенаправление на страницу созданного заказа.
            HttpResponse: Рендер шаблона с формой, если данные невалидны.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            new_order = form.save()
            redirect_url = reverse("orders:order_detail", args=[new_order.pk])
            return redirect(redirect_url)
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context=context)


# Views для AJAX

class DeleteOrderView(BaseOrderView):
    """
    View для удаления заказа.
    """
    def delete(self, request: HttpRequest, order_pk: int, *args, **kwargs):
        """
        Обрабатывает DELETE-запрос для удаления заказа.

        Args:
            request (HttpRequest): Объект запроса Django.
            order_pk (int): ID заказа для удаления.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            JsonResponse: JSON-ответ с результатом операции.
        """
        try:
            order = self.model.objects.get(pk=order_pk)
        except self.model.DoesNotExist:
            return ajax_response.not_found(
                message="Заказ не найден"
            )

        order.delete()
        return ajax_response.success_request(
            message=f"Заказ №{order_pk} удален.\nСейчас вы будете перенаправлены к списку заказов."
        )


class UpdateOrderView(BaseOrderView):
    """
    View для изменения статуса заказа
    """
    def patch(self, request: HttpRequest, order_pk):
        """
        Обрабатывает PATCH-запрос для изменения статуса заказа.

        Args:
            request (HttpRequest): Объект запроса Django.
            order_pk (int): ID заказа для обновления.

        Returns:
            JsonResponse: JSON-ответ с результатом операции.
        """
        allowed_statuses = dict(Order.STATUS_CHOICES)

        try:
            data = json.loads(request.body.decode('utf-8'))
            new_status = data.get("new_status")
        except json.JSONDecodeError:
            return ajax_response.bad_request()

        if not new_status or new_status not in allowed_statuses.keys():
            return ajax_response.bad_request()

        try:
            order = self.model.objects.get(pk=order_pk)
        except self.model.DoesNotExist:
            return ajax_response.not_found(
                message=f"Заказ не найден"
            )
        order.status = new_status
        order.save()
        return ajax_response.success_request(
            message=f"Статус успешно обновлен_{allowed_statuses.get(new_status)}"
        )


class SearchOrderView(BaseOrderView):
    """
    View для поиска заказов по ID, номеру стола или статусу.
    """
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Обрабатывает GET-запрос для поиска заказов.

        Args:
            request (HttpRequest): Объект запроса Django.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            JsonResponse: JSON-ответ с результатами поиска или ошибкой.
        """

        search_type = request.GET.get("orderSearchType")
        search_params = request.GET.get("search_val")

        if not search_type or not search_params:
            return ajax_response.bad_request_with_message(
                message="No required parameters"
            )

        if search_type == "by_id":
            return self._search_by_id(order_pk=search_params)
        elif search_type == "by_table":
            return self._search_by_table(table_id=search_params)
        elif search_type == "by_status":
            return self._search_by_status(order_status=search_params)
        else:
            return ajax_response.bad_request()

    def _search_by_id(self, order_pk):
        """
        Ищет заказ по ID.

        Args:
            order_pk (str): ID заказа для поиска.

        Returns:
            JsonResponse: JSON-ответ с результатом поиска или ошибкой.
        """
        if not order_pk.isnumeric():
            return ajax_response.bad_request_with_message("Должно быть целым числом")

        try:
            order = self.model.objects.get(pk=order_pk)
            return ajax_response.success_request(
                message=f"Найден заказ №{order.pk}\n",
                link=order.get_absolute_url()
            )
        except self.model.DoesNotExist:
            return ajax_response.not_found(f"Заказ {order_pk} не найден.")

    def _search_by_table(self, table_id):
        """
        Ищет заказ по номеру стола.

        Args:
            table_id (str): Номер стола для поиска.

        Returns:
            JsonResponse: JSON-ответ с результатом поиска или ошибкой.
        """
        if not table_id.isnumeric():
            return ajax_response.bad_request_with_message("Должно быть целым числом")

        try:
            order = self.model.objects.get(table_number=table_id)
            return ajax_response.success_request(
                message=f"Найден заказ №{order.pk}\n",
                link=order.get_absolute_url()
            )
        except self.model.DoesNotExist:
            return ajax_response.not_found(f"Заказ для стола №{table_id} не найден.")


    def _search_by_status(self, order_status):
        """
        Ищет заказы по статусу.

        Args:
            order_status (str): Статус заказа для поиска.

        Returns:
            JsonResponse: JSON-ответ с результатом поиска или ошибкой.
        """
        allowed_statuses = dict(self.model.STATUS_CHOICES)
        if order_status not in allowed_statuses.keys():
            return ajax_response.bad_request_with_message(
                message="Not allowed status"
            )

        orders = self.model.objects.filter(status=order_status)
        if orders.count() < 1:
            return ajax_response.not_found("Не найдено заказов с таким статусом.")
        return ajax_response.success_request(
            message=f"Найдено заказов: {orders.count()}",
            link=f"{reverse('orders:orders_list')}?status={order_status}"
        )


def calculate_total_revenue(request):
    """
    Обрабатывает GET-запрос.
    Рассчитывает общую выручку заказов со статусом "оплачено".

    Args:
        request (HttpRequest): Объект запроса Django.

    Returns:
        JsonResponse: JSON-ответ с суммой выручки или ошибкой.js)
    """
    if request.method == "GET":
        paid_orders = Order.objects.filter(status="paid")
        total_revenue_dict = paid_orders.aggregate(total_revenue=Sum("total_price"))
        total_revenue = total_revenue_dict["total_revenue"]
        if total_revenue is None:
            total_revenue = 0

        return ajax_response.success_request(
            message=total_revenue
        )
    else:
        return ajax_response.bad_request()



