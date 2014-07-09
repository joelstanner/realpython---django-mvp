import unittest
from django.test import TestCase, SimpleTestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response
from django import forms

from pprint import pformat

from .views import index
from payments.models import User
from payments.forms import SigninForm, UserForm

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
            expectedHtml = render_to_response('user.html',
                                              {'user':user_mock.get_by_id(1)})
            self.assertEqual(resp.content, expectedHtml.content)

class UserModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_user = User(email = "j@j.com", name = 'test user')
        cls.test_user.save()

    def test_user_to_string_print_email(self):
        self.assertEqual(str(self.test_user), "j@j.com")

    def test_get_by_id(self):
        self.assertEqual(User.get_by_id(1), self.test_user)

class FormTesterMixin():

    def assertFormError(self, form_cls, expected_error_name,
                        expected_error_msg, data):

        test_form = form_cls(data=data)
        #if we get an error then the form should not be valid
        self.assertFalse(test_form.is_valid())

        self.assertEqual(test_form.errors[expected_error_name],
                         expected_error_msg,
                         msg = 'Expected %s : Actual %s : using data %s' %
                         (test_form.errors[expected_error_name],
                          expected_error_msg, pformat(data)))

class FormTests(FormTesterMixin, SimpleTestCase):

    def test_signin_form_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {'data': {'email' : 'j@j.com'},
             'error': ('password' , [u'This field is required.'])},
            {'data': {'password' : '1234'},
             'error' : ('email', [u'This field is required.'])}
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(SigninForm,
                                 invalid_data['error'][0],
                                 invalid_data['error'][1],
                                 invalid_data['data'])

    def test_user_form_passwords_match(self):
        form = UserForm({'name' : 'jj', 'email' : 'j@j.com',
                         'password' : '1234', 'ver_password' : '1234',
                         'last_4_digits' : '3333', 'stripe_token': '1'})
        
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())
        
    def test_user_form_passwords_dont_match_throws_error(self):
        form = UserForm({'name' : 'jj', 'email' : 'j@j.com',
                         'password' : '123', 'ver_password' : '1234',
                         'last_4_digits' : '3333', 'stripe_token': '1'})
        
        self.assertFalse(form.is_valid())
                
        self.assertRaisesMessage(forms.ValidationError,
                                 'Passswords do not match', form.clean)
