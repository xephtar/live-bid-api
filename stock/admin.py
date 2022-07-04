from django_neomodel import admin as neo_admin
from .models import Category, Item, Bid
from django.contrib import admin as dj_admin


class CategoryAdmin(dj_admin.ModelAdmin):
    list_display = ["name"]


class ItemAdmin(dj_admin.ModelAdmin):
    list_display = ["name", "price", "belong_to"]


class BidAdmin(dj_admin.ModelAdmin):
    list_display = ["amount", "created_at"]


neo_admin.register(Category, CategoryAdmin)
neo_admin.register(Item, ItemAdmin)
neo_admin.register(Bid, BidAdmin)
