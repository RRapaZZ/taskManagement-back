from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task
from .serializers import TaskSerializer
from datetime import datetime

# API Views for Tasks

class TaskListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return tasks for the logged-in user
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # If the datetime is provided, we process it and save it with the task
        date = self.request.data.get('date')
        time = self.request.data.get('time')
        
        if date and time:
            datetime_str = f"{date} {time}"
            datetime_value = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            # Save the task with the logged-in user as the owner and assign the datetime
            serializer.save(user=self.request.user, datetime=datetime_value)
        else:
            # Save without datetime if not provided
            serializer.save(user=self.request.user)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return tasks for the logged-in user
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # If the datetime is provided during update, process it
        date = self.request.data.get('date')
        time = self.request.data.get('time')
        
        if date and time:
            datetime_str = f"{date} {time}"
            datetime_value = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            # Save the task with the logged-in user as the owner and assign the datetime
            serializer.save(user=self.request.user, datetime=datetime_value)
        else:
            # Save without updating datetime if not provided
            serializer.save(user=self.request.user)

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
        
# API View for Creating Task with Deadline

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task_api(request):
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # Process datetime from request
            date = request.data.get('date')
            time = request.data.get('time')
            
            if date and time:
                datetime_str = f"{date} {time}"
                datetime_value = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                # Save the task with the logged-in user and datetime field
                serializer.save(user=request.user, datetime=datetime_value)
            else:
                serializer.save(user=request.user)
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom Create Task with deadline field

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id  # Associate the authenticated user
        
        # Process datetime from request
        date = data.get('date')
        time = data.get('time')
        
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            if date and time:
                datetime_str = f"{date} {time}"
                datetime_value = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                serializer.save(user=request.user, datetime=datetime_value)
            else:
                serializer.save(user=request.user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
