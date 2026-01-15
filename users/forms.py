from django import forms
from django.core.exceptions import ValidationError
from .models import Member
from core.models import County

class JoinForm(forms.ModelForm):
    # Security Fields
    confirm_email_hidden = forms.CharField(required=False, widget=forms.HiddenInput, label="Confirm Email") # Honeypot

    # Validation Fields
    surname = forms.CharField(required=True, error_messages={'required': 'Surname is required'})
    id_number = forms.CharField(required=True, error_messages={'required': 'ID Number is required'})
    phone_number = forms.CharField(required=True, error_messages={'required': 'Phone Number is required'})
    
    class Meta:
        model = Member
        fields = [
            'surname', 'other_names', 'id_number', 'phone_number', 'email', 
            'date_of_birth', 'occupation', 'ethnicity', 'sex', 'special_interest',
            'county', 'constituency', 'ward', 'polling_center'
        ]

    def clean(self):
        cleaned_data = super().clean()
        
        # Check Honeypot
        if cleaned_data.get('confirm_email_hidden'):
             raise ValidationError("Bot detected.")
             
        return cleaned_data

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if not id_number.isdigit():
             raise ValidationError("ID Number must contain only digits.")
        if Member.objects.filter(id_number=id_number).exists():
             raise ValidationError("Comrade with this ID Number already registered!")
        return id_number
