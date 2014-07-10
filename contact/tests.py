from django.test import TestCase, SimpleTestCase
from .models import ContactForm
from datetime import datetime, timedelta


class UserModelTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        ContactForm(email="test@dummy.com,", name="test").save()
        ContactForm(email="j@j.com", name="jj").save()
        cls.firstUser=ContactForm(email="first@first.com",
                                  name="first",
                                  timestamp=datetime.today()+timedelta(days=2))
        cls.firstUser.save()
        
        def test_contactform_str_returns_email(self):
            self.assertEqual('first@first.com', str(self.firstUser))
            
        def test_ordering(self):
            contacts = ContactForm.objects.all()
            self.assertTrue(contacts.ordered)
            self.assertEqual(self.firstUser, contacts[0])