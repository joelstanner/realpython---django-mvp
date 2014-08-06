from main.serializers import StatusReportSerializer
from main.models import StatusReport
from rest_framework import mixins
from rest_framework import generics


class StatusCollection(generics.ListCreateAPIView):
    """This does GET and POST"""
    queryset = StatusReport.objects.all()
    serializer_class = StatusReportSerializer
    
    
class StatusMember(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, or DELETE"""
    queryset = StatusReport.objects.all()
    serializer_class = StatusReportSerializer