import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QPixmap
from frontend.theme import Colors, style_secondary_button

class APIKeyDialog(QDialog):
    """Dialog for entering the Anthropic API key"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup window properties
        self.setWindowTitle("API Key Setup")
        self.setMinimumWidth(450)
        self.setModal(True)  # Modal dialog that blocks input to other windows

        # Initialize settings
        self.settings = QSettings("TaxDocProcessor", "App")

        # Setup UI
        self.setup_ui()

        # Load current key if available
        self.load_api_key()

    def setup_ui(self):
        """Setup the user interface components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add header
        header_layout = QHBoxLayout()

        # Title and subtitle
        title_layout = QVBoxLayout()

        title = QLabel("API Key Setup")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {Colors.PRIMARY};
        """)

        subtitle = QLabel("Connect to Claude AI for document processing")
        subtitle.setStyleSheet(f"color: {Colors.TEXT_LIGHT};")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        # Anthropic logo (placeholder)
        logo_label = QLabel()
        logo_label.setFixedSize(48, 48)
        logo_label.setStyleSheet(f"""
            background-color: {Colors.PRIMARY};
            border-radius: 8px;
            color: white;
            font-weight: bold;
            text-align: center;
        """)
        logo_label.setText("AI")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(logo_label)

        main_layout.addLayout(header_layout)

        # Add info label with better styling
        info_frame = QLabel()
        info_frame.setStyleSheet(f"""
            background-color: {Colors.BACKGROUND};
            border-radius: 4px;
            padding: 10px;
        """)
        info_layout = QVBoxLayout(info_frame)

        info_label = QLabel(
            "Please enter your Anthropic API key to use the application.\n"
            "You can get an API key from https://console.anthropic.com/"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"background: transparent; color: {Colors.TEXT};")
        info_layout.addWidget(info_label)

        main_layout.addWidget(info_frame)

        # Add key input with modern styling
        key_layout = QVBoxLayout()

        key_label = QLabel("API Key:")
        key_label.setStyleSheet("font-weight: bold;")

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)  # Mask the API key
        self.key_input.setPlaceholderText("sk-ant-...")
        self.key_input.setMinimumHeight(35)
        self.key_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
            }}

            QLineEdit:focus {{
                border: 1px solid {Colors.PRIMARY};
            }}
        """)

        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)

        main_layout.addLayout(key_layout)

        # Add option to show/hide key with toggle button
        self.remember_key = QPushButton("Show Key")
        self.remember_key.setCheckable(True)
        self.remember_key.toggled.connect(self.toggle_key_visibility)
        self.remember_key.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(self.remember_key)

        main_layout.addWidget(self.remember_key)

        # Add buttons with improved styling
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )

        # Style the Save and Cancel buttons
        save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.setMinimumHeight(35)

        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setMinimumHeight(35)
        style_secondary_button(cancel_button)

        button_box.accepted.connect(self.save_api_key)
        button_box.rejected.connect(self.reject)

        main_layout.addWidget(button_box)

    def toggle_key_visibility(self, checked):
        """Toggle API key visibility"""
        if checked:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.remember_key.setText("Hide Key")
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.remember_key.setText("Show Key")

    def load_api_key(self):
        """Load API key from environment or settings"""
        # Check environment first
        api_key = os.environ.get('ANTHROPIC_API_KEY')

        # If not in environment, check settings
        if not api_key:
            api_key = self.settings.value("anthropic_api_key", "")

        # Set in input field
        if api_key:
            self.key_input.setText(api_key)

    def save_api_key(self):
        """Save the API key"""
        api_key = self.key_input.text().strip()

        # Validate key (basic check)
        if not api_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Please enter your Anthropic API key to continue."
            )
            return

        # Simple validation - Claude API keys usually start with "sk-ant-"
        if not api_key.startswith("sk-ant-"):
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
        self.settings.setValue("anthropic_api_key", api_key)

        # Set in environment for current session
        os.environ['ANTHROPIC_API_KEY'] = api_key

        # Close dialog
        self.accept()