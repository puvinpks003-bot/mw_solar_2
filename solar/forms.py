from django import forms
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors pr-12', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors pr-12', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['full_name', 'mobile_number', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors', 'placeholder': 'Full Name', 'autocomplete': 'name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors', 'placeholder': 'Mobile Number', 'autocomplete': 'tel'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors', 'placeholder': 'Email Address', 'autocomplete': 'email'}),
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if not re.match(r'^\+?1?\d{9,15}$', mobile):
            raise forms.ValidationError("Enter a valid mobile number.")
        if User.objects.filter(mobile_number=mobile).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mobile

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        # Strong password validation (at least 8 chars)
        if password and len(password) < 8:
            self.add_error('password', "Password must be at least 8 characters long.")
            
        return cleaned_data

class LoginForm(forms.Form):
    mobile_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors', 'placeholder': 'Mobile Number', 'autocomplete': 'tel'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors pr-12', 'placeholder': 'Password', 'autocomplete': 'current-password'}))


class CalculatorForm(forms.Form):
    monthly_bill = forms.DecimalField(
        min_value=100, 
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-4 rounded-xl bg-gray-800 border border-gray-700 text-white text-xl focus:outline-none focus:border-blue-500 transition-colors shadow-inner', 
            'placeholder': 'e.g. 5000'
        }),
        label="Monthly Electricity Bill (₹)"
    )
