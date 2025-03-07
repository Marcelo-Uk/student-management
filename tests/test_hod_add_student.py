from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from student_management_app.models import Courses, SessionYearModel

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodAddStudent(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria um usuário HOD (user_type="1") para autenticação
        self.hod_user = User.objects.create_user(
            username="hodstudentadd",
            password="hodpass",
            user_type="1"
        )
        self.client.login(username="hodstudentadd", password="hodpass")
        
        # Cria os objetos necessários para o form funcionar corretamente
        self.course = Courses.objects.create(course_name="Integration Course")
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )

    def test_add_student_save_valid(self):
        """
        Testa o fluxo de adicionar um estudante via POST na view add_student_save.
        Simula o envio de dados válidos e um arquivo de perfil.
        """
        # Cria um arquivo dummy para simular o upload do profile_pic
        dummy_file = SimpleUploadedFile("test_pic.jpg", b"file_content", content_type="image/jpeg")
        data = {
            "email": "newstudent@test.com",
            "password": "newpass",
            "first_name": "New",
            "last_name": "Student",
            "username": "newstudent",
            "address": "123 New Street",
            "course_id": str(self.course.id),
            "gender": "Male",
            "session_year_id": str(self.session.id),
        }
        files = {
            "profile_pic": dummy_file
        }
        response = self.client.post(reverse("add_student_save"), data=data, files=files)
        # Espera redirecionamento para a página de adicionar estudante
        self.assertEqual(response.status_code, 302)
        # Verifica se um novo usuário estudante foi criado com o e-mail fornecido
        new_user = User.objects.filter(email="newstudent@test.com", user_type="3").first()
        self.assertIsNotNone(new_user)
