from django.urls import path
from .views import ItemListView, ItemDetailView, CartView, create_checkout_session, success_view

urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
    path('buy/', create_checkout_session, name='create_checkout_session'),
    path('item/<uuid:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('success/', success_view,  name='success'),
]
