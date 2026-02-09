from django.contrib import admin
from django.utils.html import mark_safe
from django.urls import reverse
from unfold.admin import ModelAdmin
from image_cropping import ImageCroppingMixin

from .models import LeadershipRole, Aspirant, AspirantRegistration


@admin.register(LeadershipRole)
class LeadershipRoleAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'icon_svg_path')
        }),
        ('Role Details', {
            'fields': ('description', 'responsibilities', 'roots_context', 'prospects')
        }),
        ('Candidate Info', {
            'fields': ('candidate_name', 'image', 'video_url')
        }),
    )


@admin.register(Aspirant)
class AspirantAdmin(ImageCroppingMixin, ModelAdmin):
    list_display = ('name', 'role', 'county', 'constituency', 'is_active')
    list_filter = ('role', 'is_active', 'county', 'constituency__county')
    search_fields = ('name', 'county__name', 'constituency__name', 'description')
    list_editable = ('is_active',)
    autocomplete_fields = ['county', 'constituency']

    fieldsets = (
        (None, {
            'fields': ('role', 'name', 'is_active')
        }),
        ('Jurisdiction', {
            'fields': ('county', 'constituency', 'ward'),
            'description': "Select County for Governor/Senator. Select Constituency for MP. Select Ward for MCA."
        }),
        ('Media', {
            'fields': ('profile_image', 'cropping', 'video_url')
        }),
        ('Profile', {
            'fields': ('description', 'manifesto')
        }),
        ('Social Media', {
            'fields': ('social_handle_twitter', 'social_handle_facebook')
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Ensure ImageCropWidget is used for cropping fields"""
        from image_cropping.fields import ImageRatioField
        from image_cropping.widgets import ImageCropWidget

        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if isinstance(db_field, ImageRatioField):
            formfield.widget = ImageCropWidget()

        return formfield


@admin.register(AspirantRegistration)
class AspirantRegistrationAdmin(ModelAdmin):
    list_display = ('surname', 'other_names', 'position', 'county', 'is_verified', 'membership_status', 'created_at', 'admin_photo_thumbnail', 'download_pdf_link')
    list_filter = ('position', 'county', 'is_verified', 'membership_status', 'created_at')
    search_fields = ('surname', 'other_names', 'id_number', 'phone_number', 'county__name', 'constituency', 'ward')
    list_editable = ('is_verified',)
    readonly_fields = ('admin_photo', 'download_pdf_button', 'created_at', 'updated_at')
    ordering = ['-created_at']
    actions = ['approve_aspirants', 'reject_aspirants']

    def approve_aspirants(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count} applications marked as Approved.")
    approve_aspirants.short_description = "Approve selected applications"

    def reject_aspirants(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} applications marked as Rejected.")
    reject_aspirants.short_description = "Reject selected applications"

    fieldsets = (
        ('Actions', {
            'fields': ('download_pdf_button', 'admin_photo', 'is_verified')
        }),
        ('Personal Information', {
            'fields': ('surname', 'other_names', 'id_number', 'date_of_birth', 'photo')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'email')
        }),
        ('Position of Interest', {
            'fields': ('position', 'is_incumbent', 'membership_status')
        }),
        ('Jurisdiction', {
            'fields': ('county', 'constituency', 'ward'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'draft_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Declaration', {
            'fields': ('agreed_to_terms',)
        }),
    )

    def admin_photo_thumbnail(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50" height="50" style="object-fit:cover; border-radius:50%;" />')
        return "-"
    admin_photo_thumbnail.short_description = 'Photo'

    def admin_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="300" style="max-width:100%; height:auto; border-radius:8px; border: 4px solid #1a1a1a;" />')
        return "No Photo"
    admin_photo.short_description = 'Passport Photo Preview'

    def download_pdf_link(self, obj):
        url = reverse('aspirants:download_aspirant_pdf', args=[obj.id])
        return mark_safe(f'<a href="{url}" target="_blank" style="color:#d32f2f; font-weight:bold;">PDF</a>')
    download_pdf_link.short_description = 'PDF'

    def download_pdf_button(self, obj):
        if obj.id:
            url = reverse('aspirants:download_aspirant_pdf', args=[obj.id])
            return mark_safe(f'''
                <a href="{url}" target="_blank" class="button" style="background-color:#d32f2f; color:white; padding:10px 15px; text-decoration:none; border-radius:4px; font-weight:bold;">
                    Download Official Profile (PDF)
                </a>
            ''')
        return "-"
    download_pdf_button.short_description = 'Export Profile'

    def save_model(self, request, obj, form, change):
        """Override to invalidate cache when aspirant is saved."""
        super().save_model(request, obj, form, change)
        from core.cache_utils import invalidate_aspirant_cache
        invalidate_aspirant_cache()

    def delete_model(self, request, obj):
        """Override to invalidate cache when aspirant is deleted."""
        super().delete_model(request, obj)
        from core.cache_utils import invalidate_aspirant_cache
        invalidate_aspirant_cache()
