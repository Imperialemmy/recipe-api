from django.urls import path, include
from rest_framework import routers
from api import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'all_recipes', views.RecipeViewSet, basename='recipes')#To view all the recipes
router.register(r'all_ingredients', views.IngredientNameViewSet, basename='ingredients')#To view all the ingredients
router.register(r'users', views.UserViewSet, basename='users')#To view all the users
router.register(r'all_tags', views.TagViewSet, basename='Tags')#To view all the tags
router.register(r'all_categories', views.CategoryViewSet, basename='categories')#To view all the categories
router.register(r'my_favourites', views.FavoriteViewSet, basename='favourites')#To view all your favourites
router.register(r'role-requests', views.RoleRequestViewSet, basename='role-requests')
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'product_categories', views.ProductCategoriesViewSet)


# Nested Routers (Corrected)

ingredients_model_router = routers.NestedSimpleRouter(router, r'all_recipes', lookup='recipe')  # Use a distinct lookup name
ingredients_model_router.register(r'ingredients_model', views.IngredientModelViewSet, basename='recipe_ingredients_model')

reviews_router = routers.NestedSimpleRouter(router, r'all_recipes', lookup='recipe')  # Use a distinct lookup name
reviews_router.register(r'reviews', views.ReviewViewSet, basename='recipe_reviews')


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(ingredients_model_router.urls)),
    path(r'', include(reviews_router.urls)),
    path('recipe/by-tag/', views.RecipesByTagView.as_view(), name='recipes-by-tags'),# To view recipes by their tags
    path('', include(router.urls)),
]