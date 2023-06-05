from django.db import models

# Create your models here.
class Diary(models.Model):
    content = models.TextField()
    senti = models.TextField(null=True)
    pos = models.FloatField()
    neu = models.FloatField()
    neg = models.FloatField()
    date = models.DateTimeField()
    
class Book_Report(models.Model):
    content = models.TextField()
    keywords = models.TextField()
    image = models.ImageField()
    date = models.DateTimeField()