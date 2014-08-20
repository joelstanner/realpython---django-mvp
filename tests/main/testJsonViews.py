from django.test import TestCase
from main.models import StatusReport, Badge
from main.serializers import StatusReportSerializer, BadgeSerializer
from main.json_views import (StatusCollection, StatusMember,
                             BadgeCollection, BadgeMember)
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from payments.models import User

import pdb
        
class JsonViewTests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.factory = APIRequestFactory()
        cls.test_user = User(id=2222, email="test@test.com")
        
    def get_request(self, method='GET', authed=True):
        request_method = getattr(self.factory, method.lower())
        request = request_method("")
        if authed:
            force_authenticate(request, self.test_user)
            
        return request
    
    def test_get_collection(self):
        status = StatusReport.objects.all()
        expected_json = StatusReportSerializer(status, many=True).data
        
        response = StatusCollection.as_view()(self.get_request())
        
        self.assertEqual(expected_json, response.data)
        
    def test_get_collection_requires_auth(self):
        response = StatusCollection.as_view()(self.get_request(authed=False))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_member(self):
        status = StatusReport.objects.get(pk=1)
        expected_json = StatusReportSerializer(status).data
        
        response = StatusMember.as_view()(self.get_request(), pk=1)
        
        self.assertEqual(expected_json, response.data)
    
    def test_delete_member(self):
        deleteable_status = StatusReport(user=self.test_user, status="testing")
        deleteable_status.save()
        
        response = StatusMember.as_view()(
                                self.get_request(method='DELETE'),
                                pk=deleteable_status.pk)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_get_badges(self):
        badges = Badge.objects.all()
        expected_json = BadgeSerializer(badges, many=True).data
        
        response = BadgeCollection.as_view()(self.get_request())
        
        self.assertEqual(expected_json, response.data)
        
    def test_get_badges_requires_auth(self):
        response = BadgeCollection.as_view()(self.get_request(authed=False))
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_get_member_badges(self):
        badges = Badge.objects.get(pk=1)
        expected_json = BadgeSerializer(badges).data
        
        response = BadgeMember.as_view()(self.get_request(), pk=1)
        
        self.assertEqual(expected_json, response.data)
        
    def test_nothing_to_return(self):
        no_status = StatusReport(user=self.test_user, status="")
        expected_json = StatusReportSerializer(no_status).data
                
        
        self.assertEqual(expected_json.get('status'), '')