import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QSpinBox, QComboBox, QGroupBox, QDialogButtonBox,
    QCheckBox, QTabWidget, QFrame, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon
from frontend.theme import Colors, style_secondary_button

import config

class SettingsDialog(QDialog):
    """Settings dialog for the Tax Document Processor"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup window properties
        self.setWindowTitle("Settings")
        self.setMinimumWidth(550)
        self.setMinimumHeight(450)

        # Initialize settings
        self.settings = QSettings("TaxDocProcessor", "App")

        # Setup UI
        self.setup_ui()

        # Load current settings
        self.save_settings()

    def browse_source_dir(self):
        """Browse for source directory"""
        current_dir = self.source_dir.text() or str(config.SOURCE_DIR)
        directory = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", current_dir
        )
        if directory:
            self.source_dir.setText(directory)

    def browse_output_dir(self):
        """Browse for output directory"""
        current_dir = self.output_dir.text() or str(config.PROCESSED_DIR)
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", current_dir
        )
        if directory:
            self.output_dir.setText(directory)

    def browse_log_dir(self):
        """Browse for log directory"""
        current_dir = self.log_dir.text() or str(config.LOG_DIR)
        directory = QFileDialog.getExistingDirectory(
            self, "Select Log Directory", current_dir
        )
        if directory:
            self.log_dir.setText(directory)

    def setup_ui(self):
        """Setup the user interface components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create header
        header = QLabel("Application Settings")
        header.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {Colors.PRIMARY};
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header)

        # Create tabs
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)
        tab_widget.setStyleSheet(f"""
            QTabBar::tab:selected {{
                background-color: white;
                color: {Colors.PRIMARY};
                font-weight: bold;
            }}
        """)

        # Create API tab
        api_tab = QWidget()
        api_tab_layout = QVBoxLayout(api_tab)
        api_tab_layout.setSpacing(15)

        # API Key settings
        api_key_group = QGroupBox("API Key Management")
        api_key_layout = QGridLayout(api_key_group)
        api_key_layout.setVerticalSpacing(12)
        api_key_layout.setHorizontalSpacing(10)

        # Current API Key (masked)
        api_key_layout.addWidget(QLabel("Current API Key:"), 0, 0)
        self.current_api_key = QLineEdit()
        self.current_api_key.setMinimumHeight(30)
        self.current_api_key.setReadOnly(True)
        self.current_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_api_key.setPlaceholderText("API key not set")
        api_key_layout.addWidget(self.current_api_key, 0, 1)

        show_key_button = QPushButton("Show/Hide")
        show_key_button.setCheckable(True)
        show_key_button.toggled.connect(self.toggle_key_visibility)
        show_key_button.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(show_key_button)
        api_key_layout.addWidget(show_key_button, 0, 2)

        # New API Key
        api_key_layout.addWidget(QLabel("New API Key:"), 1, 0)
        self.new_api_key = QLineEdit()
        self.new_api_key.setMinimumHeight(30)
        self.new_api_key.setPlaceholderText("Enter new API key (sk-ant-...)")
        api_key_layout.addWidget(self.new_api_key, 1, 1)

        update_key_button = QPushButton("Update Key")
        update_key_button.clicked.connect(self.update_api_key)
        update_key_button.setCursor(Qt.CursorShape.PointingHandCursor)
        api_key_layout.addWidget(update_key_button, 1, 2)

        # Help text
        api_key_help = QLabel("Your Anthropic API key is used to access Claude AI for document processing. You can get an API key from https://console.anthropic.com/")
        api_key_help.setStyleSheet(f"color: {Colors.TEXT_LIGHT}; font-style: italic;")
        api_key_help.setWordWrap(True)

        # API model settings
        api_model_group = QGroupBox("API Settings")
        api_model_layout = QGridLayout(api_model_group)
        api_model_layout.setVerticalSpacing(12)
        api_model_layout.setHorizontalSpacing(10)

        api_model_layout.addWidget(QLabel("Claude Model:"), 0, 0)
        self.api_model = QComboBox()
        self.api_model.addItems([
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240229"
        ])
        self.api_model.setMinimumHeight(30)
        self.api_model.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 5px 10px;
            }}

            QComboBox::drop-down {{
                border: none;
                background: {Colors.PRIMARY};
                width: 25px;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}

            QComboBox::down-arrow {{
                image: none;
            }}
        """)

        api_model_layout.addWidget(self.api_model, 0, 1)

        api_model_layout.addWidget(QLabel("Max Tokens:"), 1, 0)
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 1000)
        self.max_tokens.setSingleStep(50)
        self.max_tokens.setMinimumHeight(30)
        self.max_tokens.setStyleSheet(f"""
            QSpinBox {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 5px 10px;
            }}
        """)
        api_model_layout.addWidget(self.max_tokens, 1, 1)

        api_model_help = QLabel("Select the Claude model to use. Opus is the most powerful but slower, while Haiku is faster but less capable.")
        api_model_help.setStyleSheet(f"color: {Colors.TEXT_LIGHT}; font-style: italic;")
        api_model_help.setWordWrap(True)

        # Add API elements to tab
        api_tab_layout.addWidget(api_key_group)
        api_tab_layout.addWidget(api_key_help)
        api_tab_layout.addWidget(api_model_group)
        api_tab_layout.addWidget(api_model_help)
        api_tab_layout.addStretch()

        # Add API tab to tab widget
        tab_widget.addTab(api_tab, "API Settings")

        # Create paths tab
        paths_tab = QWidget()
        paths_layout = QVBoxLayout(paths_tab)
        paths_layout.setSpacing(15)

        # Source directory
        source_group = QGroupBox("Document Directories")
        source_layout = QGridLayout(source_group)
        source_layout.setVerticalSpacing(12)
        source_layout.setHorizontalSpacing(10)

        # Source directory
        source_layout.addWidget(QLabel("Source Directory:"), 0, 0)
        self.source_dir = QLineEdit()
        self.source_dir.setMinimumHeight(30)
        source_layout.addWidget(self.source_dir, 0, 1)
        source_browse = QPushButton("Browse...")
        source_browse.clicked.connect(self.browse_source_dir)
        source_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(source_browse)
        source_layout.addWidget(source_browse, 0, 2)

        # Output directory
        source_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        self.output_dir = QLineEdit()
        self.output_dir.setMinimumHeight(30)
        source_layout.addWidget(self.output_dir, 1, 1)
        output_browse = QPushButton("Browse...")
        output_browse.clicked.connect(self.browse_output_dir)
        output_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(output_browse)
        source_layout.addWidget(output_browse, 1, 2)

        # Log directory
        source_layout.addWidget(QLabel("Log Directory:"), 2, 0)
        self.log_dir = QLineEdit()
        self.log_dir.setMinimumHeight(30)
        source_layout.addWidget(self.log_dir, 2, 1)
        log_browse = QPushButton("Browse...")
        log_browse.clicked.connect(self.browse_log_dir)
        log_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(log_browse)
        source_layout.addWidget(log_browse, 2, 2)

        # Add help text
        dir_help = QLabel("These directories will be used to store your documents during processing.")
        dir_help.setStyleSheet(f"color: {Colors.TEXT_LIGHT}; font-style: italic;")
        dir_help.setWordWrap(True)

        paths_layout.addWidget(source_group)
        paths_layout.addWidget(dir_help)
        paths_layout.addStretch()

        # Add paths tab
        tab_widget.addTab(paths_tab, "Directories")

        # Create processing tab with improved styling
        processing_tab = QWidget()
        processing_layout = QVBoxLayout(processing_tab)
        processing_layout.setSpacing(15)

        # Batch settings with better styling
        batch_group = QGroupBox("Batch Processing")
        batch_layout = QGridLayout(batch_group)
        batch_layout.setVerticalSpacing(12)
        batch_layout.setHorizontalSpacing(10)

        batch_layout.addWidget(QLabel("Batch Size:"), 0, 0)
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 50)
        self.batch_size.setMinimumHeight(30)
        self.batch_size.setStyleSheet(f"""
            QSpinBox {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 5px 10px;
            }}
        """)
        batch_layout.addWidget(self.batch_size, 0, 1)

        batch_layout.addWidget(QLabel("Batch Delay (seconds):"), 1, 0)
        self.batch_delay = QSpinBox()
        self.batch_delay.setRange(0, 60)
        self.batch_delay.setMinimumHeight(30)
        self.batch_delay.setStyleSheet(f"""
            QSpinBox {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 5px 10px;
            }}
        """)
        batch_layout.addWidget(self.batch_delay, 1, 1)

        batch_layout.addWidget(QLabel("Maximum Retries:"), 2, 0)
        self.max_retries = QSpinBox()
        self.max_retries.setRange(1, 10)
        self.max_retries.setMinimumHeight(30)
        self.max_retries.setStyleSheet(f"""
            QSpinBox {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 5px 10px;
            }}
        """)
        batch_layout.addWidget(self.max_retries, 2, 1)

        batch_help = QLabel("These settings control how documents are processed in batches to avoid API rate limits.")
        batch_help.setStyleSheet(f"color: {Colors.TEXT_LIGHT}; font-style: italic;")
        batch_help.setWordWrap(True)

        processing_layout.addWidget(batch_group)
        processing_layout.addWidget(batch_help)
        processing_layout.addStretch()

        # Add processing tab
        tab_widget.addTab(processing_tab, "Processing")

        # Add tabs to layout
        main_layout.addWidget(tab_widget)

        # Add buttons with improved styling
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )

        # Style the buttons
        save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        save_button.setMinimumHeight(35)
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setMinimumHeight(35)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(cancel_button)

        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)

        main_layout.addWidget(button_box)

    def toggle_key_visibility(self, checked):
        """Toggle API key visibility"""
        if checked:
            self.current_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.current_api_key.setEchoMode(QLineEdit.EchoMode.Password)

    def update_api_key(self):
        """Update the API key"""
        new_key = self.new_api_key.text().strip()

        if not new_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Please enter a new API key to update."
            )
            return

        # Simple validation - Claude API keys usually start with "sk-ant-"
        if not new_key.startswith("sk-ant-"):
            result = QMessageBox.question(
                self,
                "Invalid API Key Format",
                "The API key doesn't appear to be in the correct format. "
                "Anthropic API keys typically start with 'sk-ant-'.\n\n"
                "Do you want to save it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.No:
                return

        # Save to settings
        self.settings.setValue("anthropic_api_key", new_key)

        # Set in environment for current session
        os.environ['ANTHROPIC_API_KEY'] = new_key

        # Update display
        self.current_api_key.setText(new_key)
        self.new_api_key.clear()

        QMessageBox.information(
            self,
            "API Key Updated",
            "The API key has been updated successfully!"
        )

    def save_settings(self):
        """Save settings"""
        # Directories
        self.settings.setValue("source_dir", self.source_dir.text())
        self.settings.setValue("output_dir", self.output_dir.text())
        self.settings.setValue("log_dir", self.log_dir.text())

        # Update config directory values
        config.SOURCE_DIR = Path(self.source_dir.text())
        config.PROCESSED_DIR = Path(self.output_dir.text())
        config.LOG_DIR = Path(self.log_dir.text())

        # Ensure directories exist
        config.SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)

        # API settings
        self.settings.setValue("api_model", self.api_model.currentText())
        self.settings.setValue("max_tokens", self.max_tokens.value())

        # Update config API values
        config.ANTHROPIC_MODEL = self.api_model.currentText()
        config.MAX_TOKENS = self.max_tokens.value()

        # Batch settings
        self.settings.setValue("batch_size", self.batch_size.value())
        self.settings.setValue("batch_delay", self.batch_delay.value())
        self.settings.setValue("max_retries", self.max_retries.value())

        # Update config batch values
        config.BATCH_SIZE = self.batch_size.value()
        config.BATCH_DELAY = self.batch_delay.value()
        config.MAX_RETRIES = self.max_retries.value()

        # Close dialog
        self.accept()
