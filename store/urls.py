from django.urls import path, include
from . import views

urlpatterns = [
    #Leave tas empty string for base url
    path('',views.store, name="store"),
    path('cart/',views.cart, name="cart"),
    path('checkout/',views.checkout, name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    # path('update_wallet/', views.update_wallet, name='update_wallet'),
]