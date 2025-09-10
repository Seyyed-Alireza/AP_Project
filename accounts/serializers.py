from rest_framework import serializers
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source='userprofile.profile_picture', read_only=True)

    class Meta:
        model = User
        fields = ['profile_picture']
        

class CurrentUserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(source='*', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'userprofile']
