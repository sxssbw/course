from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_food, name='add_food'),
    path('register/', views.register, name='register'),
    path('profile-setup/', views.profile_setup, name='profile_setup'),
    path('search-products/', views.search_products, name='search_products'),
    path('add-entry-api/', views.add_entry_api),
    path('add-product/', views.add_product, name='add_product'),
]