from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
import uuid
from users.utils_upload import upload_profile


import datetime


class Profile(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="user_profile")
	first_name = models.CharField(max_length=30, null=True, blank=True)
	last_name = models.CharField(max_length=30, null=True, blank=True)
	pob = models.CharField(max_length=50, verbose_name='Fatin Moris', null=True, blank=True)
	dob = models.DateField(verbose_name='Data Moris', null=True, blank=True)
	sex = models.CharField(choices=[('Mane','Mane'),('Feto','Feto')], max_length=6, null=True, blank=True)
	image = models.ImageField(upload_to=upload_profile, null=True, blank=True,
			validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','gif'])], verbose_name="Upload Imajen")
	date_created = models.DateTimeField(auto_now_add=True,null=True,blank=True)

	def getAge(self):
		if self.dob:
			return datetime.date.today().year - self.dob.year
		else:
			return 0
			
	def getTotalLogin(self):
		return AuditLogin.objects.filter(user=self.user).count()
		
	def __str__(self):
		template = '{0.user}, {0.first_name} {0.last_name}'
		return template.format(self)


class AuditLogin(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="audituserlogin")
	login_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)

		
	def __str__(self):
		template = '{0.user}, {0.login_time}'
		return template.format(self)
