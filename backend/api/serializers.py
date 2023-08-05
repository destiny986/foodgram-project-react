from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import SerializerMethodField

from users.models import User

class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class UserGetSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
