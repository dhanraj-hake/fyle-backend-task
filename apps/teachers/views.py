from rest_framework import generics, status
from rest_framework.response import Response

from apps.teachers.models import Teacher

from apps.students.models import Assignment, Student
from .serializers import StudentAssignmentSerializer

import json

from apps.internal.models import User

class AssignmentsView(generics.ListCreateAPIView, generics.UpdateAPIView):
    serializer_class = StudentAssignmentSerializer
    queryset = Assignment.objects.all()
    def get(self, request, *args, **kwargs):

        myheaders = request.headers.get("X-Principal")

        values = json.loads(myheaders)
        print(values)
        # rteacher = Teacher.objects.get(id = values.get("teacher_id"))
        user = User.objects.get(id = values.get("teacher_id"))

        assignments = Assignment.objects.filter(student__user=user)

        return Response(
            data=self.serializer_class(assignments, many=True).data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        student = Student.objects.get(user=request.user)
        request.data['student'] = student.id
        
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, *args, **kwargs):

        id = request.data.get("id")

        if 'grade' in request.data:
            if request.data.get("grade") not in ['A', 'B', 'C', 'D']:
                return Response(
                    data={'grade': ['is not a valid choice.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if 'student' in request.data:
            return Response(
                data={'non_field_errors': ['Teacher cannot change the student who submitted the assignment']},
                status=status.HTTP_400_BAD_REQUEST
            )


        if 'content' in request.data:
            return Response(
                data={'non_field_errors': ['Teacher cannot change the content of the assignment']},
                status=status.HTTP_400_BAD_REQUEST
            )

        assignment = Assignment.objects.get(id=id)
        if assignment.state == "DRAFT":
            return Response(
                data={'non_field_errors': ['SUBMITTED assignments can only be graded']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if assignment.state == "GRADED":
            return Response(
                data={'non_field_errors': ['GRADED assignments cannot be graded again']},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        headers = request.headers.get("X-Principal")
        values = json.loads(headers)
        if assignment.teacher.id != values.get("teacher_id"):
            return Response(
                data={'non_field_errors': ['Teacher cannot grade for other teacher''s assignment']},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        data["state"] = "GRADED"
        data['student'] = assignment.student.id
        data['teacher'] = assignment.teacher.id
        data['content'] = assignment.content
        data['created_at'] = assignment.created_at
        data['updated_at'] = assignment.updated_at
   
        serializer = self.serializer_class(assignment, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
