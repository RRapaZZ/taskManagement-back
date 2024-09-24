from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'important', 'datecompleted', 'user']
        read_only_fields = ['user']  # Asegúrate de que el campo user sea de solo lectura
