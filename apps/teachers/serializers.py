from attr import attr
from rest_framework import serializers
from apps.students.models import Assignment


class StudentAssignmentSerializer(serializers.ModelSerializer):
    """
    Student Assignment serializer
    """
    class Meta:
        model = Assignment
        fields = '__all__'

    def validate(self, attrs):
        
        return super().validate(attrs)
