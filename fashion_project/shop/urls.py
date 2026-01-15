from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login_user, name='login'),
    path('women', views.women, name='women'),
    # path('WomenShoes', views.WomenShoes, name='WomenShoes'),
    # path('HandBags', views.HandBags, name='HandBags'),
    path('men', views.men, name='men'),
    path('featured/', views.featured_products, name='featured_products'),
    path('cart', views.cart, name='cart'),
    path("add_to_cart", views.add_to_cart, name="add_to_cart"),
    path("update_cart", views.update_cart, name="update_cart"),
    path("remove_item", views.remove_item, name="remove_item"),
    # path("password_reset", views.password_reset, name="password_reset")
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="shop/password_reset_form.html"
    ),
    name="password_reset",
    ),
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(
             template_name="shop/password_reset_done.html",
         ),
         name="password_reset_done",
         ),
         path(
             "reset/<uidb64>/<token>/",
             auth_views.PasswordResetConfirmView.as_view(
                 template_name="shop/password_reset_confirm.html"
             ),
             name="password_reset_confirm",

         ),
         path("reset/done/",
              auth_views.PasswordResetCompleteView.as_view(
                  template_name="shop/password_reset_complete.html"
              ),
              name="password_reset_complete"),

        # path("mpesa/stk/<int:order_id>/", views.stk_push, name="stk_push"),
        path('mpesa/stk/<int:order_id>/', views.checkout_stk, name='stk_push'),

    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),

]

