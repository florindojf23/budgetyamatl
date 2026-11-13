import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from users.models import Profile,AuditLogin
from users.forms import ProfileUpdateForm,UserForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from django.urls import reverse_lazy

# Create your views here.
@login_required
def ListaUtilizadores(request):
	objects = User.objects.all()#.exclude(is_staff=True)
	print('objects:',objects)
	context = {
		'userlist_active':"active",
		'objects': objects, 
		'title': 'Lista Utilizador', 'legend': 'Lista Utilizador',
	}
	return render(request,'users/userlist.html',context)


@login_required
def ProfileUpdate(request):
	profile = Profile.objects.get(user=request.user)
	if request.method == 'POST' :
		print("tama profile")
		p_form = ProfileUpdateForm(request.POST,request.FILES, instance=profile)
		if p_form.is_valid():
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('user-profile')
	else:
		p_form = ProfileUpdateForm(instance=profile)

	context = {
		'profile_active':"active",
		'profile': profile, 'p_form': p_form,
		'title': 'Perfil', 'legend': 'Perfil',
	}
	return render(request, 'account/profile.html', context)

@login_required
def AccountUpdate(request):
	group = request.user.groups.all()[0].name
	profile = Profile.objects.get(user=request.user)
	if request.method == 'POST':
		u_form = UserForm(request.POST, instance=request.user)
		if u_form.is_valid():
			print("tama")
			u_form.save()
			messages.success(request, f'Ita boot nia konta altera ona!')
			return redirect('user-account')
	else:
		u_form = UserForm(instance=request.user)
	context = {
		'account_active':"active",
		'u_form': u_form,'profile': profile,
		'title': 'Info Konta', 'legend': 'Info Konta',
	}
	return render(request, 'account/account_settings.html', context)

@login_required
def AccountLoginHistory(request):
	group = request.user.groups.all()[0].name
	objects = AuditLogin.objects.filter(user=request.user).order_by('-login_time')
	profile = Profile.objects.get(user=request.user)
	context = {
		'loginHistory_active':"active",
		'group': group, 'objects': objects,'profile': profile,
		'accountLoginHistory': 'active','title': 'Historia Login', 'legend': 'Historia Login'
	}
	return render(request, 'account/login_history.html', context)

class UserPasswordChangeView(PasswordChangeView):
	template_name = 'account/change_password.html'
	success_url = reverse_lazy('user-change-password-done')
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['profile'] = Profile.objects.get(user=self.request.user)
		context['password_active'] = "active"
		return context

class UserPasswordChangeDoneView(PasswordResetDoneView):
	template_name = 'account/change_password_done.html'


@login_required
@allowed_users(allowed_roles=['admin'])
def resetUserPassword(request,id):
	userData = get_object_or_404(User,id=id)
	password = make_password('password')
	userData.password = password
	userData.save()
	messages.success(request, f'Password ba {userData.username} Reset ho Susesu!')
	return redirect('userlist')

@login_required
@allowed_users(allowed_roles=['admin'])
def desativuUser(request,id):
	userData = get_object_or_404(User,id=id)
	userData.is_active = False
	userData.save()
	messages.success(request, f'User {userData.username} Desativu ho Susesu!')
	return redirect('userlist')

@login_required
@allowed_users(allowed_roles=['admin'])
def ativuUser(request,id):
	userData = get_object_or_404(User,id=id)
	userData.is_active = True
	userData.save()
	messages.success(request, f'User {userData.username} Ativu ho Susesu!')
	return redirect('userlist')

@login_required
@allowed_users(allowed_roles=['admin'])
def deleteUser(request,id):
	user = get_object_or_404(User,id=id)
	user.delete()
	messages.error(request, f'Utilizador ba {user.username} Hamoos ho Susesu!')
	return redirect('userlist')