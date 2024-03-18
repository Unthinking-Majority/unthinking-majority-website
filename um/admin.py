from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class UMAdminSite(admin.AdminSite):
    site_header = "UM Administration"
    enable_nav_sidebar = False


class UMAdminConfig(AdminConfig):
    default_site = "um.admin.UMAdminSite"
