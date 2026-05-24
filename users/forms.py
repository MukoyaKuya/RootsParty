from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Member
from core.models import County
from core.utils.validators import (
    validate_kenyan_phone_number,
    validate_kenyan_id_number,
    validate_email
)


def get_recaptcha_field():
    """Return ReCaptchaField when keys are configured; bypass when testing or keys missing."""
    # Use bypass in tests (RECAPTCHA_TESTING) or when keys not configured
    if getattr(settings, 'RECAPTCHA_TESTING', False):
        return forms.CharField(required=False, widget=forms.HiddenInput(), initial='bypass')
    if getattr(settings, 'RECAPTCHA_PUBLIC_KEY', None):
        try:
            from django_recaptcha.fields import ReCaptchaField
            return ReCaptchaField()
        except ImportError:
            pass
    return forms.CharField(required=False, widget=forms.HiddenInput(), initial='bypass')


class CoordinatorRecaptchaForm(forms.Form):
    """Minimal form for coordinator reCAPTCHA validation."""
    recaptcha = get_recaptcha_field()


class JoinForm(forms.ModelForm):
    # Security Fields
    confirm_email_hidden = forms.CharField(required=False, widget=forms.HiddenInput, label="Confirm Email")  # Honeypot
    recaptcha = get_recaptcha_field()

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


class CoordinatorApplicationForm(forms.Form):
    confirm_email_hidden = forms.CharField(required=False, widget=forms.HiddenInput, label="Confirm Email")
    recaptcha = get_recaptcha_field()

    surname = forms.CharField(required=True, max_length=100)
    other_names = forms.CharField(required=True, max_length=255)
    id_number = forms.CharField(required=True, max_length=20)
    phone = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=False)
    date_of_birth = forms.DateField(required=False)
    occupation = forms.CharField(required=False, max_length=100)
    ethnicity = forms.CharField(required=False, max_length=100)
    sex = forms.ChoiceField(required=False, choices=[('', 'Select Gender')] + list(Member._meta.get_field('sex').choices))
    special_interest = forms.ChoiceField(required=False, choices=list(Member._meta.get_field('special_interest').choices))
    county = forms.ModelChoiceField(queryset=County.objects.all(), required=True)
    constituency = forms.CharField(required=True, max_length=100)
    ward = forms.CharField(required=True, max_length=100)
    polling_center = forms.CharField(required=False, max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('confirm_email_hidden'):
            raise ValidationError("Bot detected.")
        return cleaned_data

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        try:
            validated_id = validate_kenyan_id_number(id_number)
        except ValidationError as e:
            raise ValidationError(str(e))

        if Member.objects.filter(id_number=validated_id).exists():
            raise ValidationError("Comrade with this ID Number already registered!")
        return validated_id

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        try:
            return validate_kenyan_phone_number(phone)
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

    def save(self):
        data = self.cleaned_data
        full_name = f"{data['surname']} {data['other_names']}".strip()
        return Member.objects.create(
            full_name=full_name,
            surname=data['surname'],
            other_names=data['other_names'],
            id_number=data['id_number'],
            phone_number=data['phone'],
            email=data.get('email') or '',
            date_of_birth=data.get('date_of_birth'),
            occupation=data.get('occupation') or '',
            ethnicity=data.get('ethnicity') or '',
            sex=data.get('sex') or None,
            special_interest=data.get('special_interest') or 'None',
            county=data['county'],
            constituency=data['constituency'],
            ward=data['ward'],
            polling_center=data.get('polling_center') or '',
            is_coordinator_applicant=True,
        )
