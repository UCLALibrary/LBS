const spinnerBox = document.getElementById('spinner-box')
const longBox = document.getElementById('long-box')
var message_box = document.getElementById("error_message");

const form = document.getElementById('p-form')

const unit = document.getElementById('id_unit')
const year = document.getElementById('id_year')
const month = document.getElementById('id_month')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

const url = ""

$(function () {
    form.addEventListener('submit', e=>{
        // close any old messages on new submissioms
        $(".alert").alert('close');

        // start spinner on submissiom
        spinnerBox.classList.remove("not-visible");

        // prevent the default submission of the form
        e.preventDefault();

        // collect the form's data
        const formData = new FormData()
        formData.append('csrfmiddlewaretoken', csrf[0].value)
        formData.append('unit', unit.value)
        formData.append('year', year.value)
        formData.append('month', month.value)

        // display "long wait" warning if All units was specified
        var unit_selected = $("#id_unit option:selected").text();
        if (unit_selected == 'All units'){
            longBox.classList.remove("not-visible");
        }

        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            success: function(data){
                success = data.success;

                // turn off spinner and any "long wait" warning
                spinnerBox.classList.add("not-visible");
                var unit_selected = $("#id_unit option:selected").text();
                if (unit_selected == 'All units'){
                    longBox.classList.add("not-visible");
                }

                // pass any messages to js in form.html
                update_messages(data.messages);
            },
            error: function(data) {
                // turn off spinner and any "long wait" warning
                spinnerBox.classList.add("not-visible");
                var unit_selected = $("#id_unit option:selected").text();
                if (unit_selected == 'All units'){
                    longBox.classList.add("not-visible");
                }
                // display ajax error
                $("#ajax-box").append("<div class='alert alert-danger alert-dismissible fade show' role='alert'><button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button><center>AJAX Error: no report could be generated.<br>-----<br>Please report this to the DIIT Help Desk:<br><a href='https://jira.library.ucla.edu/servicedesk/customer/portals'>UCLA Library Service Portal</a></center></div>");
            },
            cache: false,
            contentType: false,
            processData: false
        })
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
