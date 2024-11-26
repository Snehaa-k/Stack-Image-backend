from django.shortcuts import render
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer,ImageSerialier)
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import CustomUser,ImageModal
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta



# Create your views here.
class RegisterationApi(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
       

        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            
            return Response(
                {"message": "User created successfully. OTP sent.", "user": user_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(APIView):
    

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found or invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, user.password):
            return Response(
                {"error": "password are not correct "}, status=status.HTTP_401_UNAUTHORIZED
            )

        

        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )    

class UploadImage(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.user)
        user = request.user
        
        try:
            user = CustomUser.objects.get(id=user.id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found or invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        image_file = request.FILES.getlist("image")
        title = request.data.getlist('title')
       
        if not image_file:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )
        

        
        for image_file, title in zip(image_file, title):  
                ImageModal.objects.create(user=user, image=image_file, title=title)
        return Response({"message": "success"}, status=status.HTTP_201_CREATED)
    

class GalleryImageGet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        try:
            gallery = ImageModal.objects.filter(user=user_id).order_by("order")
        except ImageModal.DoesNotExist:
            return Response(
                {"error": "image not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ImageSerialier(gallery, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditImage(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, id):
        user_id = request.user.id  

        try:
            
            image = ImageModal.objects.get(id=id, user=user_id)
        except ImageModal.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )

        
        new_title = request.data.get("title")
        if new_title:
            image.title = new_title

        
        if "image" in request.FILES:
            image.image = request.FILES["image"]
        print(image)

        image.save()  

        return Response(
            {"message": "Image updated successfully", "title": image.title},
            status=status.HTTP_200_OK,
        )
    

class Imagedelete(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
        user = request.user

        try:
            image = ImageModal.objects.get(id=id, user=user)
            image.delete()
            return Response(
                {"message": "image deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ImageModal.DoesNotExist:
            return Response(
                {"error": "image  not found or unauthorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

class UpdateImageOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_id = request.user.id
        order_data = request.data.get("order", [])  
        if not isinstance(order_data, list):
            return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

        
        for index, image_id in enumerate(order_data):
            try:
                image = ImageModal.objects.get(id=image_id, user=user_id)
                image.order = index
                image.save()
            except ImageModal.DoesNotExist:
                return Response({"error": f"Image with ID {image_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Order updated successfully"}, status=status.HTTP_200_OK)
    
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

       
        user.create_reset_token()

        reset_url = f"https://http://localhost:5173/password-reset-confirm/{user.id}/{user.reset_token}"
        
        send_mail(
                        subject='PassWord Reset',
                        message=f'Click the link to reset your password: {reset_url} ',
                                
                        from_email="worldmagical491@gmail.com",
                        recipient_list=[email],
                        fail_silently=False,
                    )
       

        return Response({"message": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    def post(self, request):
        user_id = request.data.get('id')
        password = request.data.get("password")
        token = request.data.get('token')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.reset_token != token:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.token_expiration < timezone.now():
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)

        user.reset_token = None  
        user.token_expiration = None 
        user.save()

       
        return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)