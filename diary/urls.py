from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile-setup/', views.profile_setup, name='profile_setup'),
    path('search-products/', views.search_products, name='search_products'),
    path('add-entry-api/', views.add_entry_api, name='add_entry_api'),
    path('add-product/', views.add_product, name='add_product'),
    path('update-entry/<int:entry_id>/', views.update_entry, name='update_entry'),
    path('delete-entry/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('meal/<str:meal>/', views.meal_detail, name='meal_detail'),
    path('profile/', views.profile_detail, name='profile_detail'),
    path('delete-meal-item/<int:item_id>/', views.delete_meal_item, name='delete_meal_item'),
]
