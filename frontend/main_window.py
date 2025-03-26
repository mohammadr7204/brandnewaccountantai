import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar,
    QTextEdit, QTabWidget, QGroupBox, QLineEdit,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QIcon, QAction

from frontend.document_uploader import DocumentUploader
from frontend.processing_panel import ProcessingPanel
from frontend.settings_dialog import SettingsDialog
from frontend.api_key_dialog import APIKeyDialog
from frontend.results_view import ResultsView
from frontend.theme import Colors, style_header_label, style_secondary_button

class MainWindow(QMainWindow):
    """Main application window for the Tax Document Processor"""

    def __init__(self):
        super().__init__()

        # Setup window properties
        self.setWindowTitle("Tax Document Processor")
        self.setGeometry(100, 100, 1024, 768)

        # Initialize settings
        self.settings = QSettings("TaxDocProcessor", "App")

        # Check if API key is set
        if not self.check_api_key_set():
            api_dialog = APIKeyDialog(self)
            api_dialog.exec()

        # Setup UI
        self.setup_ui()
        self.setup_menu()

        # Connect signals
        self.connect_signals()

    def setup_ui(self):
        """Setup the user interface components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Create header with logo and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)

        # App title with styling
        app_title = QLabel("Tax Document Processor")
        style_header_label(app_title)
        app_title.setStyleSheet(f"color: {Colors.PRIMARY}; font-size: 24px;")

        # App subtitle/tagline
        app_subtitle = QLabel("Organize your financial documents with AI")
        app_subtitle.setStyleSheet(f"color: {Colors.TEXT_LIGHT}; font-size: 14px;")

        # Add title and subtitle to a vertical layout
        title_layout = QVBoxLayout()
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Add Settings button to header
        settings_button = QPushButton("Settings")
        settings_button.setIcon(QIcon.fromTheme("preferences-system", QIcon()))
        settings_button.clicked.connect(self.open_settings)
        settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_button.setMinimumHeight(40)
        style_secondary_button(settings_button)
        header_layout.addWidget(settings_button)

        # Create tab widget with modern styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # More modern look
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Create tabs
        self.uploader_tab = DocumentUploader()
        self.processing_tab = ProcessingPanel()
        self.results_tab = ResultsView()

        # Add tabs to widget with icons
        self.tab_widget.addTab(self.uploader_tab, "Upload Documents")
        self.tab_widget.addTab(self.processing_tab, "Processing")
        self.tab_widget.addTab(self.results_tab, "Results")

        # Create status bar with better styling
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"padding: 5px; color: {Colors.TEXT};")
        self.statusBar().addWidget(self.status_label)

        # Add widgets to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.tab_widget)

    def setup_menu(self):
        """Setup the application menu"""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Connect signals between components"""
        # Connect uploader to processing panel
        self.uploader_tab.documents_selected.connect(self.processing_tab.set_documents)

        # Connect start button to switch to processing tab
        self.uploader_tab.start_processing.connect(self.switch_to_processing_with_client)

        # Connect processing results to results view
        self.processing_tab.processing_complete.connect(self.results_tab.load_results)
        self.processing_tab.processing_complete.connect(self.switch_to_results)

    def switch_to_processing_with_client(self, client_name):
        """Switch to the processing tab with client name"""
        self.processing_tab.set_client_name(client_name)
        self.tab_widget.setCurrentIndex(1)

    def switch_to_results(self):
        """Switch to the results tab"""
        self.tab_widget.setCurrentIndex(2)

    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About Tax Document Processor",
            "Tax Document Processor v1.0\n\n"
            "A tool for organizing tax documents using AI."
        )

    def check_api_key_set(self):
        """Check if Anthropic API key is set"""
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            return True

        api_key = self.settings.value("anthropic_api_key")
        if api_key:
            os.environ['ANTHROPIC_API_KEY'] = api_key
            return True

        return False

