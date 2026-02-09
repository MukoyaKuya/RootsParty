from django.db import models
from django.utils.text import slugify

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='vendors/', blank=True, null=True, help_text="Shop Logo or Banner")
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False, help_text="Verified/Official Roots Party vendor")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_vendor'

    def save(self, *args, **kwargs):
        if not self.slug:
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
    
    class Meta:
        db_table = 'core_product'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} ({self.vendor.name if self.vendor else 'No Vendor'})"

class VendorReport(models.Model):
    ISSUE_CHOICES = [
        ('fake_product', 'Fake/Counterfeit Product'),
        ('wrong_price', 'Incorrect Price'),
        ('unresponsive', 'Unresponsive/Delayed Response'),
        ('scam', 'Potential Scam/Fraud'),
        ('inappropriate', 'Inappropriate Content/Language'),
        ('other', 'Other Issue'),
    ]
    
    vendor = models.ForeignKey(Vendor, related_name='reports', on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    description = models.TextField()
    email = models.EmailField(blank=True, null=True, help_text="Optional: Your email for follow-up")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        db_table = 'core_vendor_report'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.vendor.name} - {self.get_issue_type_display()}"


class VendorApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    full_name = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    
    # Location Details
    county = models.ForeignKey('core.County', on_delete=models.SET_NULL, null=True, blank=True)
    constituency = models.CharField(max_length=100, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, help_text="Specific Address or Market (e.g. River Road, Cara House)")
    product_categories = models.CharField(max_length=300, help_text="e.g., Apparel, Art, Accessories, CBD")
    business_description = models.TextField(help_text="Describe what you sell and how it aligns with Roots Party values.")
    social_links = models.TextField(blank=True, help_text="Links to your Instagram, Twitter, or Website")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Internal notes from party leadership")

    class Meta:
        db_table = 'core_vendor_application'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} - {self.full_name}"
