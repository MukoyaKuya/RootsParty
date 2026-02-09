from django import forms
from .models import AspirantRegistration
import re
import datetime
import unicodedata

# Comprehensive list of blocked words
BLOCKED_KEYWORDS = {
    'fuck', 'shit', 'bullshit', 'asshole', 'bitch', 'bastard', 'damn', 'crap',
    'dick', 'cock', 'pussy', 'cunt', 'whore', 'slut', 'nigger', 'faggot',
    'retard', 'idiot', 'stupid', 'dumbass', 'moron', 'jackass', 'piss',
    'matako', 'mkundu', 'malaya', 'umbwa', 'makende', 'shenzi', 'mjinga',
    'punda', 'mavi', 'kuma', 'mbwa', 'fala', 'ghasia', 'takataka', 'meffi',
    'nyege', 'kutomba', 'tomba', 'kunya', 'chura', 'pumbavu', 'zuzu',
    'mboro', 'matiti', 'nugu', 'mkundu', 'poko', 'senye',
    'bitcoin', 'crypto', 'ethereum', 'btc', 'forex', 'trading', 'investment',
    'casino', 'betting', 'lottery', 'jackpot', 'prize', 'winner', 'claim',
    'telegram', 'whatsapp', 'click here', 'free money', 'earn money',
    'get rich', 'make money', 'double your', 'guaranteed', 'no risk',
    'binary options', 'mlm', 'pyramid', 'ponzi', 'scam', 'hack', 'password',
    'account', 'bank details', 'credit card', 'wallet', 'binance', 'coinbase',
    'dear friend', 'dear sir', 'congratulations', 'you have won', 'selected',
    'inheritance', 'million dollars', 'urgent reply', 'confidential',
}

def contains_non_latin(text):
    for char in text:
        if char.isalpha():
            name = unicodedata.name(char, '').lower()
            if 'latin' not in name:
                return True
    return False

def contains_blocked_keywords(text):
    text_lower = text.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

class AspirantRegistrationForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'hidden',
            'autocomplete': 'off',
            'tabindex': '-1'
        })
    )
    
    class Meta:
        model = AspirantRegistration
        fields = [
            'id_number', 'surname', 'other_names', 'phone_number', 
            'date_of_birth', 'email', 'photo', 'position', 
            'county', 'constituency', 'ward',
            'is_incumbent', 'membership_status', 'agreed_to_terms'
        ]
        widgets = {
            'id_number': forms.TextInput(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors',
                'placeholder': '12345678',
                'maxlength': '8',
                'minlength': '7',
                'pattern': '[0-9]{7,8}',
                'title': 'Enter a valid 7-8 digit ID number',
                'autocomplete': 'off',
                'hx-get': '/check-aspirant-id/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#id-error-ajax',
                'hx-swap': 'innerHTML'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors',
                'placeholder': 'Enter your last name',
                'maxlength': '50',
                'pattern': '[A-Za-z\\s\\-\']{2,50}',
                'title': 'Letters, spaces, hyphens and apostrophes only (2-50 characters)',
                'autocomplete': 'family-name'
            }),
            'other_names': forms.TextInput(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors',
                'placeholder': 'Enter your other names',
                'maxlength': '100',
                'pattern': '[A-Za-z\\s\\-\']{2,100}',
                'title': 'Letters, spaces, hyphens and apostrophes only (2-100 characters)',
                'autocomplete': 'given-name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors',
                'placeholder': '0712345678',
                'maxlength': '15',
                'pattern': '[0-9\\+]{10,15}',
                'title': 'Enter a valid phone number (10-15 digits)',
                'autocomplete': 'tel'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors',
                'type': 'date',
                'min': (datetime.date.today() - datetime.timedelta(days=110*365)).isoformat(),
                'max': (datetime.date.today() - datetime.timedelta(days=18*365)).isoformat()
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors',
                'placeholder': 'your.email@example.com',
                'maxlength': '254',
                'autocomplete': 'email'
            }),
            'position': forms.Select(attrs={
                'class': 'w-full p-3 border-4 border-roots-black font-bold focus:outline-none focus:border-roots-red transition-colors bg-white cursor-pointer'
            }),
            'membership_status': forms.RadioSelect(attrs={
                'class': 'hidden peer'
            }),
            'is_incumbent': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Spam detected.')
        return website

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number', '').strip()
        if not re.match(r'^[0-9]{7,8}$', id_number):
            raise forms.ValidationError('Enter a valid 7-8 digit ID number.')
        
        sequential_patterns = ['1234567', '12345678', '123456780', '1234567890', '7654321', '87654321', '0987654321']
        if id_number in sequential_patterns:
            raise forms.ValidationError('Please enter a valid ID number.')
        
        if len(set(id_number)) == 1:
            raise forms.ValidationError('Please enter a valid ID number.')
        
        test_patterns = ['0000000', '00000000', '9999999', '99999999']
        if id_number in test_patterns:
            raise forms.ValidationError('Please enter a valid ID number.')
        
        if AspirantRegistration.objects.filter(id_number=id_number).exclude(status='draft').exists():
            raise forms.ValidationError('This ID number has already been registered.')
        
        return id_number

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Photo must be less than 2MB.')
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if hasattr(photo, 'content_type') and photo.content_type not in allowed_types:
                raise forms.ValidationError('Only JPG and PNG images are allowed.')
        return photo

    def clean_surname(self):
        surname = self.cleaned_data.get('surname', '').strip()
        if len(surname) < 2:
            raise forms.ValidationError('Surname must be at least 2 characters.')
        if len(surname) > 50:
            raise forms.ValidationError('Surname cannot exceed 50 characters.')
        if re.search(r'[0-9]', surname):
            raise forms.ValidationError('Surname cannot contain numbers.')
        if re.search(r'https?://|www\.', surname, re.I):
            raise forms.ValidationError('URLs are not allowed.')
        if contains_non_latin(surname):
            raise forms.ValidationError('Only English/Latin letters are allowed.')
        if contains_blocked_keywords(surname):
            raise forms.ValidationError('Inappropriate content detected.')
        if not re.match(r'^[A-Za-z\s\-\']+$', surname):
            raise forms.ValidationError('Only letters, spaces, hyphens and apostrophes allowed.')
        if len(surname.split()) > 3:
             raise forms.ValidationError("Please enter a valid Last Name (too many words).")
        return surname.title()

    def clean_other_names(self):
        other_names = self.cleaned_data.get('other_names', '').strip()
        if len(other_names) < 2:
            raise forms.ValidationError('Other names must be at least 2 characters.')
        if len(other_names) > 100:
            raise forms.ValidationError('Other names cannot exceed 100 characters.')
        if re.search(r'[0-9]', other_names):
            raise forms.ValidationError('Names cannot contain numbers.')
        if re.search(r'https?://|www\.', other_names, re.I):
            raise forms.ValidationError('URLs are not allowed.')
        if contains_non_latin(other_names):
            raise forms.ValidationError('Only English/Latin letters are allowed.')
        if contains_blocked_keywords(other_names):
            raise forms.ValidationError('Inappropriate content detected.')
        if not re.match(r'^[A-Za-z\s\-\']+$', other_names):
            raise forms.ValidationError('Only letters, spaces, hyphens and apostrophes allowed.')
        if len(other_names.split()) > 5:
             raise forms.ValidationError("Please enter valid Other Names (too many words).")
        return other_names.title()

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        phone = re.sub(r'[\s\-]', '', phone)
        if not re.match(r'^[\+]?[0-9]{10,15}$', phone):
            raise forms.ValidationError('Enter a valid phone number (10-15 digits).')
        if AspirantRegistration.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('This phone number has already been registered.')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            email = email.strip().lower()
            if AspirantRegistration.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('This email address has already been registered.')
        return email

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
            if age > 110:
                raise forms.ValidationError('Please enter a valid date of birth.')
        return dob
