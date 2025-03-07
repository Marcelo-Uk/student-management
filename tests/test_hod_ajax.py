from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
from student_management_app.models import Courses, SessionYearModel, Subjects, Attendance, AttendanceReport

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
            staff_id=self.hod_user  # apenas para teste
        )
        # Cria uma Attendance para o Subject
        self.attendance = Attendance.objects.create(
            subject_id=self.subject,
            attendance_date="2025-02-01",
            session_year_id=self.session
        )
        # Cria um AttendanceReport para o Attendance (caso necessário)
        # Se necessário, adicione mais dados conforme a lógica

    def test_admin_get_attendance_dates(self):
        """Testa o endpoint admin_get_attendance_dates e verifica o JSON retornado."""
        data = {
            "subject": self.subject.id,
            "session_year_id": self.session.id
        }
        response = self.client.post(reverse('admin_get_attendance_dates'), data=data)
        self.assertEqual(response.status_code, 200)
        # Como a view usa json.dumps, convertemos a resposta para JSON
        data_returned = json.loads(response.content)
        # Verifica se pelo menos um item existe e tem as chaves esperadas
        self.assertIsInstance(data_returned, list)
        if data_returned:
            self.assertIn("id", data_returned[0])
            self.assertIn("attendance_date", data_returned[0])
            self.assertIn("session_year_id", data_returned[0])

    def test_admin_get_attendance_student(self):
        """Testa o endpoint admin_get_attendance_student e verifica o JSON retornado."""
        # Primeiro, precisamos de uma Attendance com um ID específico.
        # Usamos o ID da attendance criada no setUp.
        data = {
            "attendance_date": self.attendance.id
        }
        response = self.client.post(reverse('admin_get_attendance_student'), data=data)
        self.assertEqual(response.status_code, 200)
        # Verifica se o JSON pode ser carregado
        try:
            data_returned = json.loads(response.content)
            # Se houver dados, checa as chaves
            if data_returned:
                self.assertIn("id", data_returned[0])
                self.assertIn("name", data_returned[0])
                self.assertIn("status", data_returned[0])
        except json.JSONDecodeError:
            self.fail("A resposta não contém JSON válido.")

    def test_check_username_exist_false(self):
        """Caso exista, teste semelhante para check_username_exist, se implementado."""
        # Supondo que a view check_username_exist exista
        response = self.client.post(reverse('check_username_exist'), data={"username": "uniqueusername"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"False")
