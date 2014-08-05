from django.forms import widgets
from rest_framework import serializers
from main.models import StatusReport


class StatusReportSerializer(serializers.Serializer):
    pk = serializers.Field()
    user = serializers.RelatedField(many=False)
    when = serializers.DateTimeField()
    status = serializers.CharField(max_length=200)
    
    def restore_object(self, attrs, instance=None):
        """create or update a new StatusReport instance"""
        
        if instance:
            instance.user = attrs.get('user', instance.user)
            instance.when = attrs.get('when', instance.when)
            instance.status = attrs.get('status', instance.status)
            return instance
        
        return StatusReport