from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import SignupForm, UpdateForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
# Create your views here.

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = request.POST.get('username')
            user.birth_date = request.POST.get('birth_date')
            user.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')            
        return redirect('articles:index')
    else:
        form = SignupForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
        else:
            messages.warning(request, '아이디 혹은 비밀번호가 틀렸습니다.')
            return redirect('accounts:login')
        return redirect(request.GET.get('next') or 'articles:index')
    return render(request, 'accounts/login.html')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('articles:index')

@login_required
def update(request):
    if request.method == "POST":
        form = UpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('articles:index')
    else:
        form = UpdateForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/update.html', context)

@login_required
def delete(request):
    if request.method == 'POST':
        request.user.delete()
        auth_logout(request)
    return redirect('articles:index')

@login_required
def password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('accounts:update')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/password.html', context)

def detail(request, user_pk):
    context = {
        'user': get_object_or_404(get_user_model(), pk=user_pk),
    }
    return render(request, 'accounts/detail.html', context)

def follow(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)
    if request.user != user:
        if user.followers.filter(pk=request.user.pk).exists():
            user.followers.remove(request.user)
            is_followed = False
        else:
            user.followers.add(request.user)
            is_followed = True
        context = {
            'is_followed': is_followed,
            'followings_count': user.following.count(),
            'followers_count': user.followers.count(),
        }
        return JsonResponse(context)
    else:
        messages.warning(request, '다른 유저만 가능합니다.')
    return redirect('account:detail', user_pk)

def block(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)
    if request.user != user:
        if user.blockers.filter(pk=request.user.pk).exists():
            user.blockers.remove(request.user)
            is_blocked = False
        else:
            user.blockers.add(request.user)
            is_blocked = True
        context = {
            'is_blocked': is_blocked,
        }
        return JsonResponse(context)
    else:
        messages.warning(request, '다른 유저만 가능합니다.')
    return redirect('account:detail', user_pk)