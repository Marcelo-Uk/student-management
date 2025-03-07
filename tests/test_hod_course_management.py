from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from student_management_app.models import Courses

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodCourseManagement(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria um usuário HOD (user_type como string, conforme o sistema espera)
        self.hod_user = User.objects.create_user(
            username="hodcourse",
            password="hodpass",
            user_type="1"
        )
        self.client.login(username="hodcourse", password="hodpass")

    def test_add_course_get(self):
        """Testa se a rota add_course retorna o template correto."""
        response = self.client.get(reverse("add_course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_course_template.html")

    def test_add_course_save_post_valid(self):
        """Testa se o POST em add_course_save cria um novo curso e redireciona."""
        data = {
            "course": "New Course"
        }
        response = self.client.post(reverse("add_course_save"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Courses.objects.filter(course_name="New Course").exists())

    def test_add_course_save_post_invalid_method(self):
        """Testa se um GET em add_course_save retorna redirecionamento (método inválido)."""
        response = self.client.get(reverse("add_course_save"))
        self.assertEqual(response.status_code, 302)

    def test_manage_course_get(self):
        """Testa se manage_course retorna o template correto e lista os cursos."""
        course = Courses.objects.create(course_name="Test Course")
        response = self.client.get(reverse("manage_course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_course_template.html")
        self.assertIn("courses", response.context)
        self.assertIn(course, response.context["courses"])

    def test_edit_course_get(self):
        """Testa se edit_course retorna o template correto para edição."""
        course = Courses.objects.create(course_name="Editable Course")
        response = self.client.get(reverse("edit_course", args=[course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_course_template.html")
        self.assertIn("course", response.context)
        self.assertEqual(response.context["course"].id, course.id)

    def test_edit_course_save_post_valid(self):
        """Testa se o POST em edit_course_save atualiza o curso e redireciona."""
        course = Courses.objects.create(course_name="Old Course Name")
        data = {
            "course_id": course.id,
            "course": "Updated Course Name"
        }
        response = self.client.post(reverse("edit_course_save"), data=data)
        self.assertEqual(response.status_code, 302)
        course.refresh_from_db()
        self.assertEqual(course.course_name, "Updated Course Name")

    def test_edit_course_save_post_invalid_method(self):
        """Testa se o GET em edit_course_save não retorna status 200 (método inválido)."""
        response = self.client.get(reverse("edit_course_save"))
        self.assertNotEqual(response.status_code, 200)

    def test_delete_course_get(self):
        """Testa se delete_course deleta o curso e redireciona."""
        course = Courses.objects.create(course_name="Course To Delete")
        response = self.client.get(reverse("delete_course", args=[course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Courses.objects.filter(id=course.id).exists())
