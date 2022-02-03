const spinnerBox = document.getElementById('spinner-box')
const longBox = document.getElementById('long-box')
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
                    var unit_selected = $("#id_unit").val();
                    if (unit_selected == 28){
                        longBox.classList.remove("not-visible");
                    }

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
// move the "All units" option to the top of the select
$(document).ready( function () {
    $(this).find('[value="28"]').remove();
    $('#id_unit').prepend(`<option value="28" selected>All units</option>`);
});
