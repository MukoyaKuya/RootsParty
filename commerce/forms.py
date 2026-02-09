from django import forms
from .models import VendorReport, VendorApplication

class VendorReportForm(forms.ModelForm):
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


class VendorApplicationForm(forms.ModelForm):
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
