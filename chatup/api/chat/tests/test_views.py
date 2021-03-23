from rest_framework.test import force_authenticate, APITestCase, APIRequestFactory
from django.conf import settings

from .. import models, views


class LangTestCase(APITestCase):
    fixtures = 'init',

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        self.default_found = False
        self.user = models.User.objects.get_by_natural_key('admin')
        self.codes = [lang[0] for lang in settings.LANGUAGES]

    def test_lang_view(self):
        """ Test languages response structure and values """

        request = self.factory.get('general/lang/')
        force_authenticate(request, self.user)
        response = views.LangView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['cookie_name'], settings.LANGUAGE_COOKIE_NAME)
        self.assertEqual(len(response.data['languages']), len(settings.LANGUAGES))
        self.assertEqual(list(response.data['languages'].keys()), self.codes)

        for code, data in response.data['languages'].items():
            if data['default']:
                self.assertEqual(code, settings.LANGUAGE_CODE)
                self.default_found = True
                break

        self.assertTrue(self.default_found)


class UserTestCase(APITestCase):
    fixtures = 'init',

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.user = models.User.objects.get_by_natural_key('admin')

    def test_user_view(self):
        """ Test user instance structure """

        request = self.factory.get('general/user/')
        force_authenticate(request, self.user)
        response = views.UserView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['role'], self.user.role_id)


class RoleTestCase(APITestCase):
    fixtures = 'init',

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        self.roles = models.Role.objects.all()
        self.admin_role = models.Role.objects.get(sid=models.Role.SIDS.ADMIN)
        self.user = models.User.objects.get_by_natural_key('admin')

    def test_roles_list(self):
        """ Test roles list total count, order and first element structure """

        request = self.factory.get('roles/')
        force_authenticate(request, self.user)
        response = views.RoleView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], len(self.roles))
        self.assertEqual(response.data['result'][0]['id'], self.admin_role.id)
        self.assertEqual(response.data['result'][0]['sid'], self.admin_role.sid)

    def test_roles_list_translation(self):
        """ Test translation of the 'name' field """

        request = self.factory.get('roles/')
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = settings.LANGUAGES[0][0]
        force_authenticate(request, self.user)
        response = views.RoleView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], len(self.roles))
        self.assertEqual(response.data['result'][0]['name'], self.admin_role.name)

        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = settings.LANGUAGES[1][0]
        response = views.RoleView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], len(self.roles))
        self.assertEqual(response.data['result'][0]['name'], self.admin_role.name_ru)
