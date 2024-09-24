from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from .serializers import TaskSerializer
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from rest_framework_simplejwt.tokens import RefreshToken

# API Views for Tasks

class TaskListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

# API View for User Signup

@api_view(['POST'])
def api_signup(request):
    if request.method == 'POST':
        if request.data['password1'] == request.data['password2']:
            try:
                user = User.objects.create_user(
                    request.data['username'], password=request.data['password1'])
                user.save()
                login(request, user)
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Passwords did not match."}, status=status.HTTP_400_BAD_REQUEST)

# API View for User Signin

@api_view(['POST'])
def api_signin(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.data['username'], password=request.data['password'])
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'token': str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_api(request):
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def create_task(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id  # Asociar el usuario autenticado
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Authentication and Task Management Views (for the Web UI)


