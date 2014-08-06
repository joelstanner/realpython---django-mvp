from django.test import TestCase
from main.models import StatusReport
from main.serializers import StatusReportSerializer
from main.json_views import status_collection
from payments.models import User
from django.core import serializers
from rest_framework import status


class dummyRequest(object):
    
    class dummyUser(object):
        is_authed = True
        
        def is_authenticated(self):
            return self.is_authed
    
    def __init__(self, method, authed=True):
        self.method = method
        self.encoding = 'utf8'
        self.user = self.dummyUser()
        self.user.is_authed = authed
        self.successful_authenticator = True
        self.QUERY_PARAMS = {}
        self.META = {}
        
        
class JsonViewTests(TestCase):
    
    def test_get_collection(self):
        status = StatusReport.objects.all()
        expected_json = StatusReportSerializer(status, many=True).data
        response = status_collection(dummyRequest('GET'))
        
        self.assertEqual(expected_json, response.data)
        
    def test_get_collection_requires_auth(self):
        anon_request = dummyRequest("GET", authed=False)
        response = status_collection(anon_request)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
