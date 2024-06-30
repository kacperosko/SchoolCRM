function watchRecord(recordId, modelName) {
    let mode
    if ($('#watch-button').attr('watching-record') === 'following') {
        mode = 'unfollow'
    } else {
        mode = 'follow'
    }

    $.ajax({
        url: `/crm_api/watch/${mode}/${modelName}/${recordId}/`,
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $(csrf_token).val(),
        },
        dataType: 'json',
        success: function (data) {
            if (data.status) {
                if (mode === 'follow') {
                    data.message = "Obserwujesz ten rekord"
                    handleResponse(data);
                    const watchButton = $('#watch-button');
                    const watchIcon = $('#watch_icon');

                    $('#watch-button').attr('data-content', 'Obserwujesz ten rekord');
                    $('#watch-button').attr('watching-record', 'following');
                    $('#watch_icon').attr('stroke-width', 2.5);
                    $('#watch_icon').addClass('text-primary');
                }else {
                    data.message = "Nie obserwujesz już tego rekordu"
                    handleResponse(data);
                    const watchButton = $('#watch-button');
                    const watchIcon = $('#watch_icon');

                    $('#watch-button').attr('data-content', 'Chcesz obserwować ten rekord?');
                    $('#watch-button').attr('watching-record', 'notFollowing');
                    $('#watch_icon').attr('stroke-width', 1.5);
                    $('#watch_icon').removeClass('text-primary');
                }

            } else {
                alert('Error marking notification as read.');
            }
        },
        error: function (error) {
            console.error('Error marking notification as read:', error);
        }
    });
}