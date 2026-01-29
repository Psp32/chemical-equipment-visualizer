from django.contrib import admin
from .models import EquipmentDataset, EquipmentData


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(EquipmentData)
class EquipmentDataAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name', 'equipment_type']
