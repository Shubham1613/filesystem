from django.urls import path
from .views import (
    LoginView, 
    SignUpView, 
    EmailVerifyView, 
    UploadFileView, 
    ListFilesView, 
    DownloadFileView, 
    SecureDownloadView
)

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    # path('email-verify/<str:token>/', EmailVerifyView.as_view()),
    path('upload/', UploadFileView.as_view()),
    path('files/', ListFilesView.as_view()),
    path('files/download/<int:file_id>/', DownloadFileView.as_view()),
    path('files/download-secure/<str:token>/', SecureDownloadView.as_view()),
]

