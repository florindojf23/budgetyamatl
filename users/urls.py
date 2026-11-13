from django.urls import path
from . import views
urlpatterns = [

    path('profile/', views.ProfileUpdate, name="user-profile"),
    path('my/account/', views.AccountUpdate, name='user-account'),
    path('my/account/login/history/', views.AccountLoginHistory, name='user-login-history'),
	path('change/password/', views.UserPasswordChangeView.as_view(), name='user-change-password'),
	path('change/password/done/', views.UserPasswordChangeDoneView.as_view(), name='user-change-password-done'),

    path('users-list/', views.ListaUtilizadores, name="userlist"),

    path('reset-user-password/<str:id>', views.resetUserPassword, name="resetUserPassword"),
	path('delete-user/<str:id>', views.deleteUser, name="deleteUser"),
	path('ativu-user/<str:id>', views.ativuUser, name="ativuUser"),
	path('desativu-user/<str:id>', views.desativuUser, name="desativuUser"),
]