from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response

from .views import index
from payments.models import User

import mock

class MainPageTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request = request_factory.get('/')
        cls.request.session = {}

    def test_root_resolves_to_main_view(self):
        main_page = resolve('/')
        self.assertEqual(main_page.func, index)

    def test_returns_appropriate_html_respos_code(self):
        resp = index(self.request)
        self.assertEquals(resp.status_code,200)

    def test_returns_exact_html(self):
        resp = index(self.request)
        self.assertEquals(resp.content,
                          render_to_response("index.html").content)

    def test_index_handles_logged_in_user(self):
        #create the user needed for user lookup from index page, but note we are not saving to the database
        user = User(
            name = 'jj',
            email = 'j@j.com',
        )

        #create a session that appears to have a logged in user
        self.request.session = {"user": "1"}

        with mock.patch('main.views.User') as user_mock:

            #tell the mock what to do when called
            config = {'get.return_value':user}
            user_mock.objects.configure_mock(**config)

        #run the test
        resp = index(self.request)

        #ensure we return the state of the session back to normal so we don't affect other tests
        self.request.session = {}

        #verify it returns the page for the logged in user
        expectedHtml = render_to_response('user.html', {'user':user}).content
        self.assertEquals(resp.content, expectedHtml)
