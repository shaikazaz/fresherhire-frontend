from django.urls import path

from .views import (
    ActivatePlanView,
    CreateRazorpayOrderView,
    CurrentPlanView,
    PlanListView,
    VerifyRazorpayPaymentView,
)

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="billing-plans"),
    path("current/", CurrentPlanView.as_view(), name="billing-current"),
    path("activate/", ActivatePlanView.as_view(), name="billing-activate"),
    path(
        "razorpay/create-order/",
        CreateRazorpayOrderView.as_view(),
        name="razorpay-create-order",
    ),
    path(
        "razorpay/verify/",
        VerifyRazorpayPaymentView.as_view(),
        name="razorpay-verify",
    ),
]