from django.contrib import admin
from .models import Profile, AuditLogin
# Register your models here.
admin.site.register(Profile)
admin.site.register(AuditLogin)