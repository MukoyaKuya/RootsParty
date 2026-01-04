from django.contrib import admin
from .models import Leader, LeaderImage, ManifestoItem, ManifestoEvidence, GalleryPost, PostImage, Event, Product, Resource

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
