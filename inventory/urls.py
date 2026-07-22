from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("login/", auth_views.LoginView.as_view(
        template_name="inventory/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("compatibility/", views.compatibility_check, name="compatibility_check"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/<int:product_id>/sell/", views.sell_product, name="sell_product"),
]
