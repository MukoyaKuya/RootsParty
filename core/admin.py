from django.contrib import admin
from .models import Leader, LeaderImage, ManifestoItem, ManifestoEvidence, GalleryPost, PostImage, Event, Product, Resource, ContactMessage, BlogPost, County, PageContent, HomeVideo, GatePass, Vendor

class LeaderImageInline(admin.TabularInline):
    model = LeaderImage
    extra = 1

@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    inlines = [LeaderImageInline]

class EvidenceInline(admin.TabularInline):
    model = ManifestoEvidence
    extra = 1

@admin.register(ManifestoItem)
class ManifestoAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EvidenceInline]

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    max_num = 7

@admin.register(GalleryPost)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [PostImageInline]

@admin.register(GatePass)
class GatePassAdmin(admin.ModelAdmin):
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

class GatePassInline(admin.TabularInline):
    model = GatePass
    extra = 0
    readonly_fields = ('code', 'created_at')
    can_delete = False

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'is_completed', 'gate_pass_downloads')
    list_filter = ('is_completed', 'date')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GatePassInline]

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ('name', 'slug', 'price', 'is_available', 'image')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_verified')
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'is_available')
    list_filter = ('is_available', 'vendor')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'is_public')
    list_filter = ('is_public', 'uploaded_at')
    search_fields = ('title', 'description')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
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


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_featured', 'is_published', 'views', 'created_at')
    list_filter = ('category', 'is_featured', 'is_published', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_published')
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'image', 'video_url', 'video_file')
        }),
        ('Publishing', {
            'fields': ('is_featured', 'is_published')
        }),
    )


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
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

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'title', 'kpi_value')
    search_fields = ('page_name', 'title', 'content')

@admin.register(HomeVideo)
class HomeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)

