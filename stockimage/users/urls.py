from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterationApi.as_view(), name="register"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("imageupload/", views.UploadImage.as_view(), name="imageupload"),
    path("imageview/", views.GalleryImageGet.as_view(), name="imageview"),
    path("imagedit/<int:id>/", views.EditImage.as_view(), name="editimage"),
    path("deleteimg/<int:id>/", views.Imagedelete.as_view(), name="delete"),
    path("updateorder/", views.UpdateImageOrderView.as_view(), name="updateorder"),
    path("forgot-password/", views.PasswordResetRequestView.as_view(), name="forgot_password"),
    path("password-reset/", views.PasswordResetConfirmView.as_view(), name="reset_password"),

   
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
