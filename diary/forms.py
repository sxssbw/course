from django import forms
from .models import FoodEntry, Product, MealType
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'calories', 'proteins', 'fats', 'carbs']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class FoodEntryForm(forms.ModelForm):
    class Meta:
        model = FoodEntry
        fields = ['product', 'grams']

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Продукт"
    )

    grams = forms.FloatField(label="Граммы")

    meal_type = forms.ChoiceField(
        choices=MealType.choices,
        label="Приём пищи"
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['height', 'weight', 'age', 'gender', 'goal']