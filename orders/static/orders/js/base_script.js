function showSuccessAlert(text, time=4000) {
    $(".base-alert")
        .addClass("alert-success")
        .text(text)
        .fadeIn(500); 

    setTimeout(function () {
        $(".base-alert").fadeOut(500, function () {
            // Убираем класс и очищаем текст после скрытия
            $(this).removeClass("alert-success").text("");
        });
    }, time);
}

function showDangerAlert(text) {
    $(".base-alert")
        .addClass("alert-danger")
        .text(text)
        .fadeIn(500); 

    setTimeout(function () {
        $(".base-alert").fadeOut(500, function () {
            // Убираем класс и очищаем текст после скрытия
            $(this).removeClass("alert-danger").text("");
        });
    }, time);
}

function showSuccessToast(text, link=null) {
    $("#navbarToast")
        .removeClass("navbar-toast-danger")
        .addClass("navbar-toast-success")
    $(".navbar-toast-message").text(text)

    if (link!=null) {
        $('.navbar-toast-message').append(link)
    }

    var myToast = new bootstrap.Toast(document.getElementById('navbarToast'));
    myToast.show()
}

function showDangerToast(text) {
    $("#navbarToast")
        .removeClass("navbar-toast-success")
        .addClass("navbar-toast-danger")
    $(".navbar-toast-message").text(text)

    var myToast = new bootstrap.Toast(document.getElementById('navbarToast'));
    myToast.show()
}

function checkInputForSearchByStatus(searchType) {
    
    if (searchType == "by_status") {
        $("#orderSearchInput").addClass("d-none")
        $("#orderSearchByStatusSelect").removeClass("d-none")
        $("#orderSearchInput").val($("#orderSearchByStatusSelect").val())
    } else {
        $("#orderSearchInput").removeClass("d-none")
        $("#orderSearchByStatusSelect").addClass("d-none")
        $("#orderSearchInput").val("")
    }
}

$(document).ready(function () {
    // Отслеживание выбранного способа поиска заказа
    $('.order-search-type').click(function (e) { 
        e.preventDefault();
        var orderSearchType = $(this)

        checkInputForSearchByStatus(orderSearchType.data("order_search_type"))

        var buttonForChangeSearchType = $("#buttonForChangeSearchType")
        var orderSearchTypeInput = $("#orderSearchTypeInput")
        orderSearchTypeInput.val(orderSearchType.data("order_search_type"))
        buttonForChangeSearchType.text(orderSearchType.text())
    });

    $("#orderSearchByStatusSelect").change(function () {
        var selectedValue = $(this).val();
        $("#orderSearchInput").val(selectedValue)
    });

    

    //Отправка запроса на поиск заказа
    $("#navbarSearchOrderForm").submit(function (e) { 
        e.preventDefault();
        
        var formValues = $(this).serialize()
        var urlForSearchOrderById = $(this).data("navbar_search_url")
        var myToast = new bootstrap.Toast(document.getElementById('navbarToast'));

        $.ajax({
            type: "GET",
            url: urlForSearchOrderById,
            data: formValues,
            dataType: "json",
            success: function (response) {
                if (response.success && response.link) {
                    var orderLink = `<br><a href="${response.link}" target="_blank"><b>Посмотреть</b></a>`
                    
                    showSuccessToast(text=response.message, link=orderLink)
                } else {
                    showDangerToast(response.message)
                }
            },
            error: function (xhr, status, error) {
                // Обработка ошибок
                if (xhr.status === 400 || xhr.status === 404) {
                    var response = JSON.parse(xhr.responseText);
                    showDangerToast(response.message);
                }
            }
        });
    });

    // Рассчет общей выручки
    $("#calculateRevenueButton").click(function (e) { 
        e.preventDefault();

        var urlForCalculateRevenue = $(this).data("url-for-calculate-revenue")
        
        $.ajax({
            type: "GET",
            url: urlForCalculateRevenue,
            dataType: "json",
            success: function (response) {
                var revenue = response.message
                var alertText = `Общий объем выручки составляет ${revenue} ₽`
                showSuccessAlert(text=alertText, time=5000)
            }
        });
        
    });

});