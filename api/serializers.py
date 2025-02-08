from rest_framework import serializers
from app.models import CustomUser,Recipe,IngredientName,IngredientModel,PostImage,Category,Tag,Favorite,Review, RoleRequest, Order, OrderItem, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'bio']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class IngredientNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientName
        fields = ['id', 'name']


class RecipeSerializer(serializers.ModelSerializer):
    # ingredients_used = serializers.PrimaryKeyRelatedField(queryset=IngredientName.objects.all(), many=True)
    # categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    # tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    tags = serializers.SlugRelatedField(slug_field='name', many=True, queryset=Tag.objects.all())
    categories = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all())
    ingredients_used = serializers.SlugRelatedField(slug_field='name', many=True, queryset=IngredientName.objects.all())
    author = serializers.SlugRelatedField(slug_field='username', queryset=CustomUser.objects.all())
    post_images = PostImageSerializer(many=True, read_only=True)  # Nested serializer for existing images
    uploaded_images = serializers.ListField(child=serializers.ImageField(max_length=100, allow_empty_file=False, use_url=False), write_only=True, required=False
    )
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'instructions', 'ingredients_used', 'categories', 'tags', 'post_images', 'created_at', 'updated_at', 'author', 'is_published', 'uploaded_images']
        read_only_fields = ['created_at', 'updated_at', 'is_published']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])  # Correct field name
        tags = validated_data.pop('tags', [])
        ingredients_used = validated_data.pop('ingredients_used', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.ingredients_used.set(ingredients_used)# ✅ Correct way to assign ManyToManyField
        # Save images to the PostImage model
        for image in uploaded_images:
            PostImage.objects.create(recipe=recipe, image=image)  # Create image instance

        return recipe


class IngredientModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientModel
        fields = ['id', 'name', 'recipe', 'quantity', 'unit', 'order', 'alternative_ingredient', 'alternative_ingredient_quantity', 'alternative_ingredient_unit']



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'recipe', 'rating', 'comment','created_at']
        read_only_fields = ['created_at']



class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe', 'added_at']
        read_only_fields = ['added_at']


class RoleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleRequest
        fields = ['id', 'user', 'requested_role', 'approved']
        read_only_fields = ['user', 'approved']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'order', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'updated_at','order_items']
        read_only_fields = ['created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image', 'price', 'stock','created_at']
        read_only_fields = ['created_at']
