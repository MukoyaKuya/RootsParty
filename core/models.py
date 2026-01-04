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
    description = models.TextField()

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

class Product(models.Model):
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
        return self.name

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
