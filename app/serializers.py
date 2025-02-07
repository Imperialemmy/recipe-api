from djoser.serializers import UserCreateSerializer



class CustomUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name','password']






# 'user_create': 'djoser.serializers.UserCreateSerializer',