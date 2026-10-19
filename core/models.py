from django.db import models

class Testimonial(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    club = models.CharField(max_length=150)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.author} ({self.role})"


class PlatformStat(models.Model):
    number = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    color = models.CharField(max_length=30, default='yellow')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.number} - {self.label}"
