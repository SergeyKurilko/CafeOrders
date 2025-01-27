from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views import (home_page, UpdateOrderView,
                          calculate_total_revenue, OrderListView,
                          OrderDetailView, CreateOrderView,
                          DeleteOrderView, SearchOrderView)
from orders.api_views import OrderViewSet, ItemViewSet

app_name = "orders"

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = [
    path("", home_page, name="home_page"),

    path("orders/", OrderListView.as_view(),
         name="orders_list"),
    path("orders/order/<int:order_pk>",
         OrderDetailView.as_view(),
         name="order_detail"),
    path("orders/order/create_order",
         CreateOrderView.as_view(),
         name="create_order"),
    path('api/', include(router.urls))
]

ajax_urls = [
    path("orders/ajax/search_order/",
         SearchOrderView.as_view(),
         name="search_order"),
    path("orders/ajax/change_order_status/<int:order_pk>",
         UpdateOrderView.as_view(),
         name="change_order_status"),
    path("orders/order/delete_order/<int:order_pk>",
         DeleteOrderView.as_view(),
         name="delete_order"),
    path("orders/ajax/calculate_total_revenue",
         calculate_total_revenue,
         name="calculate_total_revenue"
         )
]

urlpatterns += ajax_urls