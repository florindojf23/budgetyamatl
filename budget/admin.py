from django.contrib import admin
from .models import *
admin.site.register(YearBudget)
admin.site.register(Direction)
admin.site.register(BudgetItem)
admin.site.register(Activity)