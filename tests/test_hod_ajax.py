from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
from student_management_app.models import Courses, SessionYearModel, Subjects, Attendance

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodAjaxEndpoints(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria um usuário HOD e loga
        self.hod_user = User.objects.create_user(
            username="hodajax",
            password="hodpass",
            user_type="1"
        )
        self.client.login(username="hodajax", password="hodpass")
        
        # Cria dados básicos
        self.course = Courses.objects.create(course_name="Ajax Course")
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        self.subject = Subjects.objects.create(
            subject_name="Ajax Subject",
            course_id=self.course,
            staff_id=self.hod_user  # Apenas para teste
        )
        # Cria uma Attendance para o Subject
        self.attendance = Attendance.objects.create(
            subject_id=self.subject,
            attendance_date="2025-02-01",
            session_year_id=self.session
        )

    def test_admin_get_attendance_dates(self):
        """Testa o endpoint admin_get_attendance_dates e verifica o JSON retornado."""
        data = {
            "subject": self.subject.id,
            "session_year_id": self.session.id
        }
        response = self.client.post(reverse('admin_get_attendance_dates'), data=data)
        self.assertEqual(response.status_code, 200)
        # Primeiro deserializamos o conteúdo da resposta (que é uma string JSON)
        data_intermediate = json.loads(response.content.decode('utf-8'))
        # data_intermediate agora é uma string; desserializamos novamente:
        data_returned = json.loads(data_intermediate)
        self.assertIsInstance(data_returned, list)
        if data_returned:
            self.assertIn("id", data_returned[0])
            self.assertIn("attendance_date", data_returned[0])
            self.assertIn("session_year_id", data_returned[0])

    def test_admin_get_attendance_student(self):
        """Testa o endpoint admin_get_attendance_student e verifica o JSON retornado."""
        data = {
            "attendance_date": self.attendance.id
        }
        response = self.client.post(reverse('admin_get_attendance_student'), data=data)
        self.assertEqual(response.status_code, 200)
        # Desserializa duas vezes, como no teste anterior:
        data_intermediate = json.loads(response.content.decode('utf-8'))
        data_returned = json.loads(data_intermediate)
        try:
            if data_returned:
                self.assertIn("id", data_returned[0])
                self.assertIn("name", data_returned[0])
                self.assertIn("status", data_returned[0])
        except Exception as e:
            self.fail("A resposta não contém JSON válido: " + str(e))
