from django.contrib import admin

from main import models


class BoardAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name', )}


class BoardCategoryAdmin(admin.ModelAdmin):
    pass


class SubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['account', 'board']


class PetAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardCategory, BoardCategoryAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
admin.site.register(models.Pet, PetAdmin)
