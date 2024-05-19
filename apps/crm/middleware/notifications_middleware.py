# myapp/middleware.py
from apps.crm.models import Notification


class UnreadNotificationsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.unread_notifications_count = Notification.objects.filter(user=request.user, read=False).count()
        else:
            request.unread_notifications_count = 0
        response = self.get_response(request)

        print("notifications count:", request.unread_notifications_count)

        return response
