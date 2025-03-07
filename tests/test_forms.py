from django.test import TestCase
from student_management_app.models import Courses, SessionYearModel
from student_management_app.forms import AddStudentForm, EditStudentForm


class TestAddStudentForm(TestCase):
    def setUp(self):
        # Cria dados para popular as choices do form
        self.course = Courses.objects.create(course_name="Test Course")
        self.session_year = SessionYearModel.objects.create(
            session_start_year="2025-01-01",
            session_end_year="2025-12-31"
        )

    def test_form_valid_data(self):
        """Verifica se o form é válido quando todos os campos obrigatórios são fornecidos corretamente."""
        data = {
            "email": "test@student.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "address": "123 Street",
            "course_id": str(self.course.id),
            "gender": "Male",
            "session_year_id": str(self.session_year.id),
            # profile_pic é opcional
        }
        form = AddStudentForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_missing_email(self):
        """Verifica se o form fica inválido quando falta o campo email."""
        data = {
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "address": "123 Street",
            "course_id": str(self.course.id),
            "gender": "Male",
            "session_year_id": str(self.session_year.id),
        }
        form = AddStudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_invalid_email_format(self):
        """Verifica se o form é inválido com email em formato incorreto."""
        data = {
            "email": "not-an-email",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "address": "123 Street",
            "course_id": str(self.course.id),
            "gender": "Male",
            "session_year_id": str(self.session_year.id),
        }
        form = AddStudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_invalid_course_id(self):
        """Verifica se o form é inválido quando course_id não corresponde a um Course existente."""
        data = {
            "email": "test@student.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "address": "123 Street",
            "course_id": "9999",  # Não existe
            "gender": "Male",
            "session_year_id": str(self.session_year.id),
        }
        form = AddStudentForm(data=data)
        # A validação do choice do Django não vai dar "erro" no form, mas
        # vai rejeitar a choice como inválida se não estiver na lista
        self.assertFalse(form.is_valid())
        self.assertIn("course_id", form.errors)


class TestEditStudentForm(TestCase):
    def setUp(self):
        # Cria dados para popular as choices do form
        self.course = Courses.objects.create(course_name="Test Course Edit")
        self.session_year = SessionYearModel.objects.create(
            session_start_year="2023-01-01",
            session_end_year="2023-12-31"
        )

    def test_form_valid_data(self):
        """Verifica se o EditStudentForm é válido com dados corretos."""
        data = {
            "email": "edit@student.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "username": "janesmith",
            "address": "456 Street",
            "course_id": str(self.course.id),
            "gender": "Female",
            "session_year_id": str(self.session_year.id),
        }
        form = EditStudentForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_missing_username(self):
        """Verifica se o form fica inválido quando falta o campo username."""
        data = {
            "email": "edit@student.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "address": "456 Street",
            "course_id": str(self.course.id),
            "gender": "Female",
            "session_year_id": str(self.session_year.id),
        }
        form = EditStudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_invalid_session_year(self):
        """Verifica se session_year_id inválido torna o form inválido."""
        data = {
            "email": "edit@student.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "username": "janesmith",
            "address": "456 Street",
            "course_id": str(self.course.id),
            "gender": "Female",
            "session_year_id": "9999",  # Sessão não existente
        }
        form = EditStudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("session_year_id", form.errors)
