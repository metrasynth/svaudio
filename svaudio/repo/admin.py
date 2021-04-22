from django.contrib import admin

from . import models as m


@admin.register(m.File)
class FileAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Fetch)
class FetchAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Module)
class ModuleAdmin(admin.ModelAdmin):
    pass


@admin.register(m.Project)
class ProjectAdmin(admin.ModelAdmin):
    pass
