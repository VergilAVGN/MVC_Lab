from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

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
            instructions=request.POST.get('instructions')
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
        recipe.save()
        return redirect('recipe_list')

    return render(request, 'recipes/form.html', {'recipe': recipe})
#delete recipe
@login_required
def recipe_delete(request, id):
    recipe = get_object_or_404(Recipe, id=id, user=request.user)
    recipe.delete()
    return redirect('recipe_list')

#list recipes
@login_required
def recipe_list(request):
    if request.user.is_authenticated:
        recipes = Recipe.objects.filter(user=request.user)
    else:
        recipes = Recipe.objects.none()

    return render(request, 'recipes/list.html', {'recipes': recipes})