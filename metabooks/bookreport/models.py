from django.db import models

# Create your models here.
class Book_Report(models.Model):
    content = models.TextField()
    keywords = models.TextField()
    image = models.ImageField()
    date = models.DateTimeField()