from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from student_management_app.models import (
    CustomUser, Staffs, Courses, SessionYearModel
)

User = get_user_model()


class TestHodViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Cria um usuário com user_type=1 (HOD)
        self.hod_user = User.objects.create_user(
            username="hoduser",
            password="hodpass",
            user_type=1
        )
        self.hod_user.save()

        # Força login para garantir que o usuário seja reconhecido como HOD
        self.client.force_login(self.hod_user)

        # Criar um staff existente para testar 'manage_staff' e 'delete_staff'
        self.staff_user = User.objects.create_user(
            username="staffexisting",
            password="staffpass",
            email="staff@test.com",
            first_name="Staff",
            last_name="Exist",
            user_type=2
        )
        self.staff_user.staffs.address = "Staff Address"
        self.staff_user.save()

        # Criar um course existente para testar 'manage_course' e 'delete_course'
        self.course = Courses.objects.create(course_name="Existing Course")

    # -------------------------------------------------------------------------
    # 1. admin_home
    # -------------------------------------------------------------------------
    def test_admin_home_get(self):
        """Verifica se a rota admin_home retorna status 200 e o template correto."""
        response = self.client.get(reverse('admin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/home_content.html")
        # Checar dados de contexto que a view injeta (opcional)
        self.assertIn("all_student_count", response.context)
        self.assertIn("staff_count", response.context)

    # -------------------------------------------------------------------------
    # 2. Adicionar Staff
    # -------------------------------------------------------------------------
    def test_add_staff_get(self):
        """Verifica se a rota add_staff retorna status 200 e o template correto."""
        response = self.client.get(reverse('add_staff'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_staff_template.html")

    def test_add_staff_save_post(self):
        """
        Verifica se a rota add_staff_save cria um novo usuário do tipo Staff (user_type=2).
        """
        data = {
            "first_name": "Novo",
            "last_name": "Staff",
            "username": "novostaff",
            "email": "novo.staff@test.com",
            "password": "staff123",
            "address": "Novo Endereço"
        }
        response = self.client.post(reverse('add_staff_save'), data=data)
        # Em caso de sucesso, a view deve redirecionar (status 302)
        self.assertEqual(response.status_code, 302)

        # Verifica se o novo usuário staff foi criado
        self.assertTrue(
            User.objects.filter(username="novostaff", user_type=2).exists()
        )
        # Verifica se o staff tem o endereço salvo
        staff_user = User.objects.get(username="novostaff")
        self.assertEqual(staff_user.staffs.address, "Novo Endereço")

    # -------------------------------------------------------------------------
    # 3. Manage Staff
    # -------------------------------------------------------------------------
    def test_manage_staff_get(self):
        """Verifica se a rota manage_staff retorna status 200 e o template correto."""
        response = self.client.get(reverse('manage_staff'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_staff_template.html")
        # Checa se 'staffs' está no contexto
        self.assertIn("staffs", response.context)
        # Garante que o staff criado no setUp está na lista
        self.assertIn(self.staff_user.staffs, response.context["staffs"])

    def test_delete_staff_get(self):
        """
        Verifica se a rota delete_staff remove o staff existente
        e redireciona para manage_staff.
        """
        response = self.client.get(reverse('delete_staff', args=[self.staff_user.id]))
        self.assertEqual(response.status_code, 302)  # redireciona
        self.assertFalse(
            Staffs.objects.filter(admin=self.staff_user.id).exists()
        )

    # -------------------------------------------------------------------------
    # 4. Adicionar e Gerenciar Cursos
    # -------------------------------------------------------------------------
    def test_add_course_get(self):
        response = self.client.get(reverse('add_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_course_template.html")

    def test_add_course_save_post(self):
        data = {
            "course": "Novo Curso"
        }
        response = self.client.post(reverse('add_course_save'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Courses.objects.filter(course_name="Novo Curso").exists())

    def test_manage_course_get(self):
        response = self.client.get(reverse('manage_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_course_template.html")
        self.assertIn("courses", response.context)
        self.assertIn(self.course, response.context["courses"])

    def test_delete_course_get(self):
        response = self.client.get(reverse('delete_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Courses.objects.filter(id=self.course.id).exists())

    # -------------------------------------------------------------------------
    # 5. Admin Profile
    # -------------------------------------------------------------------------
    def test_admin_profile_get(self):
        response = self.client.get(reverse('admin_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod_template/admin_profile.html')
        self.assertIn('user', response.context)

    def test_admin_profile_update_post(self):
        data = {
            "first_name": "HODNome",
            "last_name": "HODSobrenome",
            "password": ""  # vazio significa que não troca a senha
        }
        response = self.client.post(reverse('admin_profile_update'), data=data)
        self.assertEqual(response.status_code, 302)

        self.hod_user.refresh_from_db()
        self.assertEqual(self.hod_user.first_name, "HODNome")
        self.assertEqual(self.hod_user.last_name, "HODSobrenome")
