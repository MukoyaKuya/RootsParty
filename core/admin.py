from django.contrib import admin
from django.utils.html import mark_safe
from django.urls import reverse
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Leader, LeaderImage, ManifestoItem, ManifestoEvidence, GalleryPost, PostImage, Event, Resource, ContactMessage, BlogPost, County, PageContent, HomeVideo, GatePass, NewsletterSubscriber, CarouselImage, Constituency, FloatingImage, Splash, Tribe
from .models_site_settings import SiteSettings

class LeaderImageInline(TabularInline):
    model = LeaderImage
    extra = 1

@admin.register(Leader)
class LeaderAdmin(ModelAdmin):
    list_display = ('name', 'role', 'order')
    inlines = [LeaderImageInline]

class EvidenceInline(TabularInline):
    model = ManifestoEvidence
    extra = 1

@admin.register(ManifestoItem)
class ManifestoAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EvidenceInline]

class PostImageInline(TabularInline):
    model = PostImage
    extra = 1
    max_num = 7

@admin.register(GalleryPost)
class GalleryAdmin(ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [PostImageInline]

@admin.register(GatePass)
class GatePassAdmin(ModelAdmin):
    list_display = ('code', 'event_info', 'created_at')
    list_filter = ('event__is_completed', 'event', 'created_at')
    search_fields = ('code', 'event__title')
    actions = ['delete_completed_event_passes']

    @admin.display(description='Event (Total Downloads)')
    def event_info(self, obj):
        return f"{obj.event.title} ({obj.event.gate_pass_downloads})"

    change_list_template = 'admin/core/gatepass/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_downloads'] = GatePass.objects.count()
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Delete passes for COMPLETED events")
    def delete_completed_event_passes(self, request, queryset):
        # We delete passes where the event is marked is_completed=True
        # Note: 'queryset' is what the user selected. If they select all, it works.
        # But usually actions apply to selection. 
        # If the user wants to delete *all* irrespective of selection, we might need a different approach or just instruct them to "Select All".
        # Let's stick to standard Django action behavior: apply to selected.
        # But to be helpful, let's filter the selected ones to only delete if event is completed.
        
        # Actually, standard requirement "allow admin to be able to delete the data" usually means bulk delete.
        # Let's just allow standard delete but provide the filter so they can easily find them.
        # AND provide an action that specifically deletes ONLY completed ones from the selection.
        
        deleted_count, _ = queryset.filter(event__is_completed=True).delete()
        self.message_user(request, f"Deleted {deleted_count} gate passes for completed events.")

class GatePassInline(TabularInline):
    model = GatePass
    extra = 0
    readonly_fields = ('code', 'created_at')
    can_delete = False

@admin.register(Event)
class EventAdmin(ModelAdmin):
    @display(
        description="Status",
        ordering="is_completed",
        label={
            True: "Completed",
            False: "Upcoming",
        }
    )
    def display_status(self, obj):
        return obj.is_completed

    list_display = ('title', 'location', 'date', 'display_status', 'gate_pass_downloads')
    list_filter = ('is_completed', 'date')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GatePassInline]


@admin.register(Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ('title', 'uploaded_at', 'is_public')
    list_filter = ('is_public', 'uploaded_at')
    search_fields = ('title', 'description')


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    @display(
        description="Status",
        ordering="is_read",
        label={
            True: "Read",
            False: "Unread",
        }
    )
    def display_status(self, obj):
        return obj.is_read

    list_display = ('name', 'email', 'subject', 'display_status', 'created_at')
    list_filter = ('is_read', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')
    ordering = ['-created_at']
    
    # Actions
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} message(s) marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} message(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    # Automatically mark as read when opened
    def change_view(self, request, object_id, form_url='', extra_context=None):
        ContactMessage.objects.filter(id=object_id).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)
    
    # Fieldsets for better organization
    fieldsets = (
        ('Sender Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )


from image_cropping import ImageCroppingMixin
from .widgets import ImageCropFieldWidget
from .utils.image_processing import crop_image

# Import SiteSettings after models are loaded
from .models_site_settings import SiteSettings

@admin.register(BlogPost)
class BlogPostAdmin(ImageCroppingMixin, ModelAdmin):
    actions = ['delete_selected']

    def delete_queryset(self, request, queryset):
        """
        Override bulk delete to ensure cache is invalidated.
        """
        # We can either iterate and call delete() on each instance
        # or use delete() on queryset and then invalidate manually.
        # Given we want to ensure any custom logic in delete() runs, iteration is safer
        # though slower. But for blogs, volume is low enough.
        # However, standard Django delete_selected actually uses delete() on queryset by default
        # unless we override this.
        # Let's do bulk delete then invalidate for performance, matching User expectation
        # unless there truly is critical logic in model.delete(). 
        # The only logic in model.delete() is cache invalidation.
        # So manual invalidation here is fine.
        
        count, _ = queryset.delete()
        
        from .cache_utils import invalidate_home_cache, invalidate_content_cache
        invalidate_home_cache()
        invalidate_content_cache()
        
        self.message_user(request, f"Successfully deleted {count} blog posts.")
    @display(
        description="Published",
        ordering="is_published",
        label={
            True: "Published",
            False: "Draft",
        }
    )
    def display_published(self, obj):
        return obj.is_published

    list_display = ('title', 'category', 'author', 'is_featured', 'display_published', 'views', 'created_at')
    list_filter = ('category', 'is_featured', 'is_published', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured',)
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'image', 'cropping', 'video_url', 'video_file')
        }),
        ('Publishing', {
            'fields': ('is_featured', 'is_published')
        }),
    )
    
    # Custom cropping removed to use django-image-cropping non-destructive flow
    # formfield_for_dbfield removed
    # save_model removed (except for cache invalidation which is now in model)

    class Media:
        pass
        # image_cropping automatically adds necessary assets via the widget
        # We remove the custom admin_image_crop.js as it conflicts with the library


@admin.register(County)
class CountyAdmin(ModelAdmin):
    list_display = ('name', 'code', 'presence_status', 'coordinator_name', 'members_count', 'offices_count')
    list_filter = ('presence_status',)
    search_fields = ('name', 'coordinator_name')
    list_editable = ('presence_status', 'members_count', 'offices_count')
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'code', 'presence_status')
        }),
        ('Page Content', {
            'fields': ('image', 'description', 'notes')
        }),
        ('Stats & Coordinator', {
            'fields': ('members_count', 'offices_count', 'coordinator_name', 'coordinator_phone')
        }),
    )

    def save_model(self, request, obj, form, change):
        from .cache_utils import invalidate_county_cache
        super().save_model(request, obj, form, change)
        invalidate_county_cache()

@admin.register(PageContent)
class PageContentAdmin(ModelAdmin):
    list_display = ('page_name', 'title', 'kpi_value')
    search_fields = ('page_name', 'title', 'content')

@admin.register(HomeVideo)
class HomeVideoAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ('email', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)

@admin.register(CarouselImage)
class CarouselImageAdmin(ImageCroppingMixin, ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title',)
    ordering = ['order', '-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'cropping', 'order', 'is_active')
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

    class Media:
        js = ('js/admin_crop_preview.js',)
        css = {
            'all': ('image_cropping/css/jquery.Jcrop.min.css',)
        }

@admin.register(Constituency)
class ConstituencyAdmin(ModelAdmin):
    list_display = ('name', 'county', 'slug')
    list_filter = ('county',)
    search_fields = ('name', 'county__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FloatingImage)
class FloatingImageAdmin(ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'created_at')
    list_filter = ('position', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(ImageCroppingMixin, ModelAdmin):
    """
    Admin interface for site-wide settings including logo upload.
    This is a singleton - only one instance exists.
    """
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False
    
    def get_object(self, request, object_id=None, from_field=None):
        # Always return the singleton instance
        obj, created = SiteSettings.objects.get_or_create(pk=1)
        return obj
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Ensure ImageCropWidget is used for cropping fields"""
        from image_cropping.fields import ImageRatioField
        from image_cropping.widgets import ImageCropWidget
        
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        
        if isinstance(db_field, ImageRatioField):
            formfield.widget = ImageCropWidget()
        
        return formfield
    
    list_display = ('site_name', 'site_tagline', 'updated_at')
    fieldsets = (
        ('Logo Settings', {
            'fields': ('logo', 'logo_cropping', 'logo_square'),
            'description': 'Upload the main party logo. The logo will be displayed on the homepage and throughout the site. If no logo is uploaded, the default static logo will be used.'
        }),
        ('Site Information', {
            'fields': ('site_name', 'site_tagline')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Social Media', {
            'fields': ('twitter_handle', 'facebook_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Carousel Settings', {
            'fields': ('carousel_duration',),
            'description': 'Set how long each carousel image is displayed (in milliseconds). Default is 8000ms (8 seconds). Minimum is 2000ms (2 seconds).'
        }),
    )
    
    class Media:
        js = ('js/admin_crop_preview.js',)
        css = {
            'all': ('image_cropping/css/jquery.Jcrop.min.css',)
        }


@admin.register(Splash)
class SplashAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title',)


from django_summernote.admin import SummernoteModelAdmin

@admin.register(Tribe)
class TribeAdmin(SummernoteModelAdmin, ImageCroppingMixin, ModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'slug', 'color_class', 'order')
    search_fields = ('title', 'intro', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)
    
    fieldsets = (
        ('Identity', {
            'fields': ('title', 'slug', 'order'),
            'classes': ('tab-identity',)
        }),
        ('Appearance', {
            'fields': ('color_class', 'icon', 'image', 'cropping'),
            'description': 'Customize the visual style of the tribe letter.',
        }),
        ('Letter Content', {
            'fields': ('intro', 'content'),
            'classes': ('tab-content',)
        }),
    )
