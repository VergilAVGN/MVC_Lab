from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import RecipeForm
from .models import Recipe, Comment, Favorite


class RecipeAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='secret123',
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='secret123',
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='secret123',
            is_staff=True,
        )
        self.recipe = Recipe.objects.create(
            user=self.user,
            name='Test Martini',
            ingredients='- Gin\n- Vermouth',
            instructions='1. Stir with ice.\n2. Strain into glass.',
        )

    def test_recipe_list_pagination(self):
        for i in range(10):
            Recipe.objects.create(
                user=self.user,
                name=f'Test Recipe {i}',
                ingredients='- Ingredient\n- Ingredient',
                instructions='1. Step one.\n2. Step two.',
            )

        response = self.client.get(reverse('recipe_list'))
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(page_obj.object_list), 8)

        response = self.client.get(reverse('recipe_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 3)

    def test_recipe_create_requires_authentication(self):
        url = reverse('recipe_create')
        data = {
            'name': 'Negroni',
            'ingredients': '- Gin\n- Campari\n- Sweet vermouth',
            'instructions': '1. Stir all ingredients with ice.\n2. Serve over fresh ice.',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='author', password='secret123')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipe.objects.filter(name='Negroni').exists())

    def test_recipe_update_owner_can_edit(self):
        self.client.login(username='author', password='secret123')
        url = reverse('recipe_update', args=[self.recipe.id])
        response = self.client.post(url, {
            'name': 'Updated Martini',
            'ingredients': '- Gin\n- Vermouth\n- Orange twist',
            'instructions': '1. Stir with ice.\n2. Garnish and serve.',
        })
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.name, 'Updated Martini')

    def test_recipe_delete_requires_post(self):
        self.client.login(username='author', password='secret123')
        url = reverse('recipe_delete', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_recipe_delete_owner_and_staff(self):
        url = reverse('recipe_delete', args=[self.recipe.id])
        self.client.login(username='author', password='secret123')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('recipe_list'))
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

        recipe = Recipe.objects.create(
            user=self.user,
            name='Another',
            ingredients='- Item1\n- Item2',
            instructions='1. Do it.\n2. Finish.',
        )
        self.client.logout()
        self.client.login(username='staff', password='secret123')
        response = self.client.post(reverse('recipe_delete', args=[recipe.id]))
        self.assertRedirects(response, reverse('recipe_list'))
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_favorite_toggle_adds_and_removes_favorite(self):
        self.client.login(username='author', password='secret123')
        url = reverse('favorite_toggle', args=[self.recipe.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('recipe_detail', args=[self.recipe.id]))
        self.assertTrue(Favorite.objects.filter(user=self.user, recipe=self.recipe).exists())

        response = self.client.post(url)
        self.assertRedirects(response, reverse('recipe_detail', args=[self.recipe.id]))
        self.assertFalse(Favorite.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_comment_add_and_delete(self):
        self.client.login(username='author', password='secret123')
        add_url = reverse('comment_add', args=[self.recipe.id])
        response = self.client.post(add_url, {'text': 'Nice cocktail!'})
        self.assertRedirects(response, reverse('recipe_detail', args=[self.recipe.id]))
        comment = Comment.objects.get(recipe=self.recipe)
        self.assertEqual(comment.text, 'Nice cocktail!')
        self.assertEqual(comment.user, self.user)

        delete_url = reverse('comment_delete', args=[self.recipe.id, comment.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('recipe_detail', args=[self.recipe.id]))
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_staff_can_delete_other_users_comment(self):
        other_recipe = Recipe.objects.create(
            user=self.other_user,
            name='Other cocktail',
            ingredients='- Item\n- Item',
            instructions='1. Step one.\n2. Step two.',
        )
        comment = Comment.objects.create(
            recipe=other_recipe,
            user=self.other_user,
            text='Comment from other user',
        )
        self.client.login(username='staff', password='secret123')
        response = self.client.post(reverse('comment_delete', args=[other_recipe.id, comment.id]))
        self.assertRedirects(response, reverse('recipe_detail', args=[other_recipe.id]))
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_recipe_form_validation_rejects_bad_data(self):
        form = RecipeForm(data={
            'name': 'A',
            'ingredients': 'Gin\nVermouth',
            'instructions': 'Mix together',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('ingredients', form.errors)
        self.assertIn('instructions', form.errors)
