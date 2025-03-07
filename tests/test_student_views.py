from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

import datetime

from student_management_app.models import (
    Students, Courses, SessionYearModel, LeaveReportStudent, 
    FeedBackStudent, StudentResult
)

User = get_user_model()


class TestStudentViews(TestCase):
    def setUp(self):
        """
        Configura o ambiente de teste, criando um usuário 'student' e
        objetos necessários para as views (curso, sessão etc.).
        """
        self.client = Client()

        # Cria um curso e um SessionYear para associar ao estudante
        self.course = Courses.objects.create(
            id=1,
            course_name="Test Course"
        )
        self.session = SessionYearModel.objects.create(
            id=1,
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )

        # Cria um usuário e o registra como estudante (user_type=3)
        self.user = User.objects.create_user(
            username="studentuser",
            password="testpass",
            user_type=3
        )
        self.student = Students.objects.create(
            admin=self.user,
            gender="Male",
            profile_pic="",
            address="Test Address",
            course_id=self.course,
            session_year_id=self.session
        )

        # Loga o usuário no sistema
        self.client.login(username="studentuser", password="testpass")

    def test_student_home_view_get(self):
        """
        Verifica se a rota student_home retorna status 200 e utiliza
        o template correto.
        """
        response = self.client.get(reverse('student_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_home_template.html')
        # Checando dados no contexto
        self.assertIn('total_attendance', response.context)
        self.assertIn('attendance_present', response.context)
        self.assertIn('attendance_absent', response.context)

    def test_student_view_attendance_get(self):
        """
        Verifica se a rota student_view_attendance retorna status 200
        e carrega o template correto.
        """
        response = self.client.get(reverse('student_view_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_view_attendance.html')
        # Exemplo de checar contexto
        self.assertIn('subjects', response.context)

    def test_student_view_attendance_post_valid(self):
        """
        Verifica se o student_view_attendance_post processa corretamente
        um POST com datas válidas e subject_id existente.
        """
        # Cria um subject associado ao course
        from student_management_app.models import Subjects
        subject = Subjects.objects.create(
            subject_name="Math",
            course_id=self.course,
            staff_id=self.user  # assumindo que o staff_id aceita CustomUser
        )

        data = {
            'subject': subject.id,
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }
        response = self.client.post(reverse('student_view_attendance_post'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_attendance_data.html')
        # Verifica se attendance_reports está no contexto
        self.assertIn('attendance_reports', response.context)

    def test_student_apply_leave_get(self):
        """
        Verifica se a rota student_apply_leave retorna o template correto.
        """
        response = self.client.get(reverse('student_apply_leave'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_apply_leave.html')

    def test_student_apply_leave_save_post(self):
        """
        Verifica o POST em student_apply_leave_save e se um LeaveReportStudent
        é criado corretamente.
        """
        data = {
            'leave_date': '2025-05-10',
            'leave_message': 'Sick leave'
        }
        response = self.client.post(reverse('student_apply_leave_save'), data=data)
        self.assertEqual(response.status_code, 302)  # Redireciona para student_apply_leave
        self.assertTrue(
            LeaveReportStudent.objects.filter(
                student_id=self.student,
                leave_date='2025-05-10',
                leave_message='Sick leave'
            ).exists()
        )

    def test_student_feedback_get(self):
        response = self.client.get(reverse('student_feedback'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_feedback.html')
        self.assertIn('feedback_data', response.context)

    def test_student_feedback_save_post(self):
        data = {
            'feedback_message': 'This is a feedback message.'
        }
        response = self.client.post(reverse('student_feedback_save'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FeedBackStudent.objects.filter(
                student_id=self.student,
                feedback='This is a feedback message.'
            ).exists()
        )

    def test_student_profile_get(self):
        response = self.client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_profile.html')
        self.assertIn('user', response.context)
        self.assertIn('student', response.context)

    def test_student_profile_update_post(self):
        data = {
            'first_name': 'NewName',
            'last_name': 'LastName',
            'password': '',
            'address': 'New Address'
        }
        response = self.client.post(reverse('student_profile_update'), data=data)
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.address, 'New Address')
        # Verifica se o CustomUser foi atualizado
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'NewName')
        self.assertEqual(self.user.last_name, 'LastName')

    def test_student_view_result_get(self):
        """
        Verifica se a rota student_view_result retorna o template correto.
        """
        # Criando um StudentResult
        StudentResult.objects.create(
            student_id=self.student,
            subject_id=None,  # ou crie uma Subject se necessário
            subject_exam_marks=80,
            subject_assignment_marks=90
        )
        response = self.client.get(reverse('student_view_result'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_template/student_view_result.html')
        self.assertIn('student_result', response.context)
