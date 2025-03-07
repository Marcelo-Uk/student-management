from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from student_management_app.models import Students, Courses, SessionYearModel

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodViewsSessions(TestCase):
    def setUp(self):
        self.client = Client()

        # Cria usuário HOD com user_type="1"
        self.hod_user = User.objects.create_user(
            username="hodsession",
            password="hodpass",
            user_type="1"  # agora como string, conforme esperado pelo sistema
        )
        self.client.login(username="hodsession", password="hodpass")

        # Cria uma SessionYearModel para testar edição e deleção
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )

    def test_manage_session_get(self):
        """Testa se manage_session retorna o template correto."""
        response = self.client.get(reverse('manage_session'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_session_template.html")
        self.assertIn('session_years', response.context)

    def test_add_session_get(self):
        """Verifica se a rota add_session retorna o template."""
        response = self.client.get(reverse('add_session'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_session_template.html")

    def test_add_session_save_post_valid(self):
        """POST válido em add_session_save deve criar uma nova SessionYearModel."""
        data = {
            'session_start_year': '2026-01-01',
            'session_end_year': '2026-12-31'
        }
        response = self.client.post(reverse('add_session_save'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            SessionYearModel.objects.filter(
                session_start_year='2026-01-01',
                session_end_year='2026-12-31'
            ).exists()
        )

    def test_edit_session_get(self):
        """Verifica se a rota edit_session retorna o template correto."""
        response = self.client.get(reverse('edit_session', args=[self.session.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_session_template.html")

    def test_edit_session_save_post_valid(self):
        """POST válido em edit_session_save deve atualizar a SessionYearModel."""
        data = {
            'session_id': self.session.id,
            'session_start_year': '2027-01-01',
            'session_end_year': '2027-12-31'
        }
        response = self.client.post(reverse('edit_session_save'), data=data)
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(str(self.session.session_start_year), '2027-01-01')
        self.assertEqual(str(self.session.session_end_year), '2027-12-31')

    def test_delete_session_get(self):
        """Verifica se delete_session remove a sessão e redireciona."""
        response = self.client.get(reverse('delete_session', args=[self.session.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SessionYearModel.objects.filter(id=self.session.id).exists())


@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodViewsStudentManagement(TestCase):
    def setUp(self):
        self.client = Client()

        # Cria usuário HOD com user_type="1"
        self.hod_user = User.objects.create_user(
            username="hodstudent",
            password="hodpass",
            user_type="1"
        )
        self.client.login(username="hodstudent", password="hodpass")
        
        # Cria os objetos padrão necessários para o signal funcionar:
        # O signal em models.py faz Courses.objects.get(id=1) e SessionYearModel.objects.get(id=1)
        self.default_course = Courses.objects.create(id=1, course_name="Default Course")
        self.default_session = SessionYearModel.objects.create(
            id=1,
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        
        # Cria um curso e uma sessão para os testes (podem ser diferentes dos padrão)
        self.course = Courses.objects.create(course_name="TestCourse")
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        
        # Cria um usuário estudante com user_type="3"
        self.student_user = User.objects.create_user(
            username="student_test",
            password="testpass",
            user_type="3"
        )
        # Recupera o objeto Students criado automaticamente pelo signal
        self.student = Students.objects.get(admin=self.student_user)
        # Atualiza o objeto para os dados que queremos usar no teste
        self.student.course_id = self.course
        self.student.session_year_id = self.session
        self.student.save()

    def test_manage_student_get(self):
        """Testa se manage_student retorna o template e inclui o estudante."""
        response = self.client.get(reverse('manage_student'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod_template/manage_student_template.html')
        self.assertIn('students', response.context)
        self.assertIn(self.student, response.context['students'])

    def test_delete_student_get(self):
        """Verifica se delete_student remove o student e redireciona."""
        response = self.client.get(reverse('delete_student', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Students.objects.filter(admin=self.student_user).exists())

    def test_check_email_exist_true(self):
        """Cria um usuário com e-mail 'existing@test.com' e verifica se retorna True."""
        User.objects.create_user(username="existing", email="existing@test.com", password="pass")
        response = self.client.post(reverse('check_email_exist'), data={"email": "existing@test.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"True")

    def test_check_email_exist_false(self):
        """Verifica se um e-mail que não existe retorna False."""
        response = self.client.post(reverse('check_email_exist'), data={"email": "notfound@test.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"False")
