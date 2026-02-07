from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-4 border-4 border-roots-black font-bold text-lg focus:outline-none focus:border-roots-red transition-colors',
            'placeholder': 'Your Full Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-4 border-4 border-roots-black font-bold text-lg focus:outline-none focus:border-roots-red transition-colors',
            'placeholder': 'your.email@example.com'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-4 border-4 border-roots-black font-bold text-lg focus:outline-none focus:border-roots-red transition-colors',
            'placeholder': '+254 7XX XXX XXX (Optional)'
        })
    )
    subject = forms.ChoiceField(
        choices=[
            ('', 'Select a Subject'),
            ('membership', 'Membership Inquiry'),
            ('donation', 'Donation Question'),
            ('media', 'Media / Press'),
            ('volunteering', 'Volunteering'),
            ('policy', 'Policy Feedback'),
            ('complaint', 'Complaint'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full p-4 border-4 border-roots-black font-bold text-lg focus:outline-none focus:border-roots-red transition-colors bg-white cursor-pointer'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-4 border-4 border-roots-black font-bold text-lg focus:outline-none focus:border-roots-red transition-colors resize-none',
            'placeholder': 'Write your message here...',
            'rows': 6
        })
    )


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'bg-white/10 border-2 border-white/20 text-white placeholder-gray-400 px-6 py-4 font-bold text-lg focus:outline-none focus:border-roots-red focus:bg-black transition-all w-full',
            'aria-label': 'Email Address'
        })
    )


from .models import AspirantRegistration
import re
import datetime
import unicodedata

# Comprehensive list of blocked words (profanity, spam, crypto, etc.)
BLOCKED_KEYWORDS = {
    # English profanity
    'fuck', 'shit', 'bullshit', 'asshole', 'bitch', 'bastard', 'damn', 'crap',
    'dick', 'cock', 'pussy', 'cunt', 'whore', 'slut', 'nigger', 'faggot',
    'retard', 'idiot', 'stupid', 'dumbass', 'moron', 'jackass', 'piss',
    
    # Swahili/Kenyan profanity
    'matako', 'mkundu', 'malaya', 'umbwa', 'makende', 'shenzi', 'mjinga',
    'punda', 'mavi', 'kuma', 'mbwa', 'fala', 'ghasia', 'takataka', 'meffi',
    'nyege', 'kutomba', 'tomba', 'kunya', 'chura', 'pumbavu', 'zuzu',
    'mboro', 'matiti', 'nugu', 'mkundu', 'poko', 'senye',

    # Spam/Crypto/Gambling keywords
    'bitcoin', 'crypto', 'ethereum', 'btc', 'forex', 'trading', 'investment',
    'casino', 'betting', 'lottery', 'jackpot', 'prize', 'winner', 'claim',
    'telegram', 'whatsapp', 'click here', 'free money', 'earn money',
    'get rich', 'make money', 'double your', 'guaranteed', 'no risk',
    'binary options', 'mlm', 'pyramid', 'ponzi', 'scam', 'hack', 'password',
    'account', 'bank details', 'credit card', 'wallet', 'binance', 'coinbase',
    
    # Common spam patterns
    'dear friend', 'dear sir', 'congratulations', 'you have won', 'selected',
    'inheritance', 'million dollars', 'urgent reply', 'confidential',
}

def contains_non_latin(text):
    """Check if text contains non-Latin characters (Cyrillic, Chinese, Arabic, etc.)"""
    for char in text:
        if char.isalpha():
            # Get the Unicode script/category
            name = unicodedata.name(char, '').lower()
            # Allow only basic Latin letters
            if 'latin' not in name:
                return True
    return False

def contains_blocked_keywords(text):
    """Check if text contains any blocked keywords"""
    text_lower = text.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def luhn_checksum(id_number):
    """Validate ID number using Luhn algorithm"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(id_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

class AspirantRegistrationForm(forms.ModelForm):
    # Honeypot field - should be left empty by humans
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
        """Honeypot field - reject if filled (bots fill hidden fields)"""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Spam detected.')
        return website

    def clean_id_number(self):
        """Validate ID number format"""
        id_number = self.cleaned_data.get('id_number', '').strip()
        if not re.match(r'^[0-9]{7,8}$', id_number):
            raise forms.ValidationError('Enter a valid 7-8 digit ID number.')
        
        # Block sequential numbers (123456, 12345678, etc.)
        sequential_patterns = [
            '1234567', '12345678', '123456780', '1234567890',
            '7654321', '87654321', '0987654321'
        ]
        if id_number in sequential_patterns:
            raise forms.ValidationError('Please enter a valid ID number.')
        
        # Block repeated digits (1111111, 22222222, etc.)
        if len(set(id_number)) == 1:
            raise forms.ValidationError('Please enter a valid ID number.')
        
        # Block common test patterns
        test_patterns = ['0000000', '00000000', '9999999', '99999999']
        if id_number in test_patterns:
            raise forms.ValidationError('Please enter a valid ID number.')
        
        # Check for duplicate ID number (exclude drafts)
        if AspirantRegistration.objects.filter(id_number=id_number).exclude(status='draft').exists():
            raise forms.ValidationError('This ID number has already been registered.')
        
        return id_number

    def clean_photo(self):
        """Validate photo upload"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size (max 2MB)
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Photo must be less than 2MB.')
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if hasattr(photo, 'content_type') and photo.content_type not in allowed_types:
                raise forms.ValidationError('Only JPG and PNG images are allowed.')
        return photo

    def clean_surname(self):
        """Validate surname - no numbers, URLs, or excessive punctuation"""
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
        """Validate other names - no numbers, URLs, or excessive punctuation"""
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
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', phone)
        if not re.match(r'^[\+]?[0-9]{10,15}$', phone):
            raise forms.ValidationError('Enter a valid phone number (10-15 digits).')
        
        # Check for duplicate phone number
        if AspirantRegistration.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('This phone number has already been registered.')
        
        return phone

    def clean_email(self):
        """Validate email and check for duplicates"""
        email = self.cleaned_data.get('email', '')
        if email:
            email = email.strip().lower()
            # Check for duplicate email
            if AspirantRegistration.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('This email address has already been registered.')
        return email

    def clean_date_of_birth(self):
        """Validate that the aspirant is between 18 and 110 years old"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
            if age > 110:
                raise forms.ValidationError('Please enter a valid date of birth.')
        return dob
