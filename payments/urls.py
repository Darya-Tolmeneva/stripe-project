from django.urls import path
from .views import buy_item, item_page

urlpatterns = [
    path('buy/<int:item_id>/', buy_item, name='buy-item'),
    path('item/<int:item_id>/', item_page, name='item-page'),
]
