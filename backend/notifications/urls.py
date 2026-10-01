from django.urls import path
from .views import NotificationListView,UnreadCountView,MarkReadView,MarkAllReadView
urlpatterns=[path("notifications/",NotificationListView.as_view()),path("notifications/unread-count/",UnreadCountView.as_view()),path("notifications/<int:pk>/read/",MarkReadView.as_view()),path("notifications/read-all/",MarkAllReadView.as_view())]
