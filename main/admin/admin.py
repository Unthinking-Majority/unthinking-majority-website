from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from main import models
from main.admin.autocomplete_filters import AccountsFilter, BoardFilter, ContentFilter


class ContentCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ContentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_display = ['name', 'category', 'metric', 'metric_name', 'order']
    list_editable = ['order']
    list_filter = [
        AutocompleteFilterFactory('Content Category', 'category'),
    ]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'category',
                ('metric', 'metric_name'),
                ('ordering', 'order'),
                'icon',
            ),
        }),
        ('Options', {
            'fields': (
                'slug',
            ),
            'classes': (
                'collapse',
            ),
        }),
    )


class BoardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['content']
    list_display = ['name', 'content', 'team_size', 'flex_order']
    list_editable = ['flex_order']
    list_filter = [
        AutocompleteFilterFactory('Content Category', 'content__category'),
        ContentFilter,
    ]
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'content',
                'team_size',
                'flex_order'
            ),
        }),
    )


class PetAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.ContentCategory, ContentCategoryAdmin)
admin.site.register(models.Content, ContentAdmin)
admin.site.register(models.Pet, PetAdmin)
