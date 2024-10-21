from django import forms
from .models import ShippingAddress

class ShippingForm(forms.ModelForm):

    full_name =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'full_name'}),required=True)
    email =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'email'}),required=True)
    address1 =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'address1'}),required=True)
    address2 =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'address2'}),required=False)
    city =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'city'}),required=True)
    state =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'state'}),required=False)
    zipcode =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'zipcode'}),required=False)
    country =  forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'country'}),required=True)
   
    class Meta:
       model =  ShippingAddress
       fields = ['full_name','email','address1','address2','city','state','zipcode','country']

       exclude = ['user']

class PaymentForm(forms.Form):
    card_name = forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name on card'}),required=True)
    card_number =forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Card Number'}),required=True)
    card_exp_date =forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Expiry date'}),required=True)
    card_cvv = forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'cvv'}),required=True)