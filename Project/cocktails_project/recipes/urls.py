from django.urls import path

from . import views


urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('add/', views.recipe_create, name='recipe_create'),
    path('edit/<int:id>/', views.recipe_update, name='recipe_update'),
    path('delete/<int:id>/', views.recipe_delete, name='recipe_delete'),
    path('register/', views.register, name='register'),
    path('my/', views.my_recipes, name='my_recipes'),
]