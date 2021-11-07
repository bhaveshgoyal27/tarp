from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User,Customer,Vendor,Item,Menu

class CustomerSignUpForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = User
		fields=['username','email','password']
		def save(self, commit=True):
			user = super().save(commit=False)
			user.is_customer=True
			if commit:
				user.save()
			return user


class VendorSignUpForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model =User
		fields=['username','email','password']
		def save(self,commit=True):
			user=super().save(commit=False)
			user.is_vendor=True
			if commit:
				user.save()
			return user

class CustomerForm(forms.ModelForm):
	class Meta:
		model = Customer
		fields =['f_name','l_name','city','phone','address']


class VendorForm(forms.ModelForm):
	class Meta:
		model = Vendor
		fields =['vname','info','location','v_logo','min_ord','status','approved']