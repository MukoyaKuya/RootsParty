from django import forms
from django.core.exceptions import ValidationError
from .models import Member
from core.models import County
from core.utils.validators import (
    validate_kenyan_phone_number,
    validate_kenyan_id_number,
    validate_email
)

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
        # Use centralized validation utility
        try:
            validated_id = validate_kenyan_id_number(id_number)
        except ValidationError as e:
            raise ValidationError(str(e))
        
        # Check for duplicates
        if Member.objects.filter(id_number=validated_id).exists():
            raise ValidationError("Comrade with this ID Number already registered!")
        return validated_id
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Use centralized validation utility
        try:
            return validate_kenyan_phone_number(phone_number)
        except ValidationError as e:
            raise ValidationError(str(e))
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                return validate_email(email)
            except ValidationError as e:
                raise ValidationError(str(e))
        return email
