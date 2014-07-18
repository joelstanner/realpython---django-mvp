from payments.views import sign_in, sign_out, register, edit
from django.test import TestCase, RequestFactory
from payments.models import User, Unpaid_users
from django.db import IntegrityError

import mock
import socket

from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response
from payments.forms import SigninForm, CardForm, UserForm
from django import forms


class ViewTesterMixin(object):

    @classmethod
    def setupViewTester(cls, url, view_func, expected_html,
                        status_code = 200, session={}):
        from django.test import RequestFactory
        request_factory = RequestFactory()
        cls.request = request_factory.get(url)
        cls.request.session = session
        cls.status_code = status_code
        cls.url = url
        cls.view_func = staticmethod(view_func)
        cls.expected_html = expected_html

    def test_resolves_to_correct_view(self):
        test_view = resolve(self.url)
        self.assertEqual(test_view.func, self.view_func)

    def test_returns_appropriate_response_code(self):
        resp = self.view_func(self.request)
        self.assertEqual(resp.status_code, self.status_code)

    def test_returns_correct_html(self):
        resp = self.view_func(self.request)
        self.assertEqual(resp.content, self.expected_html)

class SignInPageTests(TestCase, ViewTesterMixin):

    @classmethod
    def setUpClass(cls):
        html = render_to_response('sign_in.html',
        {
          'form': SigninForm(),
          'user': None
        })
        ViewTesterMixin.setupViewTester('/sign_in', sign_in, html.content)

class SignOutPageTests(TestCase, ViewTesterMixin):

    @classmethod
    def setUpClass(cls):
        ViewTesterMixin.setupViewTester('/sign_out', sign_out, b'', #redirect returns empty bytestring
                                        status_code=302,
                                        session={"user":"dummy"},
                                        )

    def setUp(self):
        #sign_out clears the session, so let's reset it every time
        self.request.session = {"user":"dummy"}


import mvp.settings as settings
from payments.views import soon

class RegisterPageTests(TestCase, ViewTesterMixin):

    @classmethod
    def setUpClass(cls):
        html = render_to_response('register.html',
                                  {
                                    'form': UserForm(),
                                    'months': list(range(1,12)),
                                    'publishable': settings.STRIPE_PUBLISHABLE,
                                    'soon': soon(),
                                    'user': None,
                                    'years': list(range(2011, 2036)),
                                  })
        ViewTesterMixin.setupViewTester('/register',
                                        register,
                                        html.content,
                                        )

    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get(self.url)

    def test_invalid_form_returns_registration_page(self):

        with mock.patch('payments.forms.UserForm.is_valid') as user_mock:

            user_mock.return_value = False

            self.request.method = 'POST'
            self.request.POST = None
            resp = register(self.request)
            self.assertEqual(resp.content, self.expected_html)

            #make sure that we did indeed call our is_valid function
            self.assertEqual(user_mock.call_count, 1)

    def get_mock_cust():
        class mock_cust():
            @property
            def id(self):
                return 1234
            
        return mock_cust()
    
    @mock.patch('payments.views.Customer.create',
                return_value = get_mock_cust())
    def test_registering_new_user_returns_successfully(self, stripe_mock):

        self.request.session = {}
        self.request.method = 'POST'
        self.request.POST = {'email' : 'python@rocks.com',
                             'name' : 'pyRock',
                             'stripe_token' : '...',
                             'last_4_digits' : '4242',
                             'password' : 'bad_password',
                             'ver_password' : 'bad_password',
                             'sub_type' : 'yearly',
                             }

        resp = register(self.request)

        self.assertEqual(resp.content, b"")
        self.assertEqual(resp.status_code, 302)
        
        users = User.objects.filter(email="python@rocks.com")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].stripe_id, '1234')

    #MockUserForm made for tests
    def get_MockUserForm(self):
        from django import forms

        class MockUserForm(forms.Form):

            def is_valid(self):
                return True

            @property
            def cleaned_data(self):
                return{'email': 'python@rocks.com',
                       'name': 'pyRock',
                       'stripe_token' : '...',
                       'last_4_digits': '4242',
                       'password': 'bad_password',
                       'ver_password:': 'bad_password',
                       'sub_type': 'yearly'
                       }

            def addError(self, error):
                pass

        return MockUserForm()

    @mock.patch('payments.views.UserForm', get_MockUserForm)
    @mock.patch('payments.models.User.save', side_effect=IntegrityError)
    def test_registering_user_twice_causes_error_msg(self, save_mock):

        #now create the request used to test the view
        self.request.session = {}
        self.request.method = 'POST'
        self.request.POST = {}

        #create the expected HTML
        html = render_to_response('register.html',
                                  {'form': self.get_MockUserForm,
                                   'months': list(range(1, 12)),
                                   'publishable': settings.STRIPE_PUBLISHABLE,
                                   'soon': soon(),
                                   'user': None,
                                   'years': list(range(2011, 2036)),
                                   })

        #mock out stripe so we don't hit their server
        with mock.patch('stripe.Customer') as stripe_mock:

            config = {'create.return_value': mock.Mock()}
            stripe_mock.configure_mock(**config)

            #run the test
            resp = register(self.request)

            #verify that we did things correctly
            self.assertEqual(resp.content, html.content)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self.request.session, {})

            #assert there are no records in the database
            users = User.objects.filter(email="python@rocks.com")
            self.assertEqual(len(users), 0)

    def test_registering_user_when_stripe_is_down(self):

        #create the request used to test the view
        self.request.session = {}
        self.request.method = 'POST'
        self.request.POST = {'email' : 'python@rocks.com',
                             'name' : 'pyRock',
                             'stripe_token' : '...',
                             'last_4_digits' : '4242',
                             'password' : 'bad_password',
                             'ver_password' : 'bad_password',
                             'sub_type' : 'yearly',
                             }

        #mock stripe and ask it to throw a connection error
        with mock.patch('stripe.Customer.create', side_effect =
                        socket.error("Can't connect to Stripe")) as stripe_mock:

            #run the test
            resp = register(self.request)

            #assert the is a record in the database without Stripe ID.
            users = User.objects.filter(email="python@rocks.com")
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].stripe_id, '')
            
        #check the associated table got created
        unpaid = Unpaid_users.objects.filter(email="python@rocks.com")
        self.assertEqual(len(unpaid), 1)
        self.assertIsNotNone(unpaid[0].last_notification)

class EditPageTests(TestCase, ViewTesterMixin):

    @classmethod
    def setUpClass(cls):
        ViewTesterMixin.setupViewTester('/edit',
                                        edit,
                                        b'', #redirect returns no html
                                        status_code=302,
                                        )
