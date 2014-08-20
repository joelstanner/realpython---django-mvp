from main.permissions import IsOwnerOrReadOnly
from main.serializers import StatusReportSerializer, BadgeSerializer
from main.models import StatusReport, Badge

from rest_framework import mixins, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(('GET',))
def api_root(request):
    return Response({'status_reports': reverse('status_reports_collection',
                                               request=request),
                     'badges': reverse('badges_collection', request=request),
                     })

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