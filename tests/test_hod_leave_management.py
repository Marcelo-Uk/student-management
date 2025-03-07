from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from student_management_app.models import (
    Courses, SessionYearModel, Students, Staffs,
    LeaveReportStudent, LeaveReportStaff
)

User = get_user_model()

@override_settings(
    MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]
)
class TestHodLeaveManagement(TestCase):
    def setUp(self):
        self.client = Client()

        # Cria um usuário HOD para os testes (user_type="1")
        self.hod_user = User.objects.create_user(
            username="hodleave",
            password="hodpass",
            user_type="1"
        )
        self.client.login(username="hodleave", password="hodpass")
        
        # Cria objetos padrão necessários para o signal (caso o sistema os utilize)
        self.default_course = Courses.objects.create(id=1, course_name="Default Course")
        self.default_session = SessionYearModel.objects.create(
            id=1,
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        
        # Cria um curso e uma sessão para os testes (diferentes dos padrão)
        self.course = Courses.objects.create(course_name="TestCourse")
        self.session = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )
        
        # Cria um usuário estudante dummy (user_type="3")
        self.student_user = User.objects.create_user(
            username="student_dummy",
            password="studpass",
            user_type="3"
        )
        # Tenta recuperar o objeto Students criado automaticamente; se não existir, cria manualmente
        try:
            self.student = Students.objects.get(admin=self.student_user)
        except Students.DoesNotExist:
            self.student = Students.objects.create(
                admin=self.student_user,
                course_id=self.default_course,
                session_year_id=self.default_session,
                address="",
                profile_pic="",
                gender="Male"
            )
        # Atualiza o objeto para usar os dados do teste
        self.student.course_id = self.course
        self.student.session_year_id = self.session
        self.student.save()

        # Cria um usuário staff dummy (user_type="2")
        self.staff_user = User.objects.create_user(
            username="staff_dummy",
            password="staffpass",
            user_type="2"
        )
        try:
            self.staff = Staffs.objects.get(admin=self.staff_user)
        except Staffs.DoesNotExist:
            self.staff = Staffs.objects.create(
                admin=self.staff_user,
                address="Dummy Staff Address"
            )

    # ----- Testes para Leaves de Estudantes -----

    def test_student_leave_view_get(self):
        """Testa se a rota student_leave_view retorna o template e inclui os leaves."""
        # Cria um leave para estudante
        leave = LeaveReportStudent.objects.create(
            student_id=self.student,
            leave_date="2025-03-10",
            leave_message="Need leave",
            leave_status=0
        )
        response = self.client.get(reverse('student_leave_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod_template/student_leave_view.html')
        self.assertIn('leaves', response.context)
        # Verifica se o leave criado está na lista
        self.assertIn(leave, response.context['leaves'])

    def test_student_leave_approve(self):
        """Testa se student_leave_approve atualiza o leave_status para 1 e redireciona."""
        leave = LeaveReportStudent.objects.create(
            student_id=self.student,
            leave_date="2025-03-10",
            leave_message="Need leave",
            leave_status=0
        )
        response = self.client.get(reverse('student_leave_approve', args=[leave.id]))
        self.assertEqual(response.status_code, 302)
        leave.refresh_from_db()
        self.assertEqual(leave.leave_status, 1)

    def test_student_leave_reject(self):
        """Testa se student_leave_reject atualiza o leave_status para 2 e redireciona."""
        leave = LeaveReportStudent.objects.create(
            student_id=self.student,
            leave_date="2025-03-10",
            leave_message="Need leave",
            leave_status=0
        )
        response = self.client.get(reverse('student_leave_reject', args=[leave.id]))
        self.assertEqual(response.status_code, 302)
        leave.refresh_from_db()
        self.assertEqual(leave.leave_status, 2)

    # ----- Testes para Leaves de Staff -----

    def test_staff_leave_view_get(self):
        """Testa se staff_leave_view retorna o template e inclui os leaves."""
        leave = LeaveReportStaff.objects.create(
            staff_id=self.staff,
            leave_date="2025-04-15",
            leave_message="Staff leave request",
            leave_status=0
        )
        response = self.client.get(reverse('staff_leave_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hod_template/staff_leave_view.html')
        self.assertIn('leaves', response.context)
        self.assertIn(leave, response.context['leaves'])

    def test_staff_leave_approve(self):
        """Testa se staff_leave_approve atualiza o leave_status para 1 e redireciona."""
        leave = LeaveReportStaff.objects.create(
            staff_id=self.staff,
            leave_date="2025-04-15",
            leave_message="Staff leave request",
            leave_status=0
        )
        response = self.client.get(reverse('staff_leave_approve', args=[leave.id]))
        self.assertEqual(response.status_code, 302)
        leave.refresh_from_db()
        self.assertEqual(leave.leave_status, 1)

    def test_staff_leave_reject(self):
        """Testa se staff_leave_reject atualiza o leave_status para 2 e redireciona."""
        leave = LeaveReportStaff.objects.create(
            staff_id=self.staff,
            leave_date="2025-04-15",
            leave_message="Staff leave request",
            leave_status=0
        )
        response = self.client.get(reverse('staff_leave_reject', args=[leave.id]))
        self.assertEqual(response.status_code, 302)
        leave.refresh_from_db()
        self.assertEqual(leave.leave_status, 2)
