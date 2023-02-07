from django.contrib import admin

from dragonstone import models


class RecruitmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.RecruitmentSubmission, RecruitmentAdmin)
