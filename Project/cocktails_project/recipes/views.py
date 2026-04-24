from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

import recipes

from .models import Recipe
# Create your views here.
#add recipe
@login_required
def recipe_create(request):
    if request.method == 'POST':
        Recipe.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            ingredients=request.POST.get('ingredients'),
            instructions=request.POST.get('instructions'),
            image=request.FILES.get('image')
        )
        return redirect('recipe_list')

    return render(request, 'recipes/form.html')
#edit recipe
@login_required
def recipe_update(request, id):
    recipe = get_object_or_404(Recipe, id=id, user=request.user)

    if request.method == 'POST':
        recipe.name = request.POST.get('name')
        recipe.ingredients = request.POST.get('ingredients')
        recipe.instructions = request.POST.get('instructions')
        if request.FILES.get('image'):
            recipe.image = request.FILES.get('image')

        if request.POST.get('remove_image'):
            recipe.image.delete()
            recipe.image = None
        recipe.save()
        return redirect('recipe_list')

    return render(request, 'recipes/form.html', {'recipe': recipe})
#delete recipe
@login_required
def recipe_delete(request, id):
    recipe = get_object_or_404(Recipe, id=id, user=request.user)

    if request.user == recipe.user or request.user.is_staff:
        recipe.delete()

    return redirect('recipe_list')

#list recipes
def recipe_list(request):
    sort = request.GET.get('sort')
    query = request.GET.get('q')

    recipes = Recipe.objects.all()
    if query:
        recipes = recipes.filter(name__icontains=query)
    if sort == 'date':
        recipes = recipes.order_by('-created_at')
    elif sort == 'name':
        recipes = recipes.order_by('name')
    elif sort == 'author':
        recipes = recipes.order_by('user__username')

    return render(request, 'recipes/list.html', {'recipes': recipes, 'query': query})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(user=request.user).order_by('-id')     
    return render(request, 'recipes/list.html', {'recipes': recipes})