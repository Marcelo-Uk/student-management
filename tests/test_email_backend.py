from django.test import TestCase
from django.contrib.auth import get_user_model
from student_management_app.EmailBackEnd import EmailBackEnd

User = get_user_model()

class TestEmailBackEnd(TestCase):
    def setUp(self):
        # Cria um usuário com e-mail e senha válidos
        self.email = "test@example.com"
        self.password = "secret"
        self.user = User.objects.create_user(username="testuser", email=self.email, password=self.password)
        self.backend = EmailBackEnd()

    def test_authenticate_valid(self):
        """Verifica se a autenticação retorna o usuário quando o e-mail e senha estão corretos."""
        user = self.backend.authenticate(username=self.email, password=self.password)
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_wrong_password(self):
        """Verifica se a autenticação retorna None quando a senha está incorreta."""
        user = self.backend.authenticate(username=self.email, password="wrongpassword")
        self.assertIsNone(user)

    def test_authenticate_nonexistent_email(self):
        """Verifica se a autenticação retorna None quando o e-mail não existe."""
        user = self.backend.authenticate(username="nonexistent@example.com", password="secret")
        self.assertIsNone(user)

    def test_authenticate_no_username(self):
        """Verifica se a autenticação retorna None quando o username (e-mail) é None."""
        user = self.backend.authenticate(username=None, password="secret")
        self.assertIsNone(user)
