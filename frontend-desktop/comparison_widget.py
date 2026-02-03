import sys
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QGridLayout, QComboBox, QScrollArea, QFrame, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE_URL = 'http://localhost:8000/api'

class ComparisonChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_comparison_bar(self, labels, values1, values2, title, ylabel):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x = range(len(labels))
        width = 0.35
        ax.bar([i - width/2 for i in x], values1, width, label='Dataset 1', color='#2E6BF0')
        ax.bar([i + width/2 for i in x], values2, width, label='Dataset 2', color='#60a5fa')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

class ComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataset1_data = None
        self.dataset2_data = None
        self.dataset1_summary = None
        self.dataset2_summary = None
        self.history_data = []
        self.auth_header = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel('Advanced Dataset Comparison')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2E6BF0; padding: 10px; border-bottom: 2px solid #2E6BF0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Dataset Selection
        selection_group = QGroupBox('Select Datasets to Compare')
        selection_layout = QGridLayout()
        
        # Dataset 1
        selection_layout.addWidget(QLabel('Dataset 1:'), 0, 0)
        self.dataset1_combo = QComboBox()
        self.dataset1_combo.setMinimumWidth(300)
        selection_layout.addWidget(self.dataset1_combo, 0, 1)
        
        # Dataset 2
        selection_layout.addWidget(QLabel('Dataset 2:'), 1, 0)
        self.dataset2_combo = QComboBox()
        self.dataset2_combo.setMinimumWidth(300)
        selection_layout.addWidget(self.dataset2_combo, 1, 1)
        
        # Compare button
        self.compare_btn = QPushButton('Compare Datasets')
        self.compare_btn.clicked.connect(self.compare_datasets)
        self.compare_btn.setStyleSheet("QPushButton { padding: 10px; font-weight: bold; }")
        selection_layout.addWidget(self.compare_btn, 2, 0, 1, 2)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # Results area with scroll
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.results_layout = QVBoxLayout()
        scroll_widget.setLayout(self.results_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
    
    def set_auth_header(self, auth_header):
        self.auth_header = auth_header
    
    def load_history(self, history_data):
        self.history_data = history_data
        
        # Clear combos
        self.dataset1_combo.clear()
        self.dataset2_combo.clear()
        
        # Add datasets to combos
        for dataset in history_data:
            display_text = f"{dataset['filename']} ({datetime.fromisoformat(dataset['uploaded_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d')})"
            self.dataset1_combo.addItem(display_text, dataset['id'])
            self.dataset2_combo.addItem(display_text, dataset['id'])
    
    def compare_datasets(self):
        if self.dataset1_combo.currentIndex() == self.dataset2_combo.currentIndex():
            QMessageBox.warning(self, 'Warning', 'Please select two different datasets')
            return
        
        dataset1_id = self.dataset1_combo.currentData()
        dataset2_id = self.dataset2_combo.currentData()
        
        # Find the datasets from history data
        dataset1 = None
        dataset2 = None
        for item in self.history_data:
            if item['id'] == dataset1_id:
                dataset1 = item
            if item['id'] == dataset2_id:
                dataset2 = item
        
        if not dataset1 or not dataset2:
            QMessageBox.warning(self, 'Error', 'Selected datasets not found in history')
            return
        
        # Use the summary data from history
        self.dataset1_summary = {
            'avg_flowrate': dataset1['avg_flowrate'],
            'avg_pressure': dataset1['avg_pressure'],
            'avg_temperature': dataset1['avg_temperature'],
            'total_count': dataset1['total_count'],
            'equipment_type_distribution': dataset1.get('equipment_type_distribution', {})
        }
        
        self.dataset2_summary = {
            'avg_flowrate': dataset2['avg_flowrate'],
            'avg_pressure': dataset2['avg_pressure'],
            'avg_temperature': dataset2['avg_temperature'],
            'total_count': dataset2['total_count'],
            'equipment_type_distribution': dataset2.get('equipment_type_distribution', {})
        }
        
        # Set dummy data for charts (since we can't get detailed data)
        self.dataset1_data = []
        self.dataset2_data = []
        
        self.display_comparison()
    
    def display_comparison(self):
        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
        # Performance Overview
        overview_group = QGroupBox('Performance Overview')
        overview_layout = QGridLayout()
        
        # Calculate performance scores
        score1 = self.calculate_performance_score(self.dataset1_summary)
        score2 = self.calculate_performance_score(self.dataset2_summary)
        winner = "Dataset 1" if score1 > score2 else "Dataset 2"
        
        # Dataset 1 card
        card1 = self.create_overview_card("Dataset 1", score1, self.dataset1_summary['total_count'], '#2E6BF0')
        overview_layout.addWidget(card1, 0, 0)
        
        # Dataset 2 card
        card2 = self.create_overview_card("Dataset 2", score2, self.dataset2_summary['total_count'], '#60a5fa')
        overview_layout.addWidget(card2, 0, 1)
        
        # Winner card
        winner_card = self.create_winner_card(winner, abs(score1 - score2))
        overview_layout.addWidget(winner_card, 0, 2)
        
        overview_group.setLayout(overview_layout)
        self.results_layout.addWidget(overview_group)
        
        # Detailed Metrics
        metrics_group = QGroupBox('Detailed Analysis')
        metrics_layout = QGridLayout()
        
        # Flowrate Analysis
        flowrate_card = self.create_metric_card(
            "Flowrate Analysis", 
            self.dataset1_summary['avg_flowrate'], 
            self.dataset2_summary['avg_flowrate'],
            "Flowrate"
        )
        metrics_layout.addWidget(flowrate_card, 0, 0)
        
        # Pressure Analysis
        pressure_card = self.create_metric_card(
            "Pressure Analysis", 
            self.dataset1_summary['avg_pressure'], 
            self.dataset2_summary['avg_pressure'],
            "Pressure"
        )
        metrics_layout.addWidget(pressure_card, 0, 1)
        
        # Temperature Analysis
        temp_card = self.create_metric_card(
            "Temperature Analysis", 
            self.dataset1_summary['avg_temperature'], 
            self.dataset2_summary['avg_temperature'],
            "Temperature"
        )
        metrics_layout.addWidget(temp_card, 0, 2)
        
        metrics_group.setLayout(metrics_layout)
        self.results_layout.addWidget(metrics_group)
        
        # Charts
        charts_group = QGroupBox('Visual Comparison')
        charts_layout = QVBoxLayout()
        
        charts_tabs = QTabWidget()
        
        # Type Distribution Chart
        type_chart = ComparisonChartWidget()
        self.plot_type_comparison(type_chart)
        charts_tabs.addTab(type_chart, 'Type Distribution')
        
        # Parameters Comparison
        param_chart = ComparisonChartWidget()
        self.plot_parameters_comparison(param_chart)
        charts_tabs.addTab(param_chart, 'Parameters Comparison')
        
        charts_layout.addWidget(charts_tabs)
        charts_group.setLayout(charts_layout)
        self.results_layout.addWidget(charts_group)
    
    def create_overview_card(self, title, score, count, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 8px;
                padding: 15px;
                background-color: white;
            }}
            QLabel {{ color: #1A1E29; }}
        """)
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(title_label)
        
        score_label = QLabel(f"{score:.1f}%")
        score_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(score_label)
        
        count_label = QLabel(f"Equipment: {count}")
        count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(count_label)
        
        card.setLayout(layout)
        return card
    
    def create_winner_card(self, winner, gap):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border: 2px solid #10b981;
                border-radius: 8px;
                padding: 15px;
                background-color: rgba(16, 185, 129, 0.1);
            }
            QLabel { color: #1A1E29; }
        """)
        layout = QVBoxLayout()
        
        title_label = QLabel("Winner")
        title_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(title_label)
        
        winner_label = QLabel(winner)
        winner_label.setStyleSheet("color: #10b981; font-size: 16px; font-weight: bold;")
        winner_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(winner_label)
        
        gap_label = QLabel(f"Gap: {gap:.1f}%")
        gap_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(gap_label)
        
        card.setLayout(layout)
        return card
    
    def create_metric_card(self, title, value1, value2, param_name):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 15px;
                background-color: white;
            }
            QLabel { color: #1A1E29; }
        """)
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 11, QFont.Bold))
        layout.addWidget(title_label)
        
        diff = value1 - value2
        percent_change = (diff / value2 * 100) if value2 != 0 else 0
        trend = "↑" if diff >= 0 else "↓"
        color = "#16a34a" if diff >= 0 else "#dc2626"
        
        values_label = QLabel(f"{value1:.2f} vs {value2:.2f}")
        values_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(values_label)
        
        diff_label = QLabel(f"{trend} {abs(percent_change):.1f}%")
        diff_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        diff_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(diff_label)
        
        card.setLayout(layout)
        return card
    
    def calculate_performance_score(self, summary):
        flow_score = min(summary['avg_flowrate'] / 5, 1) * 100
        pressure_score = min(summary['avg_pressure'] / 50, 1) * 100
        temp_score = min(summary['avg_temperature'] / 200, 1) * 100
        return (flow_score + pressure_score + temp_score) / 3
    
    def plot_type_comparison(self, chart_widget):
        types1 = list(self.dataset1_summary['equipment_type_distribution'].keys())
        types2 = list(self.dataset2_summary['equipment_type_distribution'].keys())
        all_types = list(set(types1 + types2))
        
        values1 = [self.dataset1_summary['equipment_type_distribution'].get(t, 0) for t in all_types]
        values2 = [self.dataset2_summary['equipment_type_distribution'].get(t, 0) for t in all_types]
        
        chart_widget.plot_comparison_bar(all_types, values1, values2, 'Equipment Type Distribution', 'Count')
    
    def plot_parameters_comparison(self, chart_widget):
        labels = ['Avg Flowrate', 'Avg Pressure', 'Avg Temperature']
        values1 = [
            self.dataset1_summary['avg_flowrate'],
            self.dataset1_summary['avg_pressure'],
            self.dataset1_summary['avg_temperature']
        ]
        values2 = [
            self.dataset2_summary['avg_flowrate'],
            self.dataset2_summary['avg_pressure'],
            self.dataset2_summary['avg_temperature']
        ]
        
        chart_widget.plot_comparison_bar(labels, values1, values2, 'Parameters Comparison', 'Values')
