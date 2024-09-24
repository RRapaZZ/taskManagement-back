from django.contrib import admin
from django.urls import path
from tasks import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),


    # Rutas para la API
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/signin/', views.api_signin, name='api_signin'),
    path('api/tasks/', views.TaskListCreate.as_view(), name='task-list-create'),
    path('api/tasks/<int:pk>/', views.TaskDetail.as_view(), name='task-detail'),
    path('api/create_task/', views.create_task_api, name='create_task_api'),

    # Rutas para JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
