from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import FoodEntry
from django import forms
from .forms import FoodEntryForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import RegisterForm
from .models import Profile
from .forms import ProfileForm
from django.http import JsonResponse, Http404
from .models import Product
from .forms import ProductForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models.functions import Lower
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json
from .models import WeightLog
from .forms import WeightForm


@login_required
def add_entry_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        entries = data.get('entries', [])
        meal = data.get('meal', 'breakfast')
        entry_date = data.get('date', None)

        if entry_date:
            try:
                entry_date = date.fromisoformat(entry_date)
            except (ValueError, TypeError):
                entry_date = date.today()
        else:
            entry_date = date.today()

        for item in entries:
            product = Product.objects.filter(id=item['product_id']).first()

            if product:
                FoodEntry.objects.create(
                    user=request.user,
                    product=product,
                    grams=item['grams'],
                    meal_type=meal,
                    date=entry_date
                )

        return JsonResponse({'success': True})


@login_required
@require_http_methods(["PATCH", "POST"])
def update_entry(request, entry_id):
    try:
        entry = FoodEntry.objects.get(id=entry_id, user=request.user)
    except FoodEntry.DoesNotExist:
        return JsonResponse({'error': 'Запись не найдена'}, status=404)

    if request.method in ('PATCH', 'POST'):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный JSON'}, status=400)

        new_grams = data.get('grams')
        if new_grams is not None:
            try:
                new_grams = float(new_grams)
                if new_grams <= 0:
                    return JsonResponse({'error': 'Граммы должны быть положительными'}, status=400)
                entry.grams = new_grams
                entry.save()
                return JsonResponse({'success': True})
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Некорректное значение граммов'}, status=400)
        else:
            return JsonResponse({'error': 'Поле grams обязательно'}, status=400)

    return JsonResponse({'error': 'Метод не разрешён'}, status=405)


@login_required
@require_http_methods(["DELETE"])
def delete_entry(request, entry_id):
    try:
        entry = FoodEntry.objects.get(id=entry_id, user=request.user)
    except FoodEntry.DoesNotExist:
        return JsonResponse({'error': 'Запись не найдена'}, status=404)

    entry.delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def delete_meal_item(request, item_id):
    entry = get_object_or_404(FoodEntry, id=item_id, user=request.user)
    entry.delete()
    return redirect('/')

@login_required
def add_product(request):
    form = ProductForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.is_custom = True
            product.save()

            grams = form.cleaned_data.get('grams')
            meal = request.GET.get('meal')  # из URL, который мы передали
            entry_date_str = request.GET.get('date')
            if grams and meal:
                try:
                    entry_date = date.fromisoformat(entry_date_str) if entry_date_str else date.today()
                except (ValueError, TypeError):
                    entry_date = date.today()

                FoodEntry.objects.create(
                    user=request.user,
                    product=product,
                    grams=grams,
                    meal_type=meal,
                    date=entry_date
                )
            return redirect(request.GET.get('next', '/add-product/'))

    return render(request, 'diary/add_product.html', {
        'form': form
    })


def search_products(request):
    query = request.GET.get('q', '').strip().lower()

    if not query:
        return JsonResponse([], safe=False)

    all_products = Product.objects.all()

    filtered = []

    for p in all_products:
        if query in p.name.lower():
            filtered.append(p)

    filtered = filtered[:10]

    data = [
        {
            'id': p.id,
            'name': p.name,
            'calories': p.calories,
            'proteins': p.proteins,
            'fats': p.fats,
            'carbs': p.carbs,
        }
        for p in filtered
    ]

    return JsonResponse(data, safe=False)


def profile_setup(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.daily_calories_goal = profile.calculate_calories()
            profile.save()
            return redirect('/')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'diary/profile_setup.html', {
        'form': form
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/profile-setup/')
    else:
        form = RegisterForm()

    return render(request, 'diary/register.html', {'form': form})


@login_required
def index(request):
    # --- Обработка даты ---
    selected_date = request.GET.get('date')
    try:
        if selected_date:
            selected_date = date.fromisoformat(selected_date)
        else:
            selected_date = date.today()
    except:
        selected_date = date.today()

    # --- Записи о еде ---
    entries = FoodEntry.objects.filter(
        user=request.user,
        date=selected_date
    ).select_related('product')

    meals_raw = {'breakfast': [], 'lunch': [], 'dinner': [], 'snack': []}
    total_calories = total_proteins = total_fats = total_carbs = 0

    for entry in entries:
        factor = entry.grams / 100
        total_calories += entry.product.calories * factor
        total_proteins += entry.product.proteins * factor
        total_fats += entry.product.fats * factor
        total_carbs += entry.product.carbs * factor
        meals_raw[entry.meal_type].append(entry)

    # Преобразование для шаблона
    meals = {'breakfast': [], 'lunch': [], 'dinner': [], 'snack': []}
    for meal_type, items in meals_raw.items():
        for item in items:
            factor = item.grams / 100
            meals[meal_type].append({
                'id': item.id,
                'product': item.product,
                'name': item.product.name,
                'grams': item.grams,
                'calories': round(item.product.calories * factor, 1),
                'proteins': round(item.product.proteins * factor, 1),
                'fats': round(item.product.fats * factor, 1),
                'carbs': round(item.product.carbs * factor, 1),
            })

    # Калории по приёмам
    breakfast_calories = sum(m['calories'] for m in meals['breakfast'])
    lunch_calories = sum(m['calories'] for m in meals['lunch'])
    dinner_calories = sum(m['calories'] for m in meals['dinner'])
    snack_calories = sum(m['calories'] for m in meals['snack'])

    # Профиль и цели
    calories_goal = 2000
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            calories_goal = profile.daily_calories_goal
        except:
            pass

    # Цели БЖУ
    if calories_goal > 0:
        protein_goal = round(calories_goal * 0.3 / 4)
        fat_goal = round(calories_goal * 0.25 / 9)
        carb_goal = round(calories_goal * 0.45 / 4)
    else:
        protein_goal, fat_goal, carb_goal = 150, 65, 250

    protein_offset = 213.6 * (1 - total_proteins / protein_goal) if protein_goal else 213.6
    fat_offset = 213.6 * (1 - total_fats / fat_goal) if fat_goal else 213.6
    carb_offset = 213.6 * (1 - total_carbs / carb_goal) if carb_goal else 213.6

    calories_percent = (total_calories / calories_goal) * 100 if calories_goal else 0
    calories_percent = max(0, min(calories_percent, 100))

    prev_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)

    context = {
        'meals': meals,
        'date': selected_date,
        'date_str': selected_date.isoformat(),
        'prev_day': prev_day.isoformat(),
        'next_day': next_day.isoformat(),
        'total_calories': round(total_calories, 1),
        'total_proteins': round(total_proteins, 1),
        'total_fats': round(total_fats, 1),
        'total_carbs': round(total_carbs, 1),
        'calories_goal': calories_goal,
        'calories_percent': round(calories_percent, 1),
        'breakfast_calories': round(breakfast_calories, 1),
        'lunch_calories': round(lunch_calories, 1),
        'dinner_calories': round(dinner_calories, 1),
        'snack_calories': round(snack_calories, 1),
        'protein_goal': protein_goal,
        'fat_goal': fat_goal,
        'carb_goal': carb_goal,
        'protein_offset': round(protein_offset, 1),
        'fat_offset': round(fat_offset, 1),
        'carb_offset': round(carb_offset, 1),
    }

    if not hasattr(request.user, 'profile') or not request.user.profile.height:
        return redirect('/profile-setup/')
    return render(request, 'diary/index.html', context)

@login_required
def add_food(request):
    selected_date = request.GET.get('date')
    meal = request.GET.get('meal', 'breakfast')

    try:
        selected_date = date.fromisoformat(selected_date)
    except:
        selected_date = date.today()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        grams = request.POST.get('grams')

        product = Product.objects.get(id=product_id)

        FoodEntry.objects.create(
            user=request.user,
            product=product,
            grams=grams,
            meal_type=meal,
            date=selected_date
        )

        return redirect(f"/?date={selected_date.isoformat()}")

    return render(request, 'diary/add_food.html', {
        'date': selected_date,
        'meal': meal
    })


@login_required
def meal_detail(request, meal):
    # Проверка допустимых типов приёма пищи
    valid_meals = ['breakfast', 'lunch', 'dinner', 'snack']
    if meal not in valid_meals:
        raise Http404("Неизвестный тип приёма пищи")

    # Получение даты
    selected_date = request.GET.get('date')
    try:
        if selected_date:
            selected_date = date.fromisoformat(selected_date)
        else:
            selected_date = date.today()
    except (ValueError, TypeError):
        selected_date = date.today()

    entries = FoodEntry.objects.filter(
        user=request.user,
        meal_type=meal,
        date=selected_date
    ).select_related('product')

    meal_names = {
        'breakfast': 'Завтрак',
        'lunch': 'Обед',
        'dinner': 'Ужин',
        'snack': 'Перекус'
    }

    context = {
        'meal': meal,
        'meal_name': meal_names[meal],
        'date': selected_date,
        'date_str': selected_date.isoformat(),
        'entries': entries,
    }
    return render(request, 'diary/meal_detail.html', context)

@login_required
def profile_detail(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        # --- Если в POST есть 'height' — значит, редактируют профиль ---
        if 'height' in request.POST:
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                # Сохраняем профиль
                profile = form.save(commit=False)
                profile.daily_calories_goal = profile.calculate_calories()
                profile.save()
                # Если в форме был вес, создаём запись в истории (всегда, когда меняли профиль)
                weight_from_form = form.cleaned_data.get('weight')
                if weight_from_form is not None:
                    WeightLog.objects.create(
                        user=request.user,
                        weight=weight_from_form,
                        date=date.today()
                    )
                return redirect('profile_detail')
            else:
                weight_form = WeightForm()  # если форма невалидна, покажем форму веса
        # --- Иначе пробуем форму веса (должен быть 'weight') ---
        elif 'weight' in request.POST:
            weight_form = WeightForm(request.POST)
            if weight_form.is_valid():
                weight = weight_form.cleaned_data['weight']
                log_date = weight_form.cleaned_data['date'] or date.today()
                WeightLog.objects.create(user=request.user, weight=weight, date=log_date)
                # Обновляем вес в профиле
                profile.weight = weight
                profile.save()
                return redirect('profile_detail')
            else:
                form = ProfileForm(instance=profile)
        else:
            # На всякий случай – отобразим обе формы заново
            form = ProfileForm(instance=profile)
            weight_form = WeightForm()
    else:
        form = ProfileForm(instance=profile)
        weight_form = WeightForm()

    # Данные для графика
    logs = WeightLog.objects.filter(
        user=request.user,
        date__gte=date.today() - timedelta(days=90)
    ).order_by('date')
    weights_data = [{'date': log.date.strftime('%d.%m.%Y'), 'weight': log.weight} for log in logs]

    return render(request, 'diary/profile_detail.html', {
        'form': form,
        'profile': profile,
        'weight_form': weight_form,
        'weights_data': json.dumps(weights_data),
    })