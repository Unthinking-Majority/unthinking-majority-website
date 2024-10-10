import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.admin.apps import AdminConfig


class UMAdminSite(admin.AdminSite):
    site_header = "UM Administration"
    enable_nav_sidebar = False


class UMAdminConfig(AdminConfig):
    default_site = "um.admin.UMAdminSite"


# register adminactions to site from django-adminactions (provides things like mass update)
actions.add_to_site(site)
