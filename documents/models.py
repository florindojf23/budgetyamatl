from django.db import models
from django.contrib.auth.models import User
from users.utils_upload import *
from django.core.validators import FileExtensionValidator

# Create your models here.

class Entity(models.Model):
    name = models.CharField( max_length=50)
    sigla = models.CharField( max_length=50)
    is_active = models.BooleanField(default=True)
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    hashed = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.name 

class SubEntity(models.Model):
    entity = models.ForeignKey(Entity, related_name='entity', on_delete=models.CASCADE)
    name = models.CharField( max_length=50)
    sigla = models.CharField( max_length=50)
    is_active = models.BooleanField(default=True)
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    hashed = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.name 

class Employee(models.Model):
    subentity = models.ForeignKey(SubEntity, related_name='subentity', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    sex = models.CharField(choices=[('Mane','Mane'),('Feto','Feto')], max_length=6, null=True, blank=True)
    dob = models.DateField(verbose_name='Data Moris', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to=upload_employee, null=True, blank=True,
			validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','gif'])], verbose_name="Upload Fotografia")
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    hashed = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.name 

class DocsType(models.Model):
    name = models.CharField( max_length=50)
    is_active = models.BooleanField(default=True)
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    hashed = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.name 
        
class DocsCategory(models.Model):
    name = models.CharField( max_length=50)
    is_active = models.BooleanField(default=True)
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    hashed = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.name 


# class Documents(models.Model):
#     category = models.ForeignKey(DocsCategory,on_delete=models.CASCADE,null=True)
#     doc_type = models.ForeignKey(DocsType,on_delete=models.CASCADE,null=True)
#     name =  models.CharField(max_length=200)
#     doc_number = models.CharField(max_length=50)
#     doc_date = models.DateField(auto_now=False, auto_now_add=False)
#     filename = models.FileField(upload_to='Documents')

#     user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
#     hashed = models.CharField(max_length=32, null=True)

#     def __str__(self):
#         return self.name 

class Documents(models.Model):
    employee = models.ForeignKey(Employee,related_name='documents',on_delete=models.CASCADE,null=True,blank=True)
    entity = models.ForeignKey(Entity,related_name='documents',on_delete=models.CASCADE,null=True,blank=True)
    category = models.ForeignKey(DocsCategory, on_delete=models.SET_NULL, null=True, blank=True)
    doc_type = models.ForeignKey( DocsType,on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=200)
    doc_number = models.CharField(max_length=50, unique=True)
    doc_date = models.DateField()
    filename = models.FileField(upload_to='Documents')
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    hashed = models.CharField(max_length=32, null=True)

    def __str__(self):
        return f"{self.name} - {self.employee.name}"

