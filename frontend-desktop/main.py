import sys
import base64
import requests
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QTabWidget,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QScrollArea,
    QFrame,
    QSplitter,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from comparison_widget import ComparisonWidget

API_BASE_URL = 'http://localhost:8000/api'

LIGHT_BLUE_THEME = """
    QMainWindow, QWidget {
        background-color: #FFFFFF;
        color: #1A1E29;
    }

    QLabel#headerLabel {
        background-color: #FFFFFF;
        color: #2E6BF0;
        padding: 15px;
        font-size: 16px;
        font-weight: bold;
        border-bottom: 2px solid #2E6BF0;
    }

    QLabel {
        color: #1A1E29;
    }

    QPushButton {
        background-color: #2E6BF0;
        color: #FFFFFF;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #2563eb;
    }

    QGroupBox {
        color: #1A1E29;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        margin-top: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        font-weight: bold;
    }

    QTableWidget {
        background-color: #FFFFFF;
        color: #1A1E29;
        gridline-color: #D1D5DB;
    }

    QHeaderView::section {
        background-color: #2E6BF0;
        color: #FFFFFF;
        padding: 8px;
        font-weight: bold;
    }

    QLabel.summaryLabel {
        color: #1A1E29;
        font-size: 13px;
    }

    QLabel.summaryValue {
        color: #2E6BF0;
        font-size: 15px;
        font-weight: bold;
    }
"""



class LoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login - Chemical Equipment Visualizer')
        self.setFixedWidth(350)
        self.setFixedHeight(200)
        self.setStyleSheet("QDialog { background-color: #FFFFFF; }")
        layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow('Username:', self.username_input)
        layout.addRow('Password:', self.password_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()


class DataLoaderThread(QThread):

    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url, auth_header):
        super().__init__()
        self.url = url
        self.auth_header = auth_header

    def run(self):
        try:
            response = requests.get(self.url, headers=self.auth_header)
            if response.status_code == 200:
                self.data_loaded.emit(response.json())
            else:
                self.error_occurred.emit(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            self.error_occurred.emit(f"Connection error: {str(e)}")


class ChartWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_pie(self, labels, values, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        colors = ['#2E6BF0', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff']
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)])
        ax.set_title(title, fontsize=14, fontweight='bold', color='#1A1E29')
        self.canvas.draw()

    def plot_bar(self, labels, values, title, ylabel):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(labels, values, color='#2E6BF0', edgecolor='#1d4ed8', alpha=0.8)
        ax.set_title(title, fontsize=14, fontweight='bold', color='#1A1E29')
        ax.set_ylabel(ylabel, color='#1A1E29')
        ax.tick_params(axis='x', rotation=45, colors='#1A1E29')
        ax.grid(True, alpha=0.3, color='#D1D5DB')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_line(self, labels, values, title, ylabel, color='#2E6BF0'):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(labels, values, marker='o', color=color, linewidth=2, markersize=6, markerfacecolor='white', markeredgewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold', color='#1A1E29')
        ax.set_ylabel(ylabel, color='#1A1E29')
        ax.grid(True, alpha=0.3, color='#D1D5DB')
        ax.tick_params(axis='x', rotation=45, colors='#1A1E29')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.fill_between(labels, values, alpha=0.1, color=color)
        self.figure.tight_layout()
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.auth_header = None
        self.current_data = []
        self.current_summary = None
        self.init_ui()
        self.show_login()

    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Parameter Visualizer - Desktop')
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(LIGHT_BLUE_THEME)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.main_tab = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_tab.setLayout(self.main_layout)

        header = QLabel('Chemical Equipment Parameter Visualizer')
        header.setObjectName('headerLabel')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header)

        upload_group = QGroupBox('Upload CSV File')
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Select CSV File')
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addStretch()
        self.logout_btn = QPushButton('Logout')
        self.logout_btn.clicked.connect(self.logout)
        upload_layout.addWidget(self.logout_btn)
        upload_group.setLayout(upload_layout)
        self.main_layout.addWidget(upload_group)

        self.summary_group = QGroupBox('Summary Statistics')
        self.summary_layout = QGridLayout()
        self.summary_group.setLayout(self.summary_layout)
        self.main_layout.addWidget(self.summary_group)

        charts_group = QGroupBox('Data Visualization')
        charts_layout = QVBoxLayout()

        self.pie_chart = ChartWidget()
        self.flowrate_chart = ChartWidget()
        self.pressure_chart = ChartWidget()
        self.temperature_chart = ChartWidget()

        charts_tabs = QTabWidget()
        charts_tabs.addTab(self.pie_chart, 'Equipment Type Distribution')
        charts_tabs.addTab(self.flowrate_chart, 'Flowrate')
        charts_tabs.addTab(self.pressure_chart, 'Pressure')
        charts_tabs.addTab(self.temperature_chart, 'Temperature')
        charts_layout.addWidget(charts_tabs)
        charts_group.setLayout(charts_layout)
        self.main_layout.addWidget(charts_group)

        table_group = QGroupBox('Equipment Data')
        table_layout = QVBoxLayout()
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSortingEnabled(True)
        self.data_table.setMaximumHeight(120)
        self.data_table.setFixedHeight(120)
        table_layout.addWidget(self.data_table)
        
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton('← Previous')
        self.next_btn = QPushButton('Next →')
        self.prev_btn.clicked.connect(self.show_previous_rows)
        self.next_btn.clicked.connect(self.show_next_rows)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        
        self.row_label = QLabel('Showing 0-0 of 0')
        self.row_label.setAlignment(Qt.AlignCenter)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.row_label)
        nav_layout.addWidget(self.next_btn)
        table_layout.addLayout(nav_layout)
        
        self.current_row_start = 0
        self.rows_per_page = 3
        
        table_group.setLayout(table_layout)
        self.main_layout.addWidget(table_group)

        pdf_layout = QHBoxLayout()
        pdf_layout.addStretch()
        self.pdf_btn = QPushButton('Generate PDF Report')
        self.pdf_btn.clicked.connect(self.generate_pdf)
        pdf_layout.addWidget(self.pdf_btn)
        pdf_layout.addStretch()
        self.main_layout.addLayout(pdf_layout)

        self.tabs.addTab(self.main_tab, 'Main')

        self.history_tab = QWidget()
        history_layout = QVBoxLayout()
        history_label = QLabel('Upload History (Last 5 Datasets)')
        history_label.setFont(QFont('Arial', 12, QFont.Bold))
        history_layout.addWidget(history_label)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            'Filename',
            'Uploaded',
            'Count',
            'Avg Flowrate',
            'Avg Pressure',
            'Avg Temperature'
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.doubleClicked.connect(self.on_history_item_double_clicked)
        history_layout.addWidget(self.history_table)
        self.history_tab.setLayout(history_layout)
        self.tabs.addTab(self.history_tab, 'History')

        self.comparison_widget = ComparisonWidget()
        self.comparison_widget.set_auth_header(self.auth_header)
        self.tabs.addTab(self.comparison_widget, 'Compare Datasets')

    def show_login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            username, password = login_dialog.get_credentials()
            if self.authenticate(username, password):
                self.username = username
                self.password = password
                self.auth_header = {
                    'Authorization': f'Basic {self.encode_auth(username, password)}'
                }
                self.load_initial_data()
            else:
                QMessageBox.warning(self, 'Login Failed', 'Invalid credentials. Please try again.')
                self.show_login()
        else:
            sys.exit()

    def encode_auth(self, username, password):
        return base64.b64encode(f'{username}:{password}'.encode()).decode()

    def authenticate(self, username, password):
        try:
            auth_header = {
                'Authorization': f'Basic {self.encode_auth(username, password)}'
            }
            response = requests.get(f'{API_BASE_URL}/history/', headers=auth_header)
            return response.status_code == 200
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def logout(self):
        self.username = None
        self.password = None
        self.auth_header = None
        self.current_data = []
        self.current_summary = None
        self.clear_ui()
        self.show_login()

    def clear_ui(self):
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.data_table.setRowCount(0)
        self.history_table.setRowCount(0)

    def load_initial_data(self):
        self.load_summary()
        self.load_data()
        self.load_history()

    def load_summary(self):
        try:
            response = requests.get(f'{API_BASE_URL}/summary/', headers=self.auth_header)
            if response.status_code == 200:
                self.current_summary = response.json()
                self.update_summary_display()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load summary: {str(e)}')

    def load_data(self):
        try:
            response = requests.get(f'{API_BASE_URL}/data/', headers=self.auth_header)
            if response.status_code == 200:
                self.current_data = response.json()
                self.update_data_table()
                self.update_charts()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load data: {str(e)}')

    def update_summary_display(self):
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if not self.current_summary:
            return
        summary = self.current_summary
        labels = ['Total Count', 'Avg Flowrate', 'Avg Pressure', 'Avg Temperature']
        values = [
            str(summary['total_count']),
            f"{summary['avg_flowrate']:.2f}",
            f"{summary['avg_pressure']:.2f}",
            f"{summary['avg_temperature']:.2f}"
        ]
        for i, (label, value) in enumerate(zip(labels, values)):
            label_widget = QLabel(f'{label}:')
            label_widget.setProperty("class", "summaryLabel")
            value_widget = QLabel(value)
            value_widget.setProperty("class", "summaryValue")
            self.summary_layout.addWidget(label_widget, i // 2, (i % 2) * 2)
            self.summary_layout.addWidget(value_widget, i // 2, (i % 2) * 2 + 1)

    def update_data_table(self):
        if not self.current_data:
            return
            
        total_rows = len(self.current_data)
        end_row = min(self.current_row_start + self.rows_per_page, total_rows)
        
        self.data_table.setRowCount(end_row - self.current_row_start)
        
        for i, row_idx in enumerate(range(self.current_row_start, end_row)):
            item = self.current_data[row_idx]
            self.data_table.setItem(i, 0, QTableWidgetItem(item['equipment_name']))
            self.data_table.setItem(i, 1, QTableWidgetItem(item['equipment_type']))
            self.data_table.setItem(i, 2, QTableWidgetItem(f"{item['flowrate']:.2f}"))
            self.data_table.setItem(i, 3, QTableWidgetItem(f"{item['pressure']:.2f}"))
            self.data_table.setItem(i, 4, QTableWidgetItem(f"{item['temperature']:.2f}"))
        
        self.prev_btn.setEnabled(self.current_row_start > 0)
        self.next_btn.setEnabled(end_row < total_rows)
        self.row_label.setText(f"Showing {self.current_row_start + 1}-{end_row} of {total_rows}")
        
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, 1)
        header.setSectionResizeMode(1, 2) 
        header.setSectionResizeMode(2, 3)
        header.setSectionResizeMode(3, 3)
        header.setSectionResizeMode(4, 3)

    def show_previous_rows(self):
        if self.current_row_start > 0:
            self.current_row_start = max(0, self.current_row_start - self.rows_per_page)
            self.update_data_table()

    def show_next_rows(self):
        total_rows = len(self.current_data)
        if self.current_row_start + self.rows_per_page < total_rows:
            self.current_row_start += self.rows_per_page
            self.update_data_table()

    def update_charts(self):
        if not self.current_data or not self.current_summary:
            return
        type_dist = self.current_summary['equipment_type_distribution']
        types = list(type_dist.keys())
        counts = list(type_dist.values())
        self.pie_chart.plot_pie(types, counts, 'Equipment Type Distribution')

        flowrate_data = sorted(self.current_data, key=lambda x: x['flowrate'], reverse=True)[:10]
        flowrate_labels = [item['equipment_name'] for item in flowrate_data]
        flowrate_values = [item['flowrate'] for item in flowrate_data]
        self.flowrate_chart.plot_bar(flowrate_labels, flowrate_values, 'Flowrate by Equipment (Top 10)', 'Flowrate')

        pressure_data = sorted(self.current_data, key=lambda x: x['pressure'], reverse=True)[:10]
        pressure_labels = [item['equipment_name'] for item in pressure_data]
        pressure_values = [item['pressure'] for item in pressure_data]
        self.pressure_chart.plot_line(pressure_labels, pressure_values, 'Pressure by Equipment (Top 10)', 'Pressure', '#60a5fa')

        temp_data = sorted(self.current_data, key=lambda x: x['temperature'], reverse=True)[:10]
        temp_labels = [item['equipment_name'] for item in temp_data]
        temp_values = [item['temperature'] for item in temp_data]
        self.temperature_chart.plot_line(temp_labels, temp_values, 'Temperature by Equipment (Top 10)', 'Temperature', '#93c5fd')

    def update_history_table(self, history_data):
        self.history_table.setRowCount(len(history_data))
        for row, item in enumerate(history_data):
            uploaded_at = datetime.fromisoformat(item['uploaded_at'].replace('Z', '+00:00'))
            self.history_table.setItem(row, 0, QTableWidgetItem(item['filename']))
            self.history_table.setItem(row, 1, QTableWidgetItem(uploaded_at.strftime('%Y-%m-%d %H:%M:%S')))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(item['total_count'])))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{item['avg_flowrate']:.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{item['avg_pressure']:.2f}"))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{item['avg_temperature']:.2f}"))
        self.history_table.resizeColumnsToContents()

    def load_history(self):
        try:
            response = requests.get(f'{API_BASE_URL}/history/', headers=self.auth_header)
            if response.status_code == 200:
                history_data = response.json()
                self.update_history_table(history_data)

                if hasattr(self, 'comparison_widget'):
                    self.comparison_widget.load_history(history_data)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load history: {str(e)}')

    def on_history_item_double_clicked(self, index):
        self.load_summary()
        self.load_data()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV File', '', 'CSV Files (*.csv)'
        )
        if not file_path:
            return
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f'{API_BASE_URL}/upload/', files=files, headers=self.auth_header
                )
            if response.status_code == 201:
                QMessageBox.information(self, 'Success', 'File uploaded successfully!')
                self.load_initial_data()
            else:
                error_msg = response.json().get('error', 'Upload failed')
                QMessageBox.warning(self, 'Upload Failed', error_msg)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to upload file: {str(e)}')

    def generate_pdf(self):
        try:
            response = requests.get(f'{API_BASE_URL}/pdf/', headers=self.auth_header, stream=True)
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 'Save PDF Report', 'equipment_report.pdf', 'PDF Files (*.pdf)'
                )
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', f'PDF saved to {file_path}')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to generate PDF')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to generate PDF: {str(e)}')


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()