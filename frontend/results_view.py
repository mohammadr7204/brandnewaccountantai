import os
import platform
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QGroupBox,
    QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QColor, QFont
from frontend.theme import Colors, style_secondary_button

class ResultsView(QWidget):
    """Widget for displaying processing results"""

    def __init__(self):
        super().__init__()

        # Initialize results data
        self.results_data = {}

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Create summary group with cards layout
        summary_group = QGroupBox("Processing Summary")
        summary_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
            }}
        """)
        summary_layout = QHBoxLayout(summary_group)
        summary_layout.setSpacing(20)

        # Create metric cards
        self.total_label = self.create_metric_card("Total Documents", "0")
        self.success_label = self.create_metric_card("Successfully Processed", "0", Colors.SUCCESS)
        self.retry_label = self.create_metric_card("Retry Success", "0", Colors.WARNING)
        self.failed_label = self.create_metric_card("Failed to Process", "0", Colors.ERROR)

        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.success_label)
        summary_layout.addWidget(self.retry_label)
        summary_layout.addWidget(self.failed_label)
        summary_layout.addStretch()

        # Create results table
        results_group = QGroupBox("Processed Documents")
        results_layout = QVBoxLayout(results_group)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Document", "Document Type", "Client", "Period/Year", "Status"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {Colors.BORDER};
                selection-background-color: {Colors.PRIMARY};
                selection-color: white;
            }}

            QHeaderView::section {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.SECONDARY};
                font-weight: bold;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)

        results_layout.addWidget(self.results_table)

        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        export_button = QPushButton("Export Results")
        export_button.setIcon(QIcon.fromTheme("document-save", QIcon()))
        export_button.clicked.connect(self.export_results)
        export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        export_button.setMinimumHeight(40)

        open_folder_button = QPushButton("Open Output Folder")
        open_folder_button.setIcon(QIcon.fromTheme("folder-open", QIcon()))
        open_folder_button.clicked.connect(self.open_output_folder)
        open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        open_folder_button.setMinimumHeight(40)
        style_secondary_button(open_folder_button)

        button_layout.addWidget(export_button)
        button_layout.addWidget(open_folder_button)
        button_layout.addStretch()

        # Add widgets to main layout
        main_layout.addWidget(summary_group)
        main_layout.addWidget(results_group, 1)
        main_layout.addLayout(button_layout)

    def create_metric_card(self, title, value, color=None):
        """Create a metric card widget"""
        card = QWidget()
        card.setMinimumWidth(180)
        card.setMinimumHeight(80)

        # Set color based on metric type
        if color:
            border_color = color
        else:
            border_color = Colors.BORDER

        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet(f"border: none; color: {Colors.TEXT_LIGHT}; font-size: 12px;")

        # Value label
        value_label = QLabel(value)
        value_label.setStyleSheet(f"border: none; color: {Colors.TEXT}; font-size: 24px; font-weight: bold;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        # Store the value label reference for later updates
        card.value_label = value_label

        return card

    def load_results(self, results):
        """Load and display processing results"""
        self.results_data = results

        # Update summary
        summary = results.get('summary', {})
        total = summary.get('success', 0) + summary.get('retry_success', 0) + summary.get('failed', 0)

        self.total_label.value_label.setText(str(total))
        self.success_label.value_label.setText(str(summary.get('success', 0)))
        self.retry_label.value_label.setText(str(summary.get('retry_success', 0)))
        self.failed_label.value_label.setText(str(summary.get('failed', 0)))

        # Clear table
        self.results_table.setRowCount(0)

        # Add successful results
        successful_results = results.get('results', [])
        for result in successful_results:
            metadata = result.get('metadata', {})
            self.add_result_row(
                Path(result.get('original_path', '')).name,
                metadata.get('document_type', 'Unknown'),
                metadata.get('client_name', 'Unknown'),
                metadata.get('period_year', 'Unknown'),
                "Success"
            )

        # Add failed results
        failed_results = results.get('failed', [])
        for failed in failed_results:
            self.add_result_row(
                failed.get('name', 'Unknown'),
                "N/A",
                "N/A",
                "N/A",
                f"Failed: {failed.get('error', 'Unknown error')}"
            )

    def add_result_row(self, document, doc_type, client, period, status):
        """Add a row to the results table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        self.results_table.setItem(row, 0, QTableWidgetItem(document))
        self.results_table.setItem(row, 1, QTableWidgetItem(doc_type))
        self.results_table.setItem(row, 2, QTableWidgetItem(client))
        self.results_table.setItem(row, 3, QTableWidgetItem(period))
        self.results_table.setItem(row, 4, QTableWidgetItem(status))

        # Color code status
        status_item = self.results_table.item(row, 4)
        if status == "Success":
            status_item.setBackground(QColor(Colors.SUCCESS))
            status_item.setForeground(QColor("white"))
        elif "Failed" in status:
            status_item.setBackground(QColor(Colors.ERROR))
            status_item.setForeground(QColor("white"))

    def export_results(self):
        """Export results to CSV file"""
        if not self.results_data:
            return

        # Get save location
        settings = QSettings("TaxDocProcessor", "App")
        last_dir = settings.value("last_export_dir", str(Path.home()))

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            os.path.join(last_dir, "processing_results.csv"),
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        # Save directory for next time
        settings.setValue("last_export_dir", str(Path(file_path).parent))

        # Create CSV content
        csv_content = [
            "Document,Document Type,Client,Period/Year,Status,Original Path,New Path"
        ]

        # Add successful results
        successful_results = self.results_data.get('results', [])
        for result in successful_results:
            metadata = result.get('metadata', {})
            csv_content.append(
                f"{Path(result.get('original_path', '')).name},"
                f"{metadata.get('document_type', 'Unknown')},"
                f"{metadata.get('client_name', 'Unknown')},"
                f"{metadata.get('period_year', 'Unknown')},"
                f"Success,"
                f"{result.get('original_path', '')},"
                f"{result.get('new_path', '')}"
            )

        # Add failed results
        failed_results = self.results_data.get('failed', [])
        for failed in failed_results:
            csv_content.append(
                f"{failed.get('name', 'Unknown')},"
                f"N/A,"
                f"N/A,"
                f"N/A,"
                f"Failed: {failed.get('error', 'Unknown error')},"
                f"{failed.get('original_path', '')},"
                f"N/A"
            )

        # Write CSV file
        try:
            with open(file_path, 'w') as f:
                f.write('\n'.join(csv_content))
        except Exception as e:
            print(f"Error exporting results: {str(e)}")

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        # Get output directory from settings
        settings = QSettings("TaxDocProcessor", "App")
        output_dir = settings.value("output_dir", str(Path(__file__).parent.parent / "data" / "processed"))

        # Open folder based on platform
        if platform.system() == "Windows":
            subprocess.call(["explorer", output_dir])
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", output_dir])
        else:  # Linux
            subprocess.call(["xdg-open", output_dir])
