from django.urls import path
from documents import views
from . import views
from .views import direction_list

urlpatterns = [
    # YearBudget
    path('yearbudgets/', views.YearBudgetList, name='yearbudget-list'),
    path('yearbudget/add/', views.YearBudgetAdd, name='yearbudget-add'),
    path('yearbudget/<int:pk>/edit/', views.YearBudgetUpdate, name='yearbudget-edit'),
    path('yearbudget/<int:pk>/delete/', views.YearBudgetDelete, name='yearbudget-delete'),

    # Direction
    path('directions/', views.DirectionList, name='direction-list'),
    path('direction/add/', views.DirectionAdd, name='direction-add'),
    path('direction/<int:pk>/edit/', views.DirectionUpdate, name='direction-edit'),
    path('direction/<int:pk>/delete/', views.DirectionDelete, name='direction-delete'),
    path('directions/', direction_list, name='direction_list'),
	path('Direction_server-side-data/', views.DirectionServerSideJson.as_view(), name='Direction_serverside_data'),


    # BudgetItem
    path('budgetitems/', views.BudgetItemList, name='budgetitem-list'),
    path('budgetitem/add/', views.BudgetItemAdd, name='budgetitem-add'),
    path('budgetitem/<int:pk>/edit/', views.BudgetItemUpdate, name='budgetitem-edit'),
    path('budgetitem/<int:pk>/delete/', views.BudgetItemDelete, name='budgetitem-delete'),
	path('BudgetItem_server-side-data/', views.BudgetItemServerSideJson.as_view(), name='BudgetItem_serverside_data'),

    # Activity
    path('activities/', views.ActivityList, name='activity-list'),
    path('activity/add/', views.ActivityAdd, name='activity-add'),
    path('activity/<int:pk>/edit/', views.ActivityUpdate, name='activity-edit'),
    path('activity/<int:pk>/delete/', views.ActivityDelete, name='activity-delete'),
	path('BudgetActivity_server-side-data/', views.BudgetActivityServerSideJson.as_view(), name='BudgetActivity_serverside_data'),
	path('activity/export/excel/', views.activity_excel, name='activity_export_excel'),

]
