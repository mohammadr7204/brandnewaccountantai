import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QListWidget, QListWidgetItem,
    QMessageBox, QGroupBox, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent, QIcon
from frontend.theme import Colors, style_secondary_button

class DocumentUploader(QWidget):
    """Widget for uploading and selecting tax documents"""

    # Signals
    documents_selected = pyqtSignal(list)  # Send list of document paths
    start_processing = pyqtSignal(str)  # Signal to start processing with client name

    def __init__(self):
        super().__init__()

        # Load settings
        self.settings = QSettings("TaxDocProcessor", "App")

        # Initialize document list
        self.document_paths = []

        # Setup UI
        self.setup_ui()

        # Enable drag and drop
        self.setAcceptDrops(True)

    def setup_ui(self):
        """Setup the user interface components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Create instructions with better styling
        instructions = QLabel(
            "Select or drag & drop PDF tax documents to process."
        )
        instructions.setFont(QFont("Segoe UI", 12))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet(f"color: {Colors.TEXT}; margin-bottom: 10px;")

        # Create drop area with enhanced styling
        self.drop_area = QFrame()
        self.drop_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.drop_area.setMinimumHeight(120)
        self.drop_area.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.CARD_BG};
                border: 2px dashed {Colors.PRIMARY};
                border-radius: 8px;
            }}
        """)

        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.setSpacing(15)

        # Add icon for drop area
        drop_icon_label = QLabel()
        drop_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_icon_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.PRIMARY};
                font-size: 24px;
            }}
        """)
        drop_icon_label.setText("📄")  # PDF file icon

        drop_label = QLabel("Drag & Drop PDF Files Here")
        drop_label.setFont(QFont("Segoe UI", 14))
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-weight: bold;")

        select_button = QPushButton("Select Files...")
        select_button.setMinimumHeight(40)
        select_button.clicked.connect(self.select_files)
        select_button.setCursor(Qt.CursorShape.PointingHandCursor)

        drop_layout.addWidget(drop_icon_label)
        drop_layout.addWidget(drop_label)
        drop_layout.addWidget(select_button)

        # Add client information group
        client_group = QGroupBox("Client Information")
        client_layout = QVBoxLayout(client_group)
        client_layout.setSpacing(10)

        client_label = QLabel("Client Name:")
        client_label.setFont(QFont("Segoe UI", 10))
        self.client_name_input = QLineEdit()
        self.client_name_input.setMinimumHeight(35)
        self.client_name_input.setPlaceholderText("Enter client name")
        self.client_name_input.textChanged.connect(self.update_process_button)

        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_name_input)

        # Create selected documents group
        docs_group = QGroupBox("Selected Documents")
        docs_layout = QVBoxLayout(docs_group)
        docs_layout.setSpacing(10)

        self.document_list = QListWidget()
        self.document_list.setAlternatingRowColors(True)
        self.document_list.setMinimumHeight(200)

        doc_buttons_layout = QHBoxLayout()
        doc_buttons_layout.setSpacing(10)

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected)
        remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(remove_button)

        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_documents)
        clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        style_secondary_button(clear_button)

        doc_buttons_layout.addWidget(remove_button)
        doc_buttons_layout.addWidget(clear_button)

        docs_layout.addWidget(self.document_list)
        docs_layout.addLayout(doc_buttons_layout)

        # Create process button with enhanced styling
        self.process_button = QPushButton("Start Processing")
        self.process_button.setMinimumHeight(50)
        self.process_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.on_process_clicked)
        self.process_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.process_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: #3dbb67;
            }}

            QPushButton:pressed {{
                background-color: #34a058;
            }}

            QPushButton:disabled {{
                background-color: {Colors.BORDER};
                color: {Colors.TEXT_LIGHT};
            }}
        """)

        # Add widgets to main layout
        main_layout.addWidget(instructions)
        main_layout.addWidget(self.drop_area, 1)
        main_layout.addWidget(client_group)
        main_layout.addWidget(docs_group, 2)
        main_layout.addWidget(self.process_button)

    def select_files(self):
        """Open file dialog to select PDF files"""
        # Get last directory from settings
        last_dir = self.settings.value("last_directory", str(Path.home()))

        # Open file dialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Tax Documents",
            last_dir,
            "PDF Files (*.pdf)"
        )

        if files:
            # Save the last directory
            self.settings.setValue("last_directory", str(Path(files[0]).parent))

            # Add files to the list
            self.add_documents(files)

    def add_documents(self, file_paths):
        """Add documents to the list"""
        for path in file_paths:
            if path not in self.document_paths and path.lower().endswith('.pdf'):
                self.document_paths.append(path)

                # Create item with PDF icon
                item = QListWidgetItem(Path(path).name)
                item.setToolTip(path)
                item.setIcon(QIcon.fromTheme("application-pdf", QIcon()))

                self.document_list.addItem(item)

        # Update process button state
        self.update_process_button()

        # Emit signal with updated document list
        self.documents_selected.emit(self.document_paths)

    def update_process_button(self):
        """Update the state of the process button based on inputs"""
        has_documents = len(self.document_paths) > 0
        has_client = bool(self.client_name_input.text().strip())
        self.process_button.setEnabled(has_documents and has_client)

    def remove_selected(self):
        """Remove selected documents from the list"""
        selected_items = self.document_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = self.document_list.row(item)
            self.document_list.takeItem(row)
            self.document_paths.pop(row)

        # Update process button state
        self.update_process_button()

        # Emit signal with updated document list
        self.documents_selected.emit(self.document_paths)

    def clear_documents(self):
        """Clear all documents from the list"""
        self.document_list.clear()
        self.document_paths = []

        # Update process button state
        self.update_process_button()

        # Emit signal with empty document list
        self.documents_selected.emit(self.document_paths)

    def on_process_clicked(self):
        """Handle process button click"""
        if not self.document_paths:
            QMessageBox.warning(
                self,
                "No Documents",
                "Please select at least one document to process."
            )
            return

        client_name = self.client_name_input.text().strip()
        if not client_name:
            QMessageBox.warning(
                self,
                "No Client Name",
                "Please enter a client name."
            )
            return

        # Emit signal to start processing with client name
        self.start_processing.emit(client_name)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for drop functionality"""
        if event.mimeData().hasUrls():
            # Change the style of the drop area to indicate an active drop target
            self.drop_area.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.HIGHLIGHT};
                    border: 2px dashed {Colors.ACCENT};
                    border-radius: 8px;
                }}
            """)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Reset drop area style when drag leaves"""
        self.drop_area.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.CARD_BG};
                border: 2px dashed {Colors.PRIMARY};
                border-radius: 8px;
            }}
        """)

    def dropEvent(self, event: QDropEvent):
        """Handle drop event for drop functionality"""
        # Reset style
        self.drop_area.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.CARD_BG};
                border: 2px dashed {Colors.PRIMARY};
                border-radius: 8px;
            }}
        """)

        file_paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.pdf'):
                file_paths.append(path)

        if file_paths:
            self.add_documents(file_paths)
