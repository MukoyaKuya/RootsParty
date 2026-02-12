import uuid
from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from image_cropping import ImageRatioField

class LeadershipRole(models.Model):
    """Model for editable leadership role content"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL identifier e.g. president, governor")
    icon_svg_path = models.TextField(help_text="Paste the SVG path data (d attribute) here")
    description = models.TextField(help_text="Main role description")
    responsibilities = models.TextField(help_text="Enter each responsibility on a new line")
    roots_context = models.TextField(help_text="The Roots Mandate for this role")
    prospects = models.TextField(blank=True, help_text="Why a Roots Government? Enter each point on a new line")
    
    # Candidate specific fields
    candidate_name = models.CharField(max_length=200, blank=True, help_text="Name of the current candidate/holder")
    image = models.ImageField(upload_to='leadership/', blank=True, null=True, help_text="Candidate photo")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo link for candidate message")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_leadershiprole'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_responsibilities_list(self):
        return [line.strip() for line in self.responsibilities.split('\n') if line.strip()]

    def get_prospects_list(self):
        return [line.strip() for line in self.prospects.split('\n') if line.strip()]

    def get_embed_url(self):
        """Convert standard YouTube/Vimeo URLs to embed URLs"""
        if not self.video_url:
            return None
        
        import re
        youtube_regex = (
            r'(?:https?:\/\/)?(?:www\.)?'
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'
        )
        match = re.search(youtube_regex, self.video_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}?rel=0"
            
        if 'vimeo.com' in self.video_url:
            video_id = self.video_url.split('/')[-1]
            if video_id.isdigit():
                return f"https://player.vimeo.com/video/{video_id}"

        return self.video_url

    def get_aspirant_role_key(self):
        """Map leadership role slug to aspirant role choice"""
        slug_map = {
            'president': 'president',
            'governor': 'governor',
            'senator': 'senator',
            'woman-rep': 'woman_rep',
            'mp': 'mp',
            'mca': 'mca',
        }
        return slug_map.get(self.slug)

class Aspirant(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    ROLE_CHOICES = (
        ('president', 'President'),
        ('governor', 'Governor'),
        ('senator', 'Senator'),
        ('woman_rep', 'Woman Representative'),
        ('mp', 'Member of Parliament'),
        ('mca', 'Member of County Assembly'),
    )
    
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mp', db_index=True)
    
    # Jurisdiction - Importing from 'core.models' to maintain relations
    county = models.ForeignKey('core.County', on_delete=models.SET_NULL, null=True, blank=True, related_name='aspirant_profiles', help_text="Required for Governor, Senator, Woman Rep")
    constituency = models.ForeignKey('core.Constituency', on_delete=models.SET_NULL, null=True, blank=True, related_name='aspirant_profiles', help_text="Required for MP")
    ward = models.CharField(max_length=200, blank=True, help_text="Required for MCA")
    
    # Media
    profile_image = models.ImageField(upload_to='aspirants/', blank=True, null=True, help_text="Candidate Photo")
    cropping = ImageRatioField('profile_image', '400x400', help_text="Crop for optimal display (Square)")
    
    description = models.TextField(blank=True, help_text="Short bio or description")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo link")
    
    # Detailed profile content
    manifesto = CKEditor5Field(blank=True, config_name='extends', help_text="Candidate's specific manifesto")
    
    social_handle_twitter = models.CharField(max_length=100, blank=True)
    social_handle_facebook = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_aspirant'
        ordering = ['role', 'name']

    def __str__(self):
        ctx = ""
        if self.constituency: ctx = f" ({self.constituency.name})"
        elif self.county: ctx = f" ({self.county.name})"
        return f"{self.name} - {self.get_role_display()}{ctx}"

    def get_embed_url(self):
        """Convert standard YouTube/Vimeo URLs to embed URLs"""
        if not self.video_url:
            return None
        
        import re
        youtube_regex = (
            r'(?:https?:\/\/)?(?:www\.)?'
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'
        )
        match = re.search(youtube_regex, self.video_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}?rel=0"
            
        if 'vimeo.com' in self.video_url:
            video_id = self.video_url.split('/')[-1]
            if video_id.isdigit():
                return f"https://player.vimeo.com/video/{video_id}"

        return self.video_url

class AspirantRegistration(models.Model):
    """Model for storing aspirant registration data"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    POSITION_CHOICES = [
        ('governor', 'Governor - KES 10,000'),
        ('senator', 'Senator - KES 5,000'),
        ('woman_rep', 'Woman Representative - KES 5,000'),
        ('mp', 'Member of Parliament (MP) - KES 5,000'),
        ('mca', 'Member of County Assembly (MCA) - KES 2,000'),
    ]
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('existing', 'Existing Roots Party Member'),
        ('new', 'New Member'),
    ]
    
    APPLICATION_STATUS_CHOICES = [
        ('draft', 'Draft - Incomplete'),
        ('submitted', 'Submitted - Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id_number = models.CharField(max_length=20, verbose_name="ID Number")
    surname = models.CharField(max_length=100)
    other_names = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, help_text="Used for verification and notifications")
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address (Optional)")
    photo = models.ImageField(upload_to='aspirants/photos/', blank=True, null=True, help_text="Passport photo (JPG/PNG, max 2MB)")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, verbose_name="Select Position", blank=True)
    county = models.ForeignKey('core.County', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Target County")
    constituency = models.CharField(max_length=100, blank=True, null=True, verbose_name="Target Constituency")
    ward = models.CharField(max_length=100, blank=True, null=True, verbose_name="Target Ward")
    is_incumbent = models.BooleanField(default=False, verbose_name="Are you a current elected leader?")
    membership_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS_CHOICES, default='new', verbose_name="Party Membership Status")
    agreed_to_terms = models.BooleanField(default=False, verbose_name="I agree to the Terms and Conditions")
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='submitted', db_index=True)
    draft_token = models.CharField(max_length=64, unique=True, null=True, blank=True, help_text="Token for resuming draft applications")
    payment_status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('completed', 'Completed')])
    is_verified = models.BooleanField(default=False, verbose_name="Verified Aspirant", help_text="Check this to mark the aspirant as verified.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_aspirantregistration'
        ordering = ['-created_at']
        verbose_name = 'Aspirant Application'
        verbose_name_plural = 'Aspirant Applications'
        indexes = [
            models.Index(fields=['id_number']),
            models.Index(fields=['position']),
            models.Index(fields=['county']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.surname} {self.other_names} - {self.get_position_display()}"
    
    def save(self, *args, **kwargs):
        if not self.draft_token:
            import secrets
            self.draft_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
