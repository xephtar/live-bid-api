from django.urls import path
from .views import CategoryView, ItemView, create_bid_for_item, get_bids_for_item

urlpatterns = [
    path('categories', CategoryView.as_view()),
    path('items', ItemView.as_view()),
    path('items/<str:item_uid>/create_bid', create_bid_for_item),
    path('items/<str:item_uid>/get_bids', get_bids_for_item)
]
