from django.contrib import admin
from.models import Recipe,Tag,Favorite,PostImage,Review,Category,IngredientName,IngredientModel,CustomUser

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(PostImage)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(IngredientName)
admin.site.register(CustomUser)
admin.site.register(IngredientModel)
