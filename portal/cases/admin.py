from django.contrib import admin
from .models import Case, CaseStatusLog

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title','status','tenant','created_at','updated_at','created_by')
    list_filter = ('status','tenant')
    search_fields = ('title',)
    ordering = ('-updated_at',)
    date_hierarchy = 'updated_at'

@admin.register(CaseStatusLog)
class CaseStatusLogAdmin(admin.ModelAdmin):
    list_display = ('case','old_status','new_status','changed_by','changed_at')
    list_filter = ('old_status','new_status','changed_by')
    search_fields = ('case__title',)
