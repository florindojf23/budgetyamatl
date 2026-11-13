from django.urls import path
from documents import views
from . import views

urlpatterns = [
	path('dash/',views.ArchivalDash,name='ArchivalDash'),
	path('add/',views.ArchivalAdd,name='ArchivalAdd'),
	path('update/<str:hashid>',views.ArchivalUpdate,name='ArchivalUpdate'),
	path('detail/<str:hashid>',views.ArchivalDetail,name='ArchivalDetail'),

	# server side
	path('documents_server-side-data/', views.DocumentsServerSideJson.as_view(), name='documents_serverside_data'),
	path('documents/export/excel/', views.export_documents_excel, name='documents_export_excel'),

]