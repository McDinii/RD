from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Employee, Node
from django.contrib.auth.models import User

class UserEmployeeRegistrationForm(UserCreationForm):
    first_name = forms.CharField( max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254, required=True)

    node_network = forms.ModelChoiceField(queryset=Node.objects.all(),required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "node_network")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Employee.objects.create(
                user=user,
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                active=True,
                node_network=self.cleaned_data["node_network"]
            )

        return user
