from django.urls import path

from .views import CareerGuideView

urlpatterns = [path("guide/", CareerGuideView.as_view())]
