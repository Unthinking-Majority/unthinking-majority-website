from django.contrib import admin

from main import models
from main.admin.autocomplete_filters import BoardCategoryFilter


class BoardCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class BoardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category']
    list_display = ['name', 'category', 'metric']
    list_filter = [BoardCategoryFilter, 'metric']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'category',
                'max_team_size',
                ('metric', 'metric_name'),
                'icon',
                'slug',
            )
        }),
    )


class SubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['accounts', 'board', 'pet']
    list_display = ['account_name', 'type', 'board', 'value', 'pet', 'proof', 'date', 'accepted']
    list_editable = ['accepted']
    list_filter = [ # put m2m account filter here TODO TODO
        'type', 'board', 'date', 'accepted']
    readonly_fields = ['account_name', 'date']
    search_fields = ['account__name', 'value']

    fieldsets = (
        (None, {
            'fields': (
                'accounts',
                'type',
                ('board', 'value'),
                'pet',
                ('proof', 'date'),
                'accepted',
            )
        }),
    )

    def account_name(self, obj):
        # return obj.account.name
        return 'put accounts here'


class PetAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardCategory, BoardCategoryAdmin)
admin.site.register(models.Pet, PetAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
