$(document).ready(function () {
    $("#deleteOrderConfirmButton").click(function (e) { 
        e.preventDefault();

        var urlForDelete = $(this).data("del_order_url");
        var csrfToken = $(this).data("csrf")
        var urlForRedirectAfterDelete = $(this).data("url_redirect_after_delete")

        $.ajax({
            type: "DELETE",
            url: urlForDelete,
            dataType: "json",
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function (response) {
                if (response.success) {
                    $('#confirmDeleteOrderModal').modal('hide');
                    $('#openModalForDeleteButton').remove();
                    $('.order-list-card').addClass("blur-4");
                    $(".table").after(`<h4 class="text-danger">Заказ удален</h4>`)
                    showSuccessAlert(response.message);
                    setTimeout(function () {
                        window.location.replace(urlForRedirectAfterDelete)
                    }, 3000);
                }
            },
            error: function (xhr, status, error) {
                showDangerAlert(error)
            }
        });
    });

    // Включение изменения статуса
    $("#changeOrderStatusButton").click(function (e) { 
        e.preventDefault();
        $("#changeOrderStatusSelects").removeClass("d-none")
        $(".actual-order-status").addClass("d-none")
        $("#confirmChangeOrderStatusButton").removeClass("d-none")
        $("#cancelChangeOrderStatusButton").removeClass("d-none")
        $(this).addClass("d-none")
        $("#newOrderStatusInput").val($("#changeOrderStatusSelects").val())
        var v = $("#newOrderStatusInput").val()
    });

    // Отмена изменения статуса
    $("#cancelChangeOrderStatusButton").click(function (e) { 
        e.preventDefault();
        $("#changeOrderStatusSelects").addClass("d-none")
        $(".actual-order-status").removeClass("d-none")
        $("#confirmChangeOrderStatusButton").addClass("d-none")
        $(this).addClass("d-none")
        $("#changeOrderStatusButton").removeClass("d-none")
    });

    // Выбор нового статуса и запись его в поле для отправки формы
    $("#changeOrderStatusSelects").change(function () {
        var selectedValue = $(this).val();
        $("#newOrderStatusInput").val(selectedValue)
    });

    $("#changeOrderStatusForm").submit(function (e) { 
        e.preventDefault();

        // var formData = $(this).serialize()
        var urlForRequest = $(this).attr("action")
        var csrfToken = $(this).data("csrf_token")
        var newStatus = $("#newOrderStatusInput").val()

        $.ajax({
            type: "PATCH",
            url: urlForRequest,
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({  // Преобразуем объект в JSON
                new_status: newStatus
            }),
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function (response) {
                if (response.success) {
                    var messageParts = response.message.split("_");
                    var messageForAlert = messageParts[0]
                    var newActualStatus = messageParts[1]

                    showSuccessAlert(messageForAlert);

                    $("#changeOrderStatusSelects").addClass("d-none")
                    $("#confirmChangeOrderStatusButton").addClass("d-none")
                    $("#cancelChangeOrderStatusButton").addClass("d-none")
                    $("#changeOrderStatusButton").removeClass("d-none")
                    $(".actual-order-status")
                        .html(`<h5>${newActualStatus}</h5>`)
                        .removeClass()
                        .addClass(`order-status-${newStatus}`)
                        .addClass(`ms-2`)
                        .addClass(`actual-order-status`)
                    // setTimeout(function () {
                    //     window.location.reload()
                    // }, 2000);   
                }
            }
        });
        
    });

});