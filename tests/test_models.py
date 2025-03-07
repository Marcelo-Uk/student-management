from django.test import TestCase
from django.contrib.auth import get_user_model

from student_management_app.models import (
    AdminHOD, Staffs, Students,
    Courses, SessionYearModel
)

CustomUser = get_user_model() 


class TestUserSignals(TestCase):
    def setUp(self):
        """
        Cria registros iniciais necessários para testar a criação automática
        de Students (user_type=3) via signals.
        """
        self.course = Courses.objects.create(
            id=1,
            course_name="Curso de Teste"
        )
        self.session_year = SessionYearModel.objects.create(
            id=1,
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )

    def test_admin_creation_signal(self):
        """
        Verifica se, ao criar um CustomUser com user_type=1, 
        um objeto AdminHOD é criado automaticamente.
        """
        user = CustomUser.objects.create_user(
            username="admin1",
            password="adminpass",
            user_type=1,
            email="admin1@test.com"
        )
        # Verifica se existe um registro de AdminHOD vinculado a esse usuário
        admin_hod = AdminHOD.objects.get(admin=user)
        self.assertIsNotNone(admin_hod)
        self.assertEqual(admin_hod.admin.username, "admin1")

    def test_staff_creation_signal(self):
        """
        Verifica se, ao criar um CustomUser com user_type=2,
        um objeto Staffs é criado automaticamente.
        """
        user = CustomUser.objects.create_user(
            username="staff1",
            password="staffpass",
            user_type=2,
            email="staff1@test.com"
        )
        # Verifica se existe um registro de Staffs vinculado a esse usuário
        staff = Staffs.objects.get(admin=user)
        self.assertIsNotNone(staff)
        self.assertEqual(staff.admin.username, "staff1")

    def test_student_creation_signal(self):
        """
        Verifica se, ao criar um CustomUser com user_type=3,
        um objeto Students é criado automaticamente, vinculado ao Course e SessionYear.
        """
        user = CustomUser.objects.create_user(
            username="student1",
            password="studpass",
            user_type=3,
            email="student1@test.com"
        )
        # Verifica se existe um registro de Students vinculado a esse usuário
        student = Students.objects.get(admin=user)
        self.assertIsNotNone(student)
        self.assertEqual(student.admin.username, "student1")
        self.assertEqual(student.course_id, self.course)
        self.assertEqual(student.session_year_id, self.session_year)
        # Verifica valores default definidos na signal
        self.assertEqual(student.address, "")
        self.assertEqual(student.gender, "")
        self.assertEqual(student.profile_pic, "")
