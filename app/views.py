from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer, LoginSerializer, SignUpSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from itsdangerous import URLSafeSerializer

SECRET_KEY = "4bFw/scqIm8Hf6ifkzgzKbSZS70dEwqcvb9PKkm8/Bk="


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            # Generate JWT Token
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(f'\n\n hello \n\n')
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully. Please verify your email.",
                "user": UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerifyView(APIView):
    def get(self, request, token):
        # Decode token and activate user account.
        return Response({'message': 'Email verified!'})

class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'ops':
            return Response({'error': 'Only Ops Users can upload files'}, status=status.HTTP_403_FORBIDDEN)
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListFilesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        files = UploadedFile.objects.all()
        return Response(FileSerializer(files, many=True).data)

class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            file = UploadedFile.objects.get(id=file_id)
            if request.user.role != 'client':
                return Response({'error': 'Only Client Users can download files'}, status=status.HTTP_403_FORBIDDEN)

            # Generate a secure URL
            s = URLSafeSerializer(SECRET_KEY)
            secure_url = s.dumps({'file_id': file.id, 'user_id': request.user.id})
            return Response({'secure_url': f"http://yourdomain.com/api/files/download/{secure_url}"})

        except UploadedFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

class SecureDownloadView(APIView):
    def get(self, request, token):
        s = URLSafeSerializer(SECRET_KEY)
        try:
            data = s.loads(token)
            file = UploadedFile.objects.get(id=data['file_id'])
            if request.user.id != data['user_id']:
                return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
            # Serve file (e.g., return file URL or stream file content)
            return Response({'file_url': file.file.url})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

