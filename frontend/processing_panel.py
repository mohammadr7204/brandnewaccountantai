import os
import sys
import time
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QColor, QTextCharFormat, QFont

# Import from your existing backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.ai_processor import process_document
from src.file_handler import organize_document
from src.utils import setup_logging, save_checkpoint, load_checkpoint
from frontend.theme import Colors, style_secondary_button

class ProcessingWorker(QThread):
    """Worker thread for document processing"""

    # Signals
    progress_updated = pyqtSignal(int, int)  # Current, Total
    document_started = pyqtSignal(str)  # Document name
    document_completed = pyqtSignal(dict)  # Document result
    document_failed = pyqtSignal(str, str)  # Document name, Error message
    processing_finished = pyqtSignal(dict)  # Results summary
    log_message = pyqtSignal(str)  # Log message

    def __init__(self, document_paths, client_name):
        super().__init__()
        self.document_paths = document_paths
        self.client_name = client_name
        self.settings = QSettings("TaxDocProcessor", "App")
        self.logger = logging.getLogger(__name__)
        self.stop_requested = False

    def run(self):
        """Process all documents in the list"""
        # Set up logging
        self.log_message.emit("Starting document processing...")
        self.log_message.emit(f"Client name: {self.client_name}")

        # Load checkpoint if available
        processed_paths = set(load_checkpoint())
        remaining_docs = [p for p in self.document_paths if str(p) not in processed_paths]

        if len(processed_paths.intersection(set(map(str, self.document_paths)))) > 0:
            self.log_message.emit(f"Resuming from checkpoint. {len(processed_paths.intersection(set(map(str, self.document_paths))))} files already processed.")

        # Initialize results tracking
        results = {'success': 0, 'failed': 0, 'retry_success': 0}
        failed_docs = []

        # Process each document
        total_docs = len(remaining_docs)

        for idx, pdf_path in enumerate(remaining_docs):
            # Check if stop was requested
            if self.stop_requested:
                self.log_message.emit("Processing stopped by user")
                break

            # Update progress
            self.progress_updated.emit(idx + 1, total_docs)

            # Get document filename
            doc_name = Path(pdf_path).name
            self.document_started.emit(doc_name)
            self.log_message.emit(f"Processing {doc_name}...")

            # Process document with error handling and retries
            retry_count = 0
            success = False

            while not success and retry_count < config.MAX_RETRIES and not self.stop_requested:
                try:
                    # Process document
                    self.log_message.emit(f"Analyzing document content...")
                    document_data = process_document(pdf_path)

                    # Add client name to document data
                    document_data['client_name'] = self.client_name

                    # Organize document
                    self.log_message.emit(f"Organizing document...")
                    result = organize_document(pdf_path, document_data, self.client_name)

                    if result['success']:
                        if retry_count > 0:
                            results['retry_success'] += 1
                        else:
                            results['success'] += 1
                        success = True

                        # Add to processed list for checkpoint
                        processed_paths.add(str(pdf_path))
                        save_checkpoint(list(processed_paths))

                        # Emit success signal
                        self.document_completed.emit(result)

                        # Display success info
                        self.log_message.emit(f"✅ Successfully processed: {doc_name}")
                        self.log_message.emit(f"  • Document type: {document_data.get('document_type', 'Unknown')}")
                        self.log_message.emit(f"  • Client: {self.client_name}")
                        self.log_message.emit(f"  • Period/Year: {document_data.get('period_year', 'Unknown')}")
                        self.log_message.emit(f"  • Organized to: {self.client_name}/")
                    else:
                        raise Exception(result.get('error', 'Unknown error'))

                except Exception as e:
                    retry_count += 1
                    if retry_count < config.MAX_RETRIES and not self.stop_requested:
                        wait_time = retry_count * 2  # Exponential backoff
                        self.log_message.emit(f"⚠️ Retrying ({retry_count}/{config.MAX_RETRIES}) after {wait_time}s: {str(e)}")
                        time.sleep(wait_time)
                    else:
                        self.log_message.emit(f"❌ Failed after {retry_count} attempts: {str(e)}")
                        results['failed'] += 1
                        failed_docs.append(str(pdf_path))

                        # Emit failure signal
                        self.document_failed.emit(doc_name, str(e))

            # Small delay between documents
            if not self.stop_requested and idx < total_docs - 1:
                time.sleep(0.2)

        # Processing complete
        self.processing_finished.emit(results)

    def request_stop(self):
        """Request the worker to stop processing"""
        self.stop_requested = True
        self.log_message.emit("Stopping processing after current document completes...")


class ProcessingPanel(QWidget):
    """Widget for document processing interface"""

    # Signals
    processing_complete = pyqtSignal(dict)  # Send processing results

    def __init__(self):
        super().__init__()

        # Initialize state
        self.document_paths = []
        self.processing_worker = None
        self.results = {}
        self.client_name = ""

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Create progress group
        progress_group = QGroupBox("Processing Progress")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(10)

        # Overall progress
        overall_layout = QHBoxLayout()
        overall_label = QLabel("Overall Progress:")
        overall_label.setStyleSheet(f"font-weight: bold; color: {Colors.TEXT};")

        self.overall_progress = QProgressBar()
        self.overall_progress.setFormat("%v/%m documents (%p%)")
        self.overall_progress.setMinimumHeight(25)
        self.overall_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                background-color: {Colors.PROGRESS_BG};
                text-align: center;
                padding: 2px;
            }}

            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: 3px;
            }}
        """)

        overall_layout.addWidget(overall_label)
        overall_layout.addWidget(self.overall_progress, 1)

        # Current document
        current_layout = QHBoxLayout()
        current_label = QLabel("Current Document:")
        current_label.setStyleSheet(f"font-weight: bold; color: {Colors.TEXT};")

        self.current_document = QLabel("None")
        self.current_document.setStyleSheet(f"color: {Colors.PRIMARY};")

        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_document, 1)

        # Add to progress layout
        progress_layout.addLayout(overall_layout)
        progress_layout.addLayout(current_layout)

        # Create log group
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(300)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 5px;
            }}
        """)

        log_layout.addWidget(self.log_text)

        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setEnabled(False)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                color: white;
            }}

            QPushButton:hover {{
                background-color: #3dbb67;
            }}

            QPushButton:pressed {{
                background-color: #34a058;
            }}
        """)

        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setMinimumHeight(40)
        style_secondary_button(self.stop_button)
        # Additional styling for stop button
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {Colors.ERROR};
                border: 1px solid {Colors.ERROR};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {Colors.HIGHLIGHT};
            }}

            QPushButton:disabled {{
                background-color: {Colors.BORDER};
                color: {Colors.TEXT_LIGHT};
                border: 1px solid {Colors.BORDER};
            }}
        """)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        # Add widgets to main layout
        main_layout.addWidget(progress_group)
        main_layout.addWidget(log_group, 1)
        main_layout.addLayout(button_layout)

    def set_documents(self, documents):
        """Set the document paths to process"""
        self.document_paths = documents
        self.start_button.setEnabled(len(documents) > 0 and bool(self.client_name))
        self.overall_progress.setMaximum(len(documents))
        self.overall_progress.setValue(0)
        self.current_document.setText("None")

    def set_client_name(self, client_name):
        """Set the client name for processing"""
        self.client_name = client_name
        self.log(f"Client name set: {client_name}")
        self.start_button.setEnabled(len(self.document_paths) > 0 and bool(self.client_name))

    def start_processing(self):
        """Start document processing"""
        if not self.document_paths:
            self.log("No documents to process.")
            return

        if not self.client_name:
            self.log("No client name specified.")
            return

        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_text.clear()
        self.log("Initializing document processing...")
        self.log(f"Processing documents for client: {self.client_name}")

        # Create worker thread
        self.processing_worker = ProcessingWorker(self.document_paths, self.client_name)

        # Connect signals
        self.processing_worker.progress_updated.connect(self.update_progress)
        self.processing_worker.document_started.connect(self.update_current_document)
        self.processing_worker.document_completed.connect(self.on_document_completed)
        self.processing_worker.document_failed.connect(self.on_document_failed)
        self.processing_worker.processing_finished.connect(self.on_processing_finished)
        self.processing_worker.log_message.connect(self.log)

        # Start worker
        self.processing_worker.start()

    def stop_processing(self):
        """Stop document processing"""
        if self.processing_worker and self.processing_worker.isRunning():
            self.processing_worker.request_stop()
            self.stop_button.setEnabled(False)
            self.stop_button.setText("Stopping...")

    def update_progress(self, current, total):
        """Update the progress bar"""
        self.overall_progress.setMaximum(total)
        self.overall_progress.setValue(current)

    def update_current_document(self, document_name):
        """Update the current document label"""
        self.current_document.setText(document_name)

    def on_document_completed(self, result):
        """Handle document processing completion"""
        # Update results
        if 'results' not in self.results:
            self.results['results'] = []

        self.results['results'].append(result)

    def on_document_failed(self, document_name, error):
        """Handle document processing failure"""
        self.log(f"❌ Failed to process {document_name}: {error}")

        # Update failed list
        if 'failed' not in self.results:
            self.results['failed'] = []

        self.results['failed'].append({'name': document_name, 'error': error})

    def on_processing_finished(self, summary):
        """Handle processing completion"""
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stop Processing")

        # Log summary with colorized output
        self.log("\n" + "="*40)
        self.log("✨ Processing complete!")
        self.log(f"  • Successfully processed: {summary['success']} documents")
        self.log(f"  • Successful after retry: {summary['retry_success']} documents")
        self.log(f"  • Failed to process: {summary['failed']} documents")
        self.log("="*40)

        # Add summary to results
        self.results['summary'] = summary

        # Emit completion signal
        self.processing_complete.emit(self.results)

    def log(self, message):
        """Add a message to the log with color formatting"""
        # Apply color formatting based on message content
        if "✅" in message or "Successfully" in message:
            color = QColor(Colors.SUCCESS)
        elif "❌" in message or "Failed" in message or "Error" in message:
            color = QColor(Colors.ERROR)
        elif "⚠️" in message or "Retrying" in message:
            color = QColor(Colors.WARNING)
        elif "Processing complete" in message or "✨" in message:
            color = QColor(Colors.PRIMARY)
        else:
            color = QColor(Colors.TEXT)

        # Set text color
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        self.log_text.setCurrentCharFormat(fmt)

        # Add the message
        self.log_text.append(message)

        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
