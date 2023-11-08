from django.shortcuts import render, redirect
from django.db import models
from django.contrib.auth import login
from core.forms import UserEmployeeRegistrationForm
from django.urls import reverse

def registration_view(request):
    if request.method == "POST":
        form = UserEmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('admin:index'))
    else:
        form = UserEmployeeRegistrationForm()

    context = {"form": form}
    if form.errors:
        error_message = form.errors.get('password')
        if error_message:
            context["error_message"] = error_message[0]

    return render(request, "register.html", context)