from django.contrib import admin

from main import models


class BoardAdmin(admin.ModelAdmin):
    search_fields = ['name']


class BoardCategoryAdmin(admin.ModelAdmin):
    pass


class SubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user', 'board']


admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardCategory, BoardCategoryAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
