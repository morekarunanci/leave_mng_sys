from django.db import models

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)
    
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    
    def __str__(self):
        return self.name
