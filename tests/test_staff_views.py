from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from student_management_app.models import (
    Staffs, Courses, SessionYearModel, LeaveReportStaff, 
    FeedBackStaffs, Subjects, Students, StudentResult
)

User = get_user_model()


class TestStaffViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Cria um curso e uma session year
        self.course = Courses.objects.create(course_name="Test Course for Staff")
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )

        # Cria usuário do tipo Staff
        self.user = User.objects.create_user(
            username="staffuser",
            password="staffpass",
            user_type=2
        )
        self.user.save()

        # A signal já cria Staffs se user_type=2
        self.staff = Staffs.objects.get(admin=self.user)
        # Ajuste campos do Staff, se necessário
        self.staff.address = "Staff Address"
        self.staff.save()

        # Força login para garantir que o usuário esteja autenticado como staff
        self.client.force_login(self.user)

    def test_staff_home_get(self):
        """Verifica se a rota staff_home retorna status 200 e o template correto."""
        response = self.client.get(reverse('staff_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_template/staff_home_template.html')

    def test_staff_take_attendance_get(self):
        """Verifica se a rota staff_take_attendance retorna status 200 e o template correto."""
        response = self.client.get(reverse('staff_take_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_template/take_attendance_template.html')
        # Verifica se 'subjects' e 'session_years' estão no contexto
        self.assertIn('subjects', response.context)
        self.assertIn('session_years', response.context)

    def test_staff_apply_leave_get(self):
        """Verifica se a rota staff_apply_leave retorna status 200 e o template correto."""
        response = self.client.get(reverse('staff_apply_leave'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_template/staff_apply_leave_template.html')

    def test_staff_apply_leave_save_post(self):
        """Verifica o POST em staff_apply_leave_save e se um LeaveReportStaff é criado."""
        data = {
            'leave_date': '2025-05-10',
            'leave_message': 'Medical leave'
        }
        response = self.client.post(reverse('staff_apply_leave_save'), data=data)
        self.assertEqual(response.status_code, 302)  # Redireciona para staff_apply_leave

        # Verifica se o LeaveReportStaff foi criado
        self.assertTrue(
            LeaveReportStaff.objects.filter(
                staff_id=self.staff,
                leave_date='2025-05-10',
                leave_message='Medical leave'
            ).exists()
        )

    def test_staff_feedback_get(self):
        """Verifica se a rota staff_feedback retorna status 200 e o template correto."""
        response = self.client.get(reverse('staff_feedback'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_template/staff_feedback_template.html')
        self.assertIn('feedback_data', response.context)

    def test_staff_feedback_save_post(self):
        """Verifica o POST em staff_feedback_save e se um FeedBackStaffs é criado."""
        data = {
            'feedback_message': 'Staff feedback message'
        }
        response = self.client.post(reverse('staff_feedback_save'), data=data)
        self.assertEqual(response.status_code, 302)  # Redireciona para staff_feedback

        # Verifica se o FeedBackStaffs foi criado
        self.assertTrue(
            FeedBackStaffs.objects.filter(
                staff_id=self.staff,
                feedback='Staff feedback message'
            ).exists()
        )

    def test_staff_profile_get(self):
        """Verifica se a rota staff_profile retorna status 200 e o template correto."""
        response = self.client.get(reverse('staff_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_template/staff_profile.html')
        self.assertIn('user', response.context)
        self.assertIn('staff', response.context)

    def test_staff_profile_update_post(self):
        """Verifica o POST em staff_profile_update e se os dados do Staff são atualizados."""
        data = {
            'first_name': 'StaffName',
            'last_name': 'LastStaff',
            'password': '',
            'address': 'New Staff Address'
        }
        response = self.client.post(reverse('staff_profile_update'), data=data)
        self.assertEqual(response.status_code, 302)

        # Verifica se o Staff foi atualizado
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.address, 'New Staff Address')
        # Verifica se o CustomUser foi atualizado
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'StaffName')
        self.assertEqual(self.user.last_name, 'LastStaff')

    def test_staff_add_result_get(self):
        """Verifica se a rota staff_add_result retorna o template correto."""
        response = self.client.get(reverse('staff_add_result'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff_template/add_result_template.html')
        self.assertIn('subjects', response.context)
        self.assertIn('session_years', response.context)

    def test_staff_add_result_save_post(self):
        """
        Verifica o POST em staff_add_result_save.
        Cria Subject e Student para simular o salvamento/atualização do resultado.
        """
        # Cria Subject vinculado ao staff
        subject = Subjects.objects.create(
            subject_name="Test Subject",
            course_id=self.course,
            staff_id=self.user
        )
        # Cria Student para simular a escolha no formulário
        student_user = User.objects.create_user(username="student2", password="studpass", user_type=3)
        student = Students.objects.create(
            admin=student_user,
            course_id=self.course,
            session_year_id=self.session
        )

        data = {
            'student_list': student_user.id,  # 'student_list' no form staff_add_result_save
            'assignment_marks': '30',
            'exam_marks': '70',
            'subject': subject.id
        }
        response = self.client.post(reverse('staff_add_result_save'), data=data)
        self.assertEqual(response.status_code, 302)  # Redireciona para staff_add_result

        # Verifica se o StudentResult foi criado ou atualizado
        self.assertTrue(
            StudentResult.objects.filter(
                student_id=student,
                subject_id=subject,
                subject_assignment_marks=30,
                subject_exam_marks=70
            ).exists()
        )
