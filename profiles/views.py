from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm

@login_required
def profile_view(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/profile.html', {'form': form})

@login_required
def profile_edit(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('editprofile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/profile_edit.html', {'form': form})    
