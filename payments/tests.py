# ---------- PAYMENT VIEW TESTS ---------- #
import unittest
from django.test import TestCase, SimpleTestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response
from django import forms

from pprint import pformat

from .views import sign_in, sign_out, register, edit, soon
from .models import User
from .forms import SigninForm, CardForm, UserForm

import mock
import mvp.settings as settings

# ---------- USER MODEL TESTS ---------- #
class UserModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_user = User(email = "j@j.com", name = 'test user')
        cls.test_user.save()

    def test_user_to_string_print_email(self):
        self.assertEqual(str(self.test_user), "j@j.com")

    def test_get_by_id(self):
        self.assertEqual(User.get_by_id(1), self.test_user)
        
    def test_create_user_function_stores_in_database(self):
        user = User.create("test", "test@t.com", "tt", "1234", "22")
        self.assertEqual(User.objects.get(email="test@t.com"), user)
        
    def test_create_user_already_exists_throws_IntegrityError(self):
        from django.db import IntegrityError
        self.assertRaises(IntegrityError, User.create, "test user", "j@j.com",
                          "jj", "1234", 89)

# ---------- FORMS TESTS ---------- #
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
                                 'Passwords do not match', form.clean)

    def test_card_form_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {'data': {'last_4_digits': '123'},
                'error': ('last_4_digits', [u'Ensure this value has at least 4 characters (it has 3).'])},
            {'data' : {'last_4_digits': '12345'},
                'error': ('last_4_digits', [u'Ensure this value has at most 4 characters (it has 5).'])}
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(CardForm,
                                 invalid_data['error'][0],
                                 invalid_data['error'][1],
                                 invalid_data['data'])
            
# ---------- PAGE VIEWS TESTS ---------- #
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
        ViewTesterMixin.setupViewTester('/sign_out', sign_out, "", #redirect returns no html
                                        status_code=302,
                                        session={"user":"dummy"},
                                        )

    def setUp(self):
        #sign_out clears the session, so let's reset it everytime
        self.request.session = {"user":"dummy"}

class RegisterPageTests(TestCase, ViewTesterMixin):

    @classmethod
    def setUpClass(cls):
        html = render_to_response('register.html',
                                  {
                                    'form': UserForm(),
                                    'months': range(1,12),
                                    'publishable': settings.STRIPE_PUBLISHABLE,
                                    'soon': soon(),
                                    'user': None,
                                    'years': range(2011, 2036),
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
            
            #make sure that we did indeed call our is_valid funciton
            self.assertEqual(user_mock.call_count, 1)
    
    @mock.patch('stripe.Customer.create')
    @mock.patch(User, 'create')
    def test_registering_new_user_returns_successfully(self, create_mock,
                                                       stripe_mock):
        
        self.request.session = {}
        self.request.method = 'POST'
        self.request.POST = {'email' : 'python@rocks.com',
                             'name' : 'pyRock',
                             'stripe_token' : '...',
                             'last_4_digits' : '4242',
                             'password' : 'bad_password',
                             'ver_password' : 'bad_password',
                             }
        
        #get the return values of the mocks, for our checks later
        new_user = create_mock.return_value
        new_cust = stripe_mock.return_value
        
        resp = register(self.request)
        
        self.assertEqual(resp.content, "")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.request.session['user'], new_user.pk)
        #verify the user was actually stored in the db.
        
        create_mock.assert_called_with('pyRock', 'python@rocks.com',
                                       'bad_password', '4242', new_cust.id)
        
        #with mock.patch('stripe.Customer') as stripe_mock:
        #    
        #    config = {'create.return_value': mock.Mock()}
        #    stripe_mock.configure_mock(**config)
        #    
        #    resp = register(self.request)
        #    self.assertEqual(resp.content, "")
        #    self.assertEqual(resp.status_code, 302)
        #    self.assertEqual(self.request.session['user'], 1)
        #    
        #    #verify the user was actually stored in the database.
        #    #if not, this will throw an error
        #    db_user = User.objects.get(email='python@rocks.com')
        
        #resp = register(self.request)
        #self.assertEqual(resp.status_code, 200)
        #self.assertEqual(self.request.session, {})
        
    def test_registering_user_twice_cause_error_msg(self):
        
        #create a user with the same email so we get an integrity error
        user = User(name='pyRock', email='python@rocks.com')
        user.save()
        
        #now create the request used to test the view
        self.request.session = {}
        self.request.method = 'POST'
        self.request.POST = {'email' : 'python@rocks.com',
                             'name' : 'pyRock',
                             'stripe_token' : '...',
                             'last_4_digits' : '4242',
                             'password' : 'bad_password',
                             'ver_password' : 'bad_password',    
                            }
        
        #create our expected form
        expected_form = UserForm(self.request.POST)
        expected_form.is_valid()
        expected_form.addError('python@rocks.com is already a member')
        
        #create the expected html
        html = render_to_response('register.html',
                                  {'form': expected_form,
                                   'months': range(1, 12),
                                   'publishable': settings.STRIPE_PUBLISHABLE,
                                   'soon': soon(),
                                   'user': None,
                                   'years': range(2011, 2036),
                                   })
        
        #mock out stripe so we don't hit their server
        with mock.patch('stripe.Customer') as stripe_mock:
            
            config = {'create.return_value': mock.Mock()}
            stripe_mock.configure_mock(**config)
            
            #run the test
            resp = register(self.request)
            
            #verify that we did things correctly
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self.request.session, {})
            
            #assert there is only one record in the database
            users = User.objects.filter(email="python@rocks.com")
            self.assertEqual(len(users), 1)
            
            #verify HTML being returned is correct
            self.assertEqual(resp.content, html.content)

class EditPageTests(TestCase, ViewTesterMixin):

    @classmethod
    def setUpClass(cls):
        ViewTesterMixin.setupViewTester('/edit',
                                        edit,
                                        '', #redirect returns no html
                                        status_code=302,
                                        )
