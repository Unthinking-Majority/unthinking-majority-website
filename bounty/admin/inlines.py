from django.contrib import admin

from bounty import models


class ExtraBountyRewardInline(admin.TabularInline):
    model = models.ExtraBountyReward
    extra = 0
