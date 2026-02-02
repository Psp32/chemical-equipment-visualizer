from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from .models import EquipmentDataset, EquipmentData
from .serializers import EquipmentDatasetSerializer, EquipmentDataSerializer, DatasetSummarySerializer


def _get_dataset(dataset_id=None):
    if dataset_id:
        try:
            return EquipmentDataset.objects.get(id=dataset_id), None
        except EquipmentDataset.DoesNotExist:
            return None, Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
    dataset = EquipmentDataset.objects.first()
    if not dataset:
        return None, Response({'error': 'No datasets available'}, status=status.HTTP_404_NOT_FOUND)
    return dataset, None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    print(f"Upload request received: {request.method}")
    print(f"Files: {request.FILES}")
    print(f"Headers: {request.headers}")
    
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    
    if not csv_file.name.endswith('.csv'):
        return Response({'error': 'Invalid file type. Please upload a CSV file.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        df = pd.read_csv(csv_file)
        
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_count = len(df)
        avg_flowrate = df['Flowrate'].mean()
        avg_pressure = df['Pressure'].mean()
        avg_temperature = df['Temperature'].mean()
        
        type_distribution = df['Type'].value_counts().to_dict()
        
        dataset = EquipmentDataset.objects.create(
            filename=csv_file.name,
            total_count=total_count,
            avg_flowrate=float(avg_flowrate),
            avg_pressure=float(avg_pressure),
            avg_temperature=float(avg_temperature),
            equipment_type_distribution=type_distribution
        )
        
        for _, row in df.iterrows():
            EquipmentData.objects.create(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=float(row['Flowrate']),
                pressure=float(row['Pressure']),
                temperature=float(row['Temperature'])
            )
        
        all_datasets = EquipmentDataset.objects.all().order_by('-uploaded_at')
        if all_datasets.count() > 5:
            datasets_to_delete = all_datasets[5:]
            for ds in datasets_to_delete:
                ds.delete()
        
        serializer = EquipmentDatasetSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary(request, dataset_id=None):
    dataset, err = _get_dataset(dataset_id)
    if err:
        return err
    data = {
        'total_count': dataset.total_count,
        'avg_flowrate': dataset.avg_flowrate,
        'avg_pressure': dataset.avg_pressure,
        'avg_temperature': dataset.avg_temperature,
        'equipment_type_distribution': dataset.equipment_type_distribution,
    }
    return Response(DatasetSummarySerializer(data).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data(request, dataset_id=None):
    dataset, err = _get_dataset(dataset_id)
    if err:
        return err
    serializer = EquipmentDataSerializer(dataset.equipment.all(), many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    datasets = EquipmentDataset.objects.all()[:5]
    serializer = EquipmentDatasetSerializer(datasets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf(request, dataset_id=None):
    dataset, err = _get_dataset(dataset_id)
    if err:
        return err

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        spaceAfter=12,
    )
    
    story.append(Paragraph("Chemical Equipment Parameter Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(f"<b>Dataset:</b> {dataset.filename}", styles['Normal']))
    story.append(Paragraph(f"<b>Uploaded:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Summary Statistics", heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment Count', str(dataset.total_count)],
        ['Average Flowrate', f"{dataset.avg_flowrate:.2f}"],
        ['Average Pressure', f"{dataset.avg_pressure:.2f}"],
        ['Average Temperature', f"{dataset.avg_temperature:.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Equipment Type Distribution", heading_style))
    type_data = [['Equipment Type', 'Count']]
    for eq_type, count in dataset.equipment_type_distribution.items():
        type_data.append([eq_type, str(count)])
    
    type_table = Table(type_data, colWidths=[3*inch, 2*inch])
    type_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(type_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Equipment Details", heading_style))
    equipment_list = dataset.equipment.all()
    equipment_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
    for eq in equipment_list:
        equipment_data.append([
            eq.equipment_name,
            eq.equipment_type,
            f"{eq.flowrate:.2f}",
            f"{eq.pressure:.2f}",
            f"{eq.temperature:.2f}"
        ])
    
    equipment_table = Table(equipment_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    equipment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(equipment_table)
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset.id}.pdf"'
    return response
