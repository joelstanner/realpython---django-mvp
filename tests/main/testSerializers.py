from django.test import TestCase
import unittest
from main.models import StatusReport
from payments.models import User
from main.serializers import StatusReportSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from collections import OrderedDict
from io import BytesIO


class StatusReportSerializer_Tests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.u = User(name="test", email="test@test.com")
        cls.u.save()
        
        cls.new_status = StatusReport(user=cls.u, status="hello world")
        cls.new_status.save()
        
    @classmethod
    def tearDownClass(cls):
        cls.u.delete()
        cls.new_status.delete()
        
        
    def test_model_to_dictionary(self):
        serializer = StatusReportSerializer(self.new_status)
        
        expected_dict = {'pk': self.new_status.id,
                         'user': 'test@test.com',
                         'when': self.new_status.when,
                         'status': 'hello world',
                         }
        self.assertEqual(expected_dict, serializer.data)
        
    def test_dictionary_to_json(self):
        serializer = StatusReportSerializer(self.new_status)
        content = JSONRenderer().render(serializer.data)
        
        expected_dict = OrderedDict([('pk', self.new_status.id),
                                    ('user', 'test@test.com'),
                                    ('when', self.new_status.when),
                                    ('status', 'hello world'),
                                ])
        
        expected_json = JSONRenderer().render(expected_dict)
        
        self.assertEqual(expected_json, content)
        
    def test_json_to_StatusReport(self):
        
        expected_dict = OrderedDict([('pk', self.new_status.id),
                                    ('user', 'test@test.com'),
                                    ('when', self.new_status.when),
                                    ('status', 'hello world'),
                                ])
        
        json = JSONRenderer().render(expected_dict)
        stream = BytesIO(json)
        data = JSONParser().parse(stream)
        
        serializer = StatusReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(self.new_status.status, serializer.object.status)
        self.assertEqual(self.new_status.when, serializer.object.when)
        
    