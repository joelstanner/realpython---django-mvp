from django.db import models

class MarketingItem(models.Model):
  img = models.CharField(max_length=255)
  heading = models.CharField(max_length=300)
  caption = models.TextField()
  button_link = models.URLField(null=True, default="register")
  button_title = models.CharField(max_length=20, default="View Details")
  