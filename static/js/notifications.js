$(document).ready(function () {
    function fetchNotifications() {
        $.ajax({
            url: '/notifications',
            type: 'GET',
            success: function (data) {
                const notifications = data.notifications;
                const notificationContainer = $('#notification-container');
                notificationContainer.empty();

                if (notifications.length > 0) {
                    notifications.forEach(function (notification) {
                        console.log(notification);
                        const notificationElement = `
                                <li class="dropdown-item-1 float-none p-3 mark-as-read d-flex" id="notification_${notification.id}"
                                ${notification.model_name ? `onclick="location.href='/${notification.model_name}/${notification.record_id}?tab=Notes'"` : ''}>
                                    ${!notification.read ? `<div id="notificationRead_${notification.id}" class="my-auto bg-primary rounded-circle p-1"></div>` : ''}
                                    <div class="list-item d-flex justify-content-start align-items-start notification" >
                                      <div class="list-style-detail ml-2 mr-2">
                                          <p class="m-0">
                                              ${notification.message}
                                          </p>
                                          <p class="m-0">
                                              <small class="text-secondary">
                                                  <svg xmlns="http://www.w3.org/2000/svg" class="text-secondary mr-1" width="15" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                                  </svg>
                                              ${notification.created_at}</small>
                                          </p>
                                      </div>
                                     </div>                                                
                                </li>
                            `;
                        notificationContainer.append(notificationElement);
                    });

                    $('.mark-as-read').on('click', function () {
                        const notificationId = $(this).attr('id').split('_')[1];
                        console.log(notificationId);
                        $('#notificationRead_' + notificationId).hide();
                        markNotificationAsRead(notificationId);
                    });


                } else {
                    notificationContainer.append('<p>No new notifications.</p>');
                }
                if (data.unread_notifications > 0) {
                    $('#notification_count').text(data.unread_notifications);
                }
            },
            error: function (error) {
                console.error('Error fetching notifications:');
            }
        });
    }

    function markNotificationAsRead(notificationId) {
        $.ajax({
            data: {
                csrfmiddlewaretoken: $(csrf_token).val(),
            },
            dataType: 'json',
            error: function (error) {
                console.error('Error marking notification as read:', error);
            },
            success: function (data) {
                if (data.success) {
                    const notification_count = $('#notification_count');
                    notification_count.text(parseInt(notification_count.text()) - 1);
                    if (parseInt(notification_count.text()) < 1) {
                        notification_count.hide();
                    }
                } else {
                    alert('Error marking notification as read.');
                }
            },
            type: 'POST',
            url: `/notifications/read/${notificationId}/`
        });
    }
    fetchNotifications();
});