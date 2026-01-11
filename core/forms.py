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

