from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
from student_management_app.models import FeedBackStudent, FeedBackStaffs, Courses, SessionYearModel, Students, Staffs

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestFeedbackReplyEndpoints(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria um usuário HOD para autenticação
        self.hod_user = User.objects.create_user(
            username="hodfeedback",
            password="pass",
            user_type="1"
        )
        self.client.login(username="hodfeedback", password="pass")
        
        # Cria objetos padrão para que, se necessário, o signal funcione
        self.default_course = Courses.objects.create(id=1, course_name="Default Course")
        self.default_session = SessionYearModel.objects.create(
            id=1,
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        
        # Cria usuário dummy para feedback de estudante (user_type="3")
        self.dummy_student_user = User.objects.create_user(
            username="dummy_student",
            password="pass",
            user_type="3"
        )
        # Tenta recuperar o objeto Students criado automaticamente pelo signal;
        # se não existir, cria manualmente usando os objetos padrão
        try:
            self.dummy_student = Students.objects.get(admin=self.dummy_student_user)
        except Students.DoesNotExist:
            self.dummy_student = Students.objects.create(
                admin=self.dummy_student_user,
                course_id=self.default_course,
                session_year_id=self.default_session,
                address="",
                profile_pic="",
                gender="Male"
            )
        
        # Cria usuário dummy para feedback de staff (user_type="2")
        self.dummy_staff_user = User.objects.create_user(
            username="dummy_staff",
            password="pass",
            user_type="2"
        )
        try:
            self.dummy_staff = Staffs.objects.get(admin=self.dummy_staff_user)
        except Staffs.DoesNotExist:
            self.dummy_staff = Staffs.objects.create(
                admin=self.dummy_staff_user,
                address="Staff Address"
            )
        
        # Cria feedback para estudante e staff utilizando os objetos dummy
        self.student_feedback = FeedBackStudent.objects.create(
            student_id=self.dummy_student,
            feedback="Initial student feedback",
            feedback_reply=""
        )
        self.staff_feedback = FeedBackStaffs.objects.create(
            staff_id=self.dummy_staff,
            feedback="Initial staff feedback",
            feedback_reply=""
        )

    def test_student_feedback_reply_success(self):
        """Verifica se o endpoint student_feedback_message_reply atualiza o feedback com sucesso."""
        data = {
            "id": self.student_feedback.id,
            "reply": "Student reply updated"
        }
        response = self.client.post(reverse("student_feedback_message_reply"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"True")
        self.student_feedback.refresh_from_db()
        self.assertEqual(self.student_feedback.feedback_reply, "Student reply updated")

    def test_student_feedback_reply_failure(self):
        """Verifica se o endpoint student_feedback_message_reply retorna 'False' quando o feedback não existe."""
        data = {
            "id": 9999,  # ID inexistente
            "reply": "Reply"
        }
        response = self.client.post(reverse("student_feedback_message_reply"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"False")

    def test_staff_feedback_reply_success(self):
        """Verifica se o endpoint staff_feedback_message_reply atualiza o feedback com sucesso."""
        data = {
            "id": self.staff_feedback.id,
            "reply": "Staff reply updated"
        }
        response = self.client.post(reverse("staff_feedback_message_reply"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"True")
        self.staff_feedback.refresh_from_db()
        self.assertEqual(self.staff_feedback.feedback_reply, "Staff reply updated")

    def test_staff_feedback_reply_failure(self):
        """Verifica se o endpoint staff_feedback_message_reply retorna 'False' quando o feedback não existe."""
        data = {
            "id": 9999,  # ID inexistente
            "reply": "Reply"
        }
        response = self.client.post(reverse("staff_feedback_message_reply"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"False")
