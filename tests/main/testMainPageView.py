import unittest
from django.test import TestCase, SimpleTestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response
from django import forms
from main.models import MarketingItem


from pprint import pformat

from main.views import index
from payments.models import User
from payments.forms import SigninForm, UserForm

import mock
import mvp.settings as settings


class MainPageTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request = request_factory.get('/')
        cls.request.session = {}

    def test_root_resolves_to_main_view(self):
        main_page = resolve('/')
        self.assertEqual(main_page.func, index)

    def test_returns_appropriate_html_response_code(self):
        resp = index(self.request)
        self.assertEqual(resp.status_code,200)
    
    def test_returns_exact_html(self):
        resp = index(self.request)
        market_items = MarketingItem.objects.all()
        self.assertEqual(resp.content,
                          render_to_response("main/index.html",
                                             {"marketing_items":market_items}
                                             ).content)

    def test_index_handles_logged_in_user(self):
        #create a session that appears to have a logged in user
        self.request.session = {"user": "1"}

        with mock.patch('main.views.User') as user_mock:

            #tell the mock what to do when called
            config = {'get_by_id.return_value':mock.Mock()}
            user_mock.objects.configure_mock(**config)

            #run the test
            resp = index(self.request)

            #ensure we return the state of the session back to normal so we don't affect other tests
            self.request.session = {}

            #verify it returns the page for the logged in user
            expectedHtml = render_to_response('main/user.html',
                                              {'user':user_mock.get_by_id(1)})
            self.assertEqual(resp.content, expectedHtml.content)


