from rest_framework import serializers
from .models import CustomUser ,ImageModal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "password", "username", "phonenumber"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser.objects.create_user(**validated_data)  
        
        if password is not None:
            user.set_password(password)  
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)


class ImageSerialier(serializers.ModelSerializer):
    class Meta:
        model = ImageModal
        fields = ["id", "title", "image"]
