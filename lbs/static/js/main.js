const spinnerBox = document.getElementById('spinner-box')

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
        })

    });
});