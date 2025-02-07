from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, RecipeSerializer, IngredientNameSerializer, IngredientModelSerializer, PostImageSerializer, CategorySerializer, TagSerializer, FavoriteSerializer, ReviewSerializer, RoleRequestSerializer
from app.models import CustomUser, Recipe, IngredientName, IngredientModel, PostImage, Category, Tag, Favorite, Review, RoleRequest
from rest_framework import viewsets, status,permissions,generics,filters,parsers
from django_filters.rest_framework import DjangoFilterBackend,OrderingFilter
from rest_framework.permissions import BasePermission
from .permissions import IsAdminUser, IsChefOrAdmin
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 3  # Default items per page
    page_size_query_param = 'page_size'  # Allows users to specify page size
    max_page_size = 6  # Limits max items per page



class IsRecipeAuthorOrAdmin(BasePermission):
    """
    Allows recipe authors and admins to modify recipes.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:  # SAFE_METHODS = ('GET', 'OPTIONS', 'HEAD')
            return True

        # Write permissions are only allowed to the author of the recipe, or admin
        return obj.author == request.user or request.user.role == 'admin' # Assuming you have a role field in the user model


class UserViewSet(viewsets.ModelViewSet):#To view all users
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class TagViewSet(viewsets.ModelViewSet):#To view all tags
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        """Assign different permissions based on actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return [IsChefOrAdmin()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return [permissions.AllowAny()]  # Anyone can view

class RecipesByTagView(ListAPIView):# To filter recipes based on tags
    serializer_class = RecipeSerializer

    def get_queryset(self):
        tags = self.request.query_params.getlist('tags')  # Get tags as a list
        if tags:
            return Recipe.objects.filter(tags__id__in=tags).distinct()
        return Recipe.objects.all()  # If no tag is provided, return all recipes



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """Assign different permissions based on actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return [IsChefOrAdmin()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return [permissions.AllowAny()]  # Anyone can view


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    filterset_fields = {
        'categories': ['exact'],  # Exact match for categories
        'tags': ['exact'],  # Exact match for tags
        'ingredients_used': ['exact'],  # Exact match for ingredients
    }
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'rating']
    pagination_class = CustomPageNumberPagination
    # parser_classes = (parsers.MultiPartParser,)

    def get_permissions(self):
        if self.action in ['create']:  # Chef can only create
            return [IsChefOrAdmin()]
        elif self.action in ['update', 'partial_update']:  # Chef can update only his recipes
            return [IsRecipeAuthorOrAdmin()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return [permissions.AllowAny()]  # Anyone can view

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_recipes(self, request):
        """Retrieve recipes created by the logged-in user"""
        recipes = Recipe.objects.filter(author=request.user)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)



class IngredientNameViewSet(viewsets.ModelViewSet):
    queryset = IngredientName.objects.all()
    serializer_class = IngredientNameSerializer

    def get_permissions(self):
        """Assign different permissions based on actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return [IsChefOrAdmin()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        return [permissions.AllowAny()]  # Anyone can view


class IngredientModelViewSet(viewsets.ModelViewSet): #api/recipe/recipe_pk/ingredients_model
    serializer_class = IngredientModelSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        recipe_pk = self.kwargs['recipe_pk']  # Get recipe_pk from URL
        return IngredientModel.objects.filter(recipe_id=recipe_pk)



class ReviewViewSet(viewsets.ModelViewSet): #api/recipe/recipe_pk/reviews
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Review.objects.filter(recipe=self.kwargs['recipe_pk'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe_pk = self.kwargs['recipe_pk']

        try:
            recipe = Recipe.objects.get(pk=recipe_pk)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

        # serializer.save(recipe=recipe, user=request.user)
        serializer.save(recipe=recipe)#Without user auth
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user).distinct()


class RoleRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RoleRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Users see their own requests; admins see all requests"""
        if self.request.user.role == 'admin':
            return RoleRequest.objects.all()
        return RoleRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure the request is created for the logged-in user"""
        if RoleRequest.objects.filter(user=self.request.user).exists():
            return Response({"error": "You already have a pending request."}, status=400)
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Allow admins to approve role requests"""
        try:
            role_request = RoleRequest.objects.get(pk=pk, approved=False)
            role_request.approved = True
            role_request.user.role = role_request.requested_role  # Update user role
            role_request.user.save()
            role_request.save()
            return Response({"success": f"{role_request.user.username} is now a {role_request.requested_role}."})
        except RoleRequest.DoesNotExist:
            return Response({"error": "Invalid request."}, status=400)



class PostImageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PostImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


