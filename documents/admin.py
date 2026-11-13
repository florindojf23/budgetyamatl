from django.contrib import admin
from documents.models import *

# Register your models here.
admin.site.register(DocsType)
admin.site.register(DocsCategory)
admin.site.register(Documents)
admin.site.register(Entity)
admin.site.register(SubEntity)
admin.site.register(Employee)
