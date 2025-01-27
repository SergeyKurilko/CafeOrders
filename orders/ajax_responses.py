from django.http.response import JsonResponse
from typing import Optional

class AjaxResponse:
    """
    Класс для формирования JSON-ответов в AJAX-запросах.
    """
    def bad_request(self) -> JsonResponse:
        """
        Возвращает ответ с кодом 400 (Bad Request).
        """
        return JsonResponse({
            "success": False,
        }, status=400)

    def bad_request_with_message(self, message: str) -> JsonResponse:
        """
        Возвращает сообщение о некорректном запросе.
        """
        return JsonResponse({
            "success": False,
            "message": message
        }, status=400)

    def success_request(self, message: str, link: Optional[str] = None) -> JsonResponse:
        """
        Возвращает успешный JSON-ответ с сообщением (message).
        Опционально возвращает ссылку (link).
        """
        return JsonResponse({
            "success": True,
            "message": message,
            "link": link
        })

    def not_found(self, message: str) -> JsonResponse:
        """
        Возвращает JSON-ответ с сообщением о ненайденном объекте и статусом 404 (Not Found).
        """
        return JsonResponse({
            "success": False,
            "message": message
        }, status=404)

ajax_response = AjaxResponse()


