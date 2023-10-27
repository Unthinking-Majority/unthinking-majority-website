from django.contrib.admin.apps import AdminConfig
from django.contrib import admin


class UMAdminSite(admin.AdminSite):
    site_header = "UM Administration"
    enable_nav_sidebar = False


class UMAdminConfig(AdminConfig):
    default_site = "um.admin.UMAdminSite"
