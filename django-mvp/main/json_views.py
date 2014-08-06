from main.permissions import IsOwnerOrReadOnly
from main.serializers import StatusReportSerializer, BadgeSerializer
from main.models import StatusReport
from rest_framework import mixins, generics, permissions


class StatusCollection(generics.ListCreateAPIView):
    """This does GET and POST"""
    queryset = StatusReport.objects.all()
    serializer_class = StatusReportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    
class StatusMember(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, or DELETE"""
    queryset = StatusReport.objects.all()
    serializer_class = StatusReportSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

class BadgeCollection(generics.ListCreateAPIView):
    """This does GET and POST"""

    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes  = (permissions.IsAuthenticated,)
    
class BadgeMember(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, or DELETE"""
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)