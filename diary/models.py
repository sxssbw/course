from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    GOAL_CHOICES = [
        ('lose', 'Похудение'),
        ('maintain', 'Поддержание'),
        ('gain', 'Набор массы'),
    ]

    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # height = models.FloatField()
    # weight = models.FloatField()
    # age = models.IntegerField()
    # gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    # goal = models.CharField(max_length=10, choices=GOAL_CHOICES)

    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, null=True, blank=True)

    daily_calories_goal = models.FloatField(default=2000)

    def calculate_calories(self):
        if self.gender == 'male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        calories = bmr * 1.4

        if self.goal == 'lose':
            calories -= 400
        elif self.goal == 'gain':
            calories += 300

        return round(calories)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    proteins = models.FloatField()
    fats = models.FloatField()
    carbs = models.FloatField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_custom = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class MealType(models.TextChoices):
    BREAKFAST = 'breakfast', 'Завтрак'
    LUNCH = 'lunch', 'Обед'
    DINNER = 'dinner', 'Ужин'
    SNACK = 'snack', 'Перекус'


class FoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    grams = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.product.name} ({self.grams} г)"