from django.contrib import admin
from .models import Leader, LeaderImage, ManifestoItem, ManifestoEvidence, GalleryPost, PostImage, Event, Product, Resource, ContactMessage, BlogPost, County, PageContent

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

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'is_completed')
    list_filter = ('is_completed', 'date')
    search_fields = ('title', 'location')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name',)
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

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'title', 'kpi_value')
    search_fields = ('page_name', 'title', 'content')
