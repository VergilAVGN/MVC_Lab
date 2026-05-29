from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import RecipeForm, CommentForm
from .models import Recipe, Comment, Favorite
from django.contrib import messages
from .cocktail_api import fetch_cocktail_by_name
# Create your views here.
#add recipe
@login_required
def recipe_create(request):
    api_initial = {}
    if request.method == "GET" and request.GET.get("api_name"):
        mapped = fetch_cocktail_by_name(request.GET.get("api_name"))
        if mapped:
            api_initial = mapped
            messages.success(request, "Recipe loaded from TheCocktailDB. Review and save.")
        else:
            messages.error(request, "Cocktail not found in API.")
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            #image Url 
            if 'image_url' in request.POST and request.POST['image_url']:
                recipe.image_url = request.POST['image_url']
            recipe.save()
            return redirect('recipe_detail', id=recipe.id)
    else:
        form = RecipeForm(initial=api_initial)

    return render(request, 'recipes/form.html', {'form': form})

#edit recipe
@login_required
def recipe_update(request, id):
    recipe = get_object_or_404(Recipe, id=id, user=request.user)
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('recipe_detail', id=obj.id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, "recipes/form.html", {"form": form, "recipe": recipe})

#delete recipe
@login_required
def recipe_delete(request, id):
    recipe = get_object_or_404(Recipe, id=id)

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

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    comments = recipe.comments.select_related('user')
    comment_form = CommentForm()
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).exists()
    return render(request, 'recipes/detail.html', {
        'recipe': recipe,
        'comments': comments,
        'comment_form': comment_form,
        'is_favorite': is_favorite,
    })


@login_required
def favorite_toggle(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        recipe=recipe,
    )
    if not created:
        favorite.delete()
        messages.info(request, 'Removed from favorites.')
    else:
        messages.success(request, 'Added to favorites.')
    return redirect('recipe_detail', id=id)


@login_required
def comment_add(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method != 'POST':
        return redirect('recipe_detail', id=id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.recipe = recipe
        comment.save()
        messages.success(request, 'Comment added.')
    else:
        messages.error(request, 'Could not add comment.')
    return redirect('recipe_detail', id=id)


def _can_delete_comment(user, comment) -> bool:
    if not user.is_authenticated:
        return False
    if user == comment.user:
        return True
    return user.is_staff or user.is_superuser


@login_required
def comment_delete(request, id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        recipe_id=id,
    )
    if _can_delete_comment(request.user, comment):
        is_moderator = (
            (request.user.is_staff or request.user.is_superuser)
            and request.user != comment.user
        )
        comment.delete()
        if is_moderator:
            messages.info(request, 'Comment removed by moderator.')
        else:
            messages.info(request, 'Comment deleted.')
    else:
        messages.error(request, 'You cannot delete this comment.')
    return redirect('recipe_detail', id=id)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('recipe', 'recipe__user').order_by('-created_at')
    recipes = [f.recipe for f in favorites]
    return render(request, 'recipes/favorites.html', {'recipes': recipes})

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

