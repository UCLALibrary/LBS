console.log('hello world')

const spinnerBox = document.getElementById('spinner-box')
const errorBox = document.getElementById('error-box')

//console.log(spinnerBox)

$(function () {
    $('#report_submit').on('click', function () {
        $.ajax({
            type: 'GET',
            url: '/qdb/report/',
            success: function(response){
                console.log('hello world2')
                setTimeout(()=>{
                    spinnerBox.classList.remove("not-visible")
                    console.log('response', response)
                }, 500)
            },
            error: function(error){
                console.log('hello world3')
                console.log(error.status)
                errorBox.classList.remove("not-visible")
            }
        })

    });
});