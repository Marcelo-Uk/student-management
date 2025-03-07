from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from student_management_app.models import Courses, SessionYearModel

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodSubjectManagement(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria um usuário HOD (user_type como string, conforme esperado)
        self.hod_user = User.objects.create_user(
            username="hodsubject",
            password="hodpass",
            user_type="1"
        )
        self.client.login(username="hodsubject", password="hodpass")
        
        # Cria um curso que será usado para subjects
        self.course = Courses.objects.create(course_name="Test Course for Subject")
        # Cria uma sessão, caso seja necessária (não usada diretamente aqui)
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        
        # Cria um usuário staff para associar ao subject (user_type="2")
        self.staff_user = User.objects.create_user(
            username="staffsubject",
            password="staffpass",
            user_type="2"
        )
    
    def test_add_subject_get(self):
        """Testa se a rota add_subject retorna o template correto."""
        response = self.client.get(reverse("add_subject"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_subject_template.html")
    
    def test_add_subject_save_post_valid(self):
        """Testa se o POST em add_subject_save cria um novo subject e redireciona."""
        data = {
            "subject": "Mathematics",
            "course": str(self.course.id),
            "staff": str(self.staff_user.id)
        }
        response = self.client.post(reverse("add_subject_save"), data=data)
        self.assertEqual(response.status_code, 302)
        from student_management_app.models import Subjects
        subject_exists = Subjects.objects.filter(
            subject_name="Mathematics",
            course_id=self.course,
            staff_id=self.staff_user
        ).exists()
        self.assertTrue(subject_exists)
    
    def test_manage_subject_get(self):
        """Testa se manage_subject retorna o template correto e inclui os subjects."""
        from student_management_app.models import Subjects
        subject = Subjects.objects.create(
            subject_name="Physics",
            course_id=self.course,
            staff_id=self.staff_user
        )
        response = self.client.get(reverse("manage_subject"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_subject_template.html")
        self.assertIn("subjects", response.context)
        self.assertIn(subject, response.context["subjects"])
    
    def test_edit_subject_get(self):
        """Testa se edit_subject retorna o template correto com o subject a ser editado."""
        from student_management_app.models import Subjects
        subject = Subjects.objects.create(
            subject_name="Chemistry",
            course_id=self.course,
            staff_id=self.staff_user
        )
        response = self.client.get(reverse("edit_subject", args=[subject.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_subject_template.html")
        self.assertIn("subject", response.context)
        self.assertEqual(response.context["subject"].id, subject.id)
    
    def test_edit_subject_save_post_valid(self):
        """Testa se o POST em edit_subject_save atualiza o subject e redireciona."""
        from student_management_app.models import Subjects
        subject = Subjects.objects.create(
            subject_name="Biology",
            course_id=self.course,
            staff_id=self.staff_user
        )
        data = {
            "subject_id": subject.id,
            "subject": "Advanced Biology",
            "course": str(self.course.id),
            "staff": str(self.staff_user.id)
        }
        response = self.client.post(reverse("edit_subject_save"), data=data)
        self.assertEqual(response.status_code, 302)
        subject.refresh_from_db()
        self.assertEqual(subject.subject_name, "Advanced Biology")
    
    def test_delete_subject_get(self):
        """Testa se delete_subject deleta o subject e redireciona."""
        from student_management_app.models import Subjects
        subject = Subjects.objects.create(
            subject_name="Geography",
            course_id=self.course,
            staff_id=self.staff_user
        )
        response = self.client.get(reverse("delete_subject", args=[subject.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Subjects.objects.filter(id=subject.id).exists())
