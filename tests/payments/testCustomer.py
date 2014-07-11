from payments.views import Customer
from django.test import TestCase
import mock

class CustomerTests(TestCase):
    
    def test_create_yearly_billing(self):
        with mock.patch('stripe.Customer.create') as create_mock:
            
            cust_data = {'description': 'test user', 'email': 'test@test.com',
                         'card': '4242', 'plan': 'platinum'}
            cust = Customer.create("yearly", **cust_data)
            
            create_mock.assert_called_with(**cust_data)

    def test_create_monthly_billing(self):
        
        with mock.patch('stripe.Charge.create') as charge_mock:
            
            cust_data = {'description': 'test user', 'email': 'test@test.com',
                         'card': '4242', 'plan': 'gold'}
            
            cust = Customer.create("monthly", **cust_data)
            
            charge_mock.assert_called_with(**cust_data)