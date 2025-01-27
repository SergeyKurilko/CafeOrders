from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from orders.models import Order, Item
from orders.serializers import ItemSerializer, OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заказами.

    Поддерживает стандартные операции CRUD (создание, чтение, обновление, удаление)
    для модели Order. Также предоставляет кастомное действие для изменения статуса заказа.

    Attributes:
        queryset (QuerySet): Набор всех заказов.
        serializer_class (OrderSerializer): Сериализатор для модели Order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        Изменяет статус заказа.

        Args:
            request (Request): Объект запроса, содержащий новый статус.
            pk (int, optional): ID заказа. По умолчанию None.

        Returns:
            Response: JSON-ответ с сообщением об успешном обновлении статуса
            или ошибкой, если статус недопустим.

        Examples:
            Пример запроса:
            POST /api/orders/1/change_status/
            {
                "status": "paid"
            }
        """
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES).keys():
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({"message": "Status updated successfully"})


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления блюдами.

    Поддерживает стандартные операции CRUD (создание, чтение, обновление, удаление)
    для модели Item.

    Attributes:
        queryset (QuerySet): Набор всех блюд.
        serializer_class (ItemSerializer): Сериализатор для модели Item.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer