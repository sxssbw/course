from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FoodEntry, Product, MealType, Profile
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'

class ProductForm(forms.ModelForm):
    grams = forms.FloatField(
        required=False,
        label='Граммы (необязательно)',
        min_value=0.1
    )

    class Meta:
        model = Product
        fields = ['name', 'calories', 'proteins', 'fats', 'carbs']
        labels = {
            'name': 'Название продукта',
            'calories': 'Калории (на 100 г)',
            'proteins': 'Белки (на 100 г)',
            'fats': 'Жиры (на 100 г)',
            'carbs': 'Углеводы (на 100 г)',
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
    
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'


class FoodEntryForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Продукт"
    )
    grams = forms.FloatField(label="Граммы")
    meal_type = forms.ChoiceField(
        choices=MealType.choices,
        label="Приём пищи"
    )

    class Meta:
        model = FoodEntry
        fields = ['product', 'grams']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['height', 'weight', 'age', 'gender', 'goal']
        labels = {
            'height': 'Рост (см)',
            'weight': 'Вес (кг)',
            'age': 'Возраст',
            'gender': 'Пол',
            'goal': 'Цель',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем все поля обязательными (кроме, возможно, goal)
        for field in ['height', 'weight', 'age', 'gender']:
            self.fields[field].required = True

class WeightForm(forms.Form):
    weight = forms.FloatField(
        label='Вес (кг)',
        min_value=1,
        max_value=500,
        widget=forms.NumberInput(attrs={'placeholder': 'Ваш вес', 'step': '0.1'})
    )
    date = forms.DateField(
        required=False,
        label='Дата измерения',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Сегодня'})
    )       