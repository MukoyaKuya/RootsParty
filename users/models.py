from django.db import models

class Member(models.Model):
    full_name = models.CharField(max_length=255)
    surname = models.CharField(max_length=100, blank=True, null=True)
    other_names = models.CharField(max_length=255, blank=True, null=True)
    id_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    ethnicity = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Intersex', 'Intersex')], blank=True, null=True)
    special_interest = models.CharField(max_length=100, blank=True, null=True, choices=[('Youth', 'Youth'), ('Women', 'Women'), ('PWD', 'PWD'), ('Elderly', 'Elderly'), ('None', 'None')])
    
    # Location Details
    county = models.ForeignKey('core.County', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    constituency = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    polling_center = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.id_number})"
