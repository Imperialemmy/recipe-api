from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('chef', 'Chef'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True, null=True)  # Allow empty bio
    image = models.ImageField(upload_to='images/', blank=True, null=True)  # Allow empty image

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Avoids conflict with Django's default User model
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Avoids conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

    class Meta:
        swappable = 'AUTH_USER_MODEL'



class RoleRequest(models.Model):
    ROLE_CHOICES = [
        ('chef', 'Chef'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    requested_role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} requested {self.requested_role}"



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name



class IngredientName(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True, null=True, default='')
    instructions = models.TextField(max_length=255, blank=True, null=True, default='')
    ingredients_used = models.ManyToManyField(IngredientName,related_name='recipes')
    categories = models.ForeignKey(Category, related_name='recipes',on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipes')
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, null=True)  # Add slug field and allow it to be blank

    def __str__(self):
        return self.title




class IngredientModel(models.Model):
    name = models.ForeignKey(IngredientName, on_delete=models.CASCADE, related_name='ingredient_model_set')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_model_set')
    quantity = models.CharField(max_length=50, blank=True, null=True)  # Could be CharField or DecimalField
    unit = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True)
    alternative_ingredient = models.ForeignKey(IngredientName, on_delete=models.CASCADE, related_name='alternative_ingredient_model_set',null=True, blank=True)
    alternative_ingredient_quantity = models.CharField(max_length=50, blank=True, null=True)
    alternative_ingredient_unit = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'recipe')  # Prevent duplicate ingredients in a recipe

    def __str__(self):
        return f"{self.name.name} in {self.recipe.title}"



class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()  # Or a choices field for specific ratings
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.recipe.title}"




class PostImage(models.Model):  # You'll need to define the fields for this model
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='post_images', blank=True, null=True)
    image = models.ImageField(upload_to='post_images/',default = '', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.recipe.title}"



class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorites')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe') # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.title}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  # Number of items available
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in order {self.order.id}"