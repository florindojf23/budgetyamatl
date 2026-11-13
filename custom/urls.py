from django.urls import path
from . import views
urlpatterns = [

    path('dash/', views.ConfigDash, name="config-dash"),
    path('config-update-owner-image/', views.ConfigUpdateOwnerImage, name="config-update-owner-image"),
    path('config/', views.ConfigPage, name='config-dash'),
    
    path('config-doc-types/', views.ConfigDocType, name="config-doc-types"),
    path('config-add-doc-types/', views.ConfigAddDocType, name="config-add-doc-types"),
    path('docs-type/edit/<int:pk>/', views.ConfigEditDocsType, name='config-edit-docs-type'),
    path('docs-type/delete/<int:pk>/', views.ConfigDeleteDocsType, name='config-delete-docs-type'),

    path('config-doc-cat/', views.ConfigDocCat, name="config-doc-cat"),
    path('config-add-doc-category/', views.ConfigAddDocCategory, name="config-add-doc-category"),
    path('docs-category/edit/<int:pk>/', views.ConfigEditDocsCategory, name='config-edit-docs-category'),
    path('docs-category/delete/<int:pk>/', views.ConfigDeleteDocsCategory, name='config-delete-docs-category'),

    path('config-entity/', views.ConfigEntity, name="config-entity"),
    path('config-add-entity/', views.ConfigAddEntity, name="config-add-entity"),
    path('entity/edit/<int:pk>/', views.ConfigEditEntity, name='config-edit-entity'),
    path('entity/delete/<int:pk>/', views.ConfigDeleteEntity, name='config-delete-entity'),

    path('config-sub-entity/', views.SubConfigEntity, name="config-sub-entity"),
    path('config-add-sub-entity/', views.ConfigAddSubEntity, name="config-add-sub-entity"),
    path('sub-entity/edit/<int:pk>/', views.ConfigEditSubEntity, name='config-edit-sub-entity'),

    path('config-funcionariu/', views.ConfigEmployee, name="config-funcionariu"),
    path('config-add-employee/', views.ConfigAddEmployee, name="config-add-employee"),
    path('employee/edit/<int:pk>/', views.ConfigEditEmployee, name='config-edit-employee'),

    
]