const spinnerBox = document.getElementById('spinner-box')
const ajaxBox = document.getElementById('ajax-box')
var message_box = document.getElementById("error_message");

$(function () {
    $('#report_submit').on('click', function () {
        $.ajax({
            type: 'GET',
            url: '/qdb/report/',
            success: function(response){
                setTimeout(()=>{
                    spinnerBox.classList.remove("not-visible")
                }, 500)
            },
            error: function(data) {
                setTimeout(()=>{
                    ajaxBox.classList.remove("not-visible")
                }, 500)
            },
        })
        message_box.style.display = "none";
    });
});