from django.contrib import admin
from .models import Profile, Product, FoodEntry, WeightLog

admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(FoodEntry)
admin.site.register(WeightLog)