from rest_framework import serializers
from .models import Task

# serializers.py
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'important', 'datetime', 'datecompleted', 'user']
        read_only_fields = ['user']
