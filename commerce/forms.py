from django import forms
from .models import VendorReport, VendorApplication
from core.utils.validators import validate_email, validate_kenyan_phone_number


def _clean_short_text(value, field_name, max_words=20):
    value = (value or '').strip()
    if any(token in value.lower() for token in ('http://', 'https://', 'www.', '<script')):
        raise forms.ValidationError(f'{field_name} contains unsupported content.')
    if len(value.split()) > max_words:
        raise forms.ValidationError(f'{field_name} is too long.')
    return value

class VendorReportForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = VendorReport
        fields = ['issue_type', 'description', 'email']
        widgets = {
            'issue_type': forms.Select(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-lg focus:outline-none focus:border-roots-red transition-all rounded-xl'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-lg focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'rows': 5,
                'placeholder': 'Tell us what happened...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-lg focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'placeholder': 'your@email.com (optional)'
            }),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''

    def clean_description(self):
        description = (self.cleaned_data.get('description') or '').strip()
        if len(description) < 20:
            raise forms.ValidationError('Please provide at least 20 characters.')
        if len(description) > 2000:
            raise forms.ValidationError('Description cannot exceed 2000 characters.')
        return description

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return validate_email(email)
        return email


class VendorApplicationForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = VendorApplication
        fields = [
            'full_name', 'business_name', 'email', 'phone_number', 
            'county', 'constituency', 'ward', 'location', 
            'product_categories', 'business_description', 'social_links'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'placeholder': 'FULL NAME'
            }),
            'business_name': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'placeholder': 'BUSINESS NAME'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'placeholder': 'EMAIL ADDRESS'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'placeholder': 'PHONE NUMBER'
            }),
            'county': forms.Select(attrs={
                'class': "w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23000000%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E')] bg-[length:1em_1em] bg-[right_1rem_center] bg-no-repeat",
                'id': 'field-county'
            }),
            'constituency': forms.Select(attrs={
                'class': "w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23000000%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E')] bg-[length:1em_1em] bg-[right_1rem_center] bg-no-repeat",
                'id': 'field-constituency'
            }),
            'ward': forms.Select(attrs={
                'class': "w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23000000%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E')] bg-[length:1em_1em] bg-[right_1rem_center] bg-no-repeat",
                'id': 'field-ward'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'placeholder': 'STREET ADDRESS / MARKET NAME',
                'id': 'id_location'
            }),
            'product_categories': forms.HiddenInput(attrs={
                'id': 'id_product_categories'
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'rows': 4,
                'placeholder': 'DESCRIBE YOUR PRODUCTS...'
            }),
            'social_links': forms.Textarea(attrs={
                'class': 'w-full bg-white border-4 border-roots-black p-4 font-black uppercase text-base focus:outline-none focus:border-roots-red transition-all rounded-xl',
                'rows': 2,
                'placeholder': 'INSTAGRAM, TWITTER, OR WEBSITE LINKS'
            }),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''

    def clean_full_name(self):
        return _clean_short_text(self.cleaned_data.get('full_name'), 'Full name', max_words=6).title()

    def clean_business_name(self):
        return _clean_short_text(self.cleaned_data.get('business_name'), 'Business name', max_words=8)

    def clean_email(self):
        return validate_email(self.cleaned_data.get('email'))

    def clean_phone_number(self):
        return validate_kenyan_phone_number(self.cleaned_data.get('phone_number'))

    def clean_product_categories(self):
        categories = [item.strip() for item in (self.cleaned_data.get('product_categories') or '').split(',') if item.strip()]
        if not categories:
            raise forms.ValidationError('Select at least one product category.')
        if len(categories) > 4:
            raise forms.ValidationError('Select no more than 4 product categories.')
        return ', '.join(categories)

    def clean_business_description(self):
        description = (self.cleaned_data.get('business_description') or '').strip()
        if len(description) < 30:
            raise forms.ValidationError('Business description must be at least 30 characters.')
        if len(description) > 2000:
            raise forms.ValidationError('Business description cannot exceed 2000 characters.')
        return description
