from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from main import models


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
        AutocompleteFilterFactory('Content', 'content'),
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


class RecordSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['accounts', 'board']
    list_display = ['accounts_display', 'board', 'value', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Accounts', 'accounts'),
        AutocompleteFilterFactory('Board', 'board'),
    ]
    search_fields = ['accounts__name']

    fieldsets = (
        (None, {
            'fields': (
                'accounts',
                'board',
                'value',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )

    @admin.display(description='Accounts')
    def accounts_display(self, obj):
        return ", ".join(obj.accounts.values_list('name', flat=True))


class PetSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account', 'pet']
    list_display = ['account', 'pet', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [
        AutocompleteFilterFactory('Account', 'account'),
        AutocompleteFilterFactory('Pet', 'pet'),
    ]
    search_fields = ['account__name']

    fieldsets = (
        (None, {
            'fields': (
                'account',
                'pet',
                'notes',
                ('proof', 'date', 'accepted'),
            ),
        }),
    )


class ColLogSubmissionAdmin(admin.ModelAdmin):
    pass


class CASubmissionAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.ContentCategory, ContentCategoryAdmin)
admin.site.register(models.Content, ContentAdmin)
admin.site.register(models.Pet, PetAdmin)
admin.site.register(models.RecordSubmission, RecordSubmissionAdmin)
admin.site.register(models.PetSubmission, PetSubmissionAdmin)
admin.site.register(models.ColLogSubmission, ColLogSubmissionAdmin)
admin.site.register(models.CASubmission, CASubmissionAdmin)
