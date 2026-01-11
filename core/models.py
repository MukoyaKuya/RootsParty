from django.db import models
from django.utils import timezone

class Leader(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="URL friendly name, e.g. george-wajackoyah", blank=True)
    role = models.CharField(max_length=100, help_text="e.g. Party Leader, Deputy Party Leader")
    nickname = models.CharField(max_length=100, blank=True, help_text="e.g. The Fifth")
    image = models.ImageField(upload_to='leaders/')
    bio = models.TextField(blank=True, help_text="Detailed biography.")
    twitter_handle = models.CharField(max_length=100, blank=True, help_text="@username")
    order = models.IntegerField(default=0, help_text="Higher number = earlier in list")
    
    class Meta:
        ordering = ['-order']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class LeaderImage(models.Model):
    leader = models.ForeignKey(Leader, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='leaders/gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.leader.name}"

class ManifestoItem(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL friendly name, e.g. legalize-marijuana")
    icon = models.CharField(max_length=10, help_text="Emoji icon, e.g. 🌿")
    summary = models.TextField(help_text="Short description for the main list.")
    description = models.TextField(help_text="Detailed description for the detail page.")
    local_impact = models.TextField(help_text="Impact on Kenya.", blank=True)
    target_revenue = models.CharField(max_length=200, blank=True, help_text="Optional revenue text highlight")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class ManifestoEvidence(models.Model):
    item = models.ForeignKey(ManifestoItem, on_delete=models.CASCADE, related_name='evidence')
    country = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, help_text="URL-friendly country name")
    flag_emoji = models.CharField(max_length=10, blank=True, help_text="Country flag emoji")
    description = models.TextField()
    detailed_history = models.TextField(blank=True, help_text="Comprehensive legalization history")
    timeline = models.TextField(blank=True, help_text="Key dates and milestones in JSON format")
    economic_impact = models.TextField(blank=True, help_text="Economic effects and statistics")
    lessons_for_kenya = models.TextField(blank=True, help_text="What Kenya can learn")
    annual_revenue = models.CharField(max_length=100, blank=True, help_text="Annual cannabis revenue in Ksh")

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.country)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.country} - {self.item.title}"

class GalleryPost(models.Model):
    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True, help_text="Up to 500 words.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(GalleryPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    
    def __str__(self):
        return f"Image for {self.post.title}"

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    location = models.CharField(max_length=200)
    date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    gate_pass_downloads = models.PositiveIntegerField(default=0, help_text="Number of times the gate pass has been downloaded")
    
    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.title} - {self.location}"

    @property
    def is_upcoming(self):
        return self.date > timezone.now()

class GatePass(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='passes')
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.code} - {self.event.title}"

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='vendors/', blank=True, null=True, help_text="Shop Logo or Banner")
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Verified/Official Roots Party vendor")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} ({self.vendor.name if self.vendor else 'No Vendor'})"

class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Brief description of the document")
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    def get_file_type(self):
        ext = self.file.name.split('.')[-1].lower()
        if ext in ['pdf']: return 'PDF'
        if ext in ['doc', 'docx']: return 'DOC'
        if ext in ['png', 'jpg', 'jpeg']: return 'IMG'
        return 'FILE'

    def __str__(self):
        return self.title
        
    class Meta:
        ordering = ['-uploaded_at']


class ContactMessage(models.Model):
    """Model for storing contact form submissions"""
    SUBJECT_CHOICES = [
        ('membership', 'Membership Inquiry'),
        ('donation', 'Donation Question'),
        ('media', 'Media / Press'),
        ('volunteering', 'Volunteering'),
        ('policy', 'Policy Feedback'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class PageContent(models.Model):
    """Model for editable page content (e.g. Counties page intro)"""
    page_name = models.CharField(max_length=50, unique=True, help_text="Internal ID e.g. 'counties', 'about'")
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    content = models.TextField(blank=True, help_text="Main content area")
    image = models.ImageField(upload_to='pages/', blank=True, null=True)
    kpi_value = models.IntegerField(blank=True, null=True, help_text="Optional override for main stat (e.g. Member Count)")
    
    def __str__(self):
        return self.page_name
    
    class Meta:
        verbose_name = 'Page Content'
        verbose_name_plural = 'Page Contents'


class BlogPost(models.Model):
    """Model for news and blog posts"""
    CATEGORY_CHOICES = [
        ('news', 'Party News'),
        ('press', 'Press Release'),
        ('campaign', 'Campaign Update'),
        ('policy', 'Policy Announcement'),
        ('event', 'Event Recap'),
        ('opinion', 'Opinion'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news')
    excerpt = models.TextField(max_length=300, help_text="Short summary for list views")
    content = models.TextField(help_text="Full article content (supports markdown)")
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL")
    video_file = models.FileField(upload_to='blog/videos/', blank=True, null=True, help_text="Upload video file (MP4, etc.)")
    author = models.CharField(max_length=100, default="Roots Party Media")
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    is_published = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_embed_url(self):
        """Convert standard YouTube URLs to embed URLs"""
        if not self.video_url:
            return None
        if 'youtube.com/watch?v=' in self.video_url:
            return self.video_url.replace('youtube.com/watch?v=', 'youtube.com/embed/')
        if 'youtu.be/' in self.video_url:
            return self.video_url.replace('youtu.be/', 'youtube.com/embed/')
        return self.video_url
        
    def __str__(self):
        return self.title
    
    @property
    def read_time(self):
        """Estimate read time based on word count"""
        word_count = len(self.content.split())
        minutes = max(1, word_count // 200)
        return f"{minutes} min read"


class County(models.Model):
    """Model for county presence tracking"""
    PRESENCE_CHOICES = [
        ('active', 'Active - Full Operations'),
        ('growing', 'Growing - Establishing Presence'),
        ('starting', 'Starting - Initial Contact'),
        ('planned', 'Planned - Not Yet Started'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    code = models.CharField(max_length=10, help_text="County code e.g. 001", blank=True)
    presence_status = models.CharField(max_length=20, choices=PRESENCE_CHOICES, default='planned')
    coordinator_name = models.CharField(max_length=100, blank=True)
    coordinator_phone = models.CharField(max_length=20, blank=True)
    members_count = models.PositiveIntegerField(default=0)
    offices_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='counties/', blank=True, null=True, help_text="Header image for the county page")
    description = models.TextField(blank=True, help_text="General introduction about the county")
    notes = models.TextField(blank=True, verbose_name="Economic Plan", help_text="Detailed economic revolution plan")
    
    class Meta:
        ordering = ['name']
        verbose_name = 'County'
        verbose_name_plural = 'Counties'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class HomeVideo(models.Model):
    """Model for homepage video section"""
    title = models.CharField(max_length=200, help_text="e.g. Watch The Message")
    description = models.TextField(blank=True, help_text="Short description or quote")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Upload a video file (MP4)")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL (overrides uploaded file)")
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True, help_text="Cover image for the video")
    button_text = models.CharField(max_length=50, default="View More Videos", help_text="Text for the call-to-action button")
    button_url = models.CharField(max_length=200, default="/gallery/", help_text="URL for the button")
    is_active = models.BooleanField(default=True, help_text="Only one active video will be shown")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Home Video'
        verbose_name_plural = 'Home Videos'

    def __str__(self):
        return self.title

    def get_embed_url(self):
        """Convert standard YouTube/Vimeo URLs to embed URLs"""
        if not self.video_url:
            return None
        
        # YouTube Logic
        import re
        # Support for:
        # - youtube.com/watch?v=ID
        # - youtube.com/embed/ID
        # - youtube.com/v/ID
        # - youtube.com/shorts/ID
        # - youtu.be/ID
        youtube_regex = (
            r'(?:https?:\/\/)?(?:www\.)?'
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)'
            r'([a-zA-Z0-9_-]{11})'
        )
        match = re.search(youtube_regex, self.video_url)
        if match:
            video_id = match.group(1)
            # Use youtube-nocookie and explicit origin to fix Error 153 on localhost
            return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&origin=http://127.0.0.1:8080"
            
        # Basic Vimeo Check (keep simple for now)
        if 'vimeo.com' in self.video_url:
             # Vimeo usually needs the ID extracted, simple split for now
             # format: https://vimeo.com/123456789
             video_id = self.video_url.split('/')[-1]
             if video_id.isdigit():
                 return f"https://player.vimeo.com/video/{video_id}"

        return self.video_url


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email



