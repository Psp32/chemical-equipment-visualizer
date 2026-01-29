from django.db import models
from django.utils import timezone


class EquipmentDataset(models.Model):
    """Model to store uploaded CSV datasets (last 5 only)"""
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    total_count = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    equipment_type_distribution = models.JSONField() 
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"


class EquipmentData(models.Model):
    """Model to store individual equipment records"""
    dataset = models.ForeignKey(EquipmentDataset, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    class Meta:
        ordering = ['equipment_name']
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
