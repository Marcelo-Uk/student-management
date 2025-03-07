from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.http import HttpResponse
from student_management_app.LoginCheckMiddleWare import LoginCheckMiddleWare
from django.contrib.auth import get_user_model

User = get_user_model()

class DummyView:
    def __call__(self, request):
        return HttpResponse("OK")

class TestLoginCheckMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = LoginCheckMiddleWare()
        self.dummy_view = DummyView()

    def set_view_module(self, module_name):
        # Define o atributo __module__ na view dummy
        self.dummy_view.__module__ = module_name

    def test_not_authenticated_redirects_to_login(self):
        # Usuário não autenticado e caminho diferente de login/doLogin
        request = self.factory.get("/some_path/")
        request.user = AnonymousUser()
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

    def test_not_authenticated_on_login_page(self):
        # Usuário não autenticado mas acessa a página de login
        request = self.factory.get(reverse("login"))
        request.user = AnonymousUser()
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNone(response)

    def test_hod_correct_module_allows_view(self):
        # Usuário HOD com view no módulo correto
        request = self.factory.get("/hod/")
        user = User.objects.create_user(username="hoduser", password="pass", user_type="1")
        request.user = user
        self.set_view_module("student_management_app.HodViews")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNone(response)

    def test_hod_wrong_module_redirects_admin_home(self):
        # Usuário HOD acessando view fora do módulo adequado
        request = self.factory.get("/hod/")
        user = User.objects.create_user(username="hoduser", password="pass", user_type="1")
        request.user = user
        self.set_view_module("student_management_app.OtherViews")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNotNone(response)
        self.assertEqual(response.url, reverse("admin_home"))

    def test_staff_correct_module_allows_view(self):
        # Usuário Staff com módulo correto
        request = self.factory.get("/staff/")
        user = User.objects.create_user(username="staffuser", password="pass", user_type="2")
        request.user = user
        self.set_view_module("student_management_app.StaffViews")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNone(response)

    def test_staff_wrong_module_redirects_staff_home(self):
        # Usuário Staff acessando view errada
        request = self.factory.get("/staff/")
        user = User.objects.create_user(username="staffuser", password="pass", user_type="2")
        request.user = user
        self.set_view_module("student_management_app.SomeOtherModule")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNotNone(response)
        self.assertEqual(response.url, reverse("staff_home"))

    def test_student_correct_module_allows_view(self):
        # Usuário Student com módulo correto
        request = self.factory.get("/student/")
        user = User.objects.create_user(username="studentuser", password="pass", user_type="3")
        request.user = user
        self.set_view_module("student_management_app.StudentViews")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNone(response)

    def test_student_wrong_module_redirects_student_home(self):
        # Usuário Student acessando view fora do módulo adequado
        request = self.factory.get("/student/")
        user = User.objects.create_user(username="studentuser", password="pass", user_type="3")
        request.user = user
        self.set_view_module("student_management_app.OtherModule")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNotNone(response)
        self.assertEqual(response.url, reverse("student_home"))

    def test_invalid_user_type_redirects_to_login(self):
        # Usuário com user_type não reconhecido
        request = self.factory.get("/invalid/")
        user = User.objects.create_user(username="invaliduser", password="pass", user_type="99")
        request.user = user
        self.set_view_module("student_management_app.HodViews")
        response = self.middleware.process_view(request, self.dummy_view, [], {})
        self.assertIsNotNone(response)
        self.assertEqual(response.url, reverse("login"))
