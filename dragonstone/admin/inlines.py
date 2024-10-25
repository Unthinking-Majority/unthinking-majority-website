from django.contrib import admin

from dragonstone.models import (
    PVMSplitPoints,
    MentorPoints,
    EventHostPoints,
    EventParticipantPoints,
    EventDonorPoints,
    NewMemberRaidPoints,
    GroupCAPoints,
)

__all__ = [
    "PVMSplitPointsAdminInline",
    "MentorPointsAdminInline",
    "EventHostPointsAdminInline",
    "EventParticipantPointsAdminInline",
    "EventDonorPointsAdminInline",
]


class PVMSplitPointsAdminInline(admin.TabularInline):
    model = PVMSplitPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]


class MentorPointsAdminInline(admin.TabularInline):
    model = MentorPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]


class EventHostPointsAdminInline(admin.TabularInline):
    model = EventHostPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]


class EventParticipantPointsAdminInline(admin.TabularInline):
    model = EventParticipantPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]


class EventDonorPointsAdminInline(admin.TabularInline):
    model = EventDonorPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]


class NewMemberRaidPointsAdminInline(admin.TabularInline):
    model = NewMemberRaidPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]


class GroupCAPointsAdminInline(admin.TabularInline):
    model = GroupCAPoints
    extra = 0
    autocomplete_fields = ["account"]
    readonly_fields = ["dragonstonepoints_ptr", "points"]
    exclude = ["date"]
