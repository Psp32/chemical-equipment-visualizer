from rest_framework import serializers
from .models import EquipmentDataset, EquipmentData


class EquipmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentData
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    equipment = EquipmentDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'filename', 'uploaded_at', 'total_count', 'avg_flowrate', 
                  'avg_pressure', 'avg_temperature', 'equipment_type_distribution', 'equipment']


class DatasetSummarySerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    equipment_type_distribution = serializers.DictField()
