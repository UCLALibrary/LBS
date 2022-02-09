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
                    var unit_selected = $("#id_unit option:selected").text();
                    if (unit_selected == 'All units'){
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
    const optionText = 'All units';
    const $unitSelect = document.querySelector('#id_unit');
    const $unitOptions = Array.from($unitSelect.options);
    const optionToSelect = $unitOptions.find(item => item.text === optionText);
    optionToSelect.remove();
    optionToSelect.selected = true;
    $('#id_unit').prepend(optionToSelect);
});
