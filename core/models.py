from django.db import models

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
