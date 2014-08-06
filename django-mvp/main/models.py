from django.db import models
from datetime import datetime
#from payments.models import User


class MarketingItem(models.Model):
    img = models.CharField(max_length=255)
    heading = models.CharField(max_length=300)
    caption = models.TextField()
    button_link = models.URLField(null=True, default="register")
    button_title = models.CharField(max_length=20, default="View Details")
    
class StatusReport(models.Model):
    user = models.ForeignKey('payments.User')
    when = models.DateTimeField(blank=True)
    status = models.CharField(max_length=200)
    
    def save(self, *args, **kwargs):
        if self.when is None:
            self.when = self._getNowNoMicroseconds()
        super(StatusReport, self).save(*args, **kwargs)
        
    def _getNowNoMicroseconds(self):
        """We want to get time without microseconds, so it converts
        to JavaScript time correctly"""
        
        t = datetime.now()
        return datetime(t.year, t.month, t.day, t.hour, t.minute, t.second,
                        0, t.tzinfo)

class Announcements(models.Model):
    when = models.DateTimeField(auto_now=True)
    img = models.CharField(max_length=255, null=True)
    vid = models.URLField(null=True)
    info = models.TextField()
  
class Badge(models.Model):
    img = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    desc = models.TextField()
    
    class Meta:
        ordering = ('name',)