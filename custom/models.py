from django.db import models

# Create your models here.
class Core(models.Model):
    name = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, blank=True, null=True)
    logo = models.ImageField(upload_to='Owner')
    is_active = models.BooleanField(default=False)
    nu_kontaktu = models.CharField(max_length=10, blank=True, null=True)
    enderesu = models.CharField(max_length=50, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
     
    def __str__(self):
        return self.name 
    




