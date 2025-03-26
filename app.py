#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Set Poppler path for pdf2image
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    base_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(os.path.dirname(sys.executable))
    poppler_path = str(base_dir / "poppler-bin")
    os.environ['POPPLER_PATH'] = poppler_path
else:
    # Running in development
    poppler_path = str(Path(__file__).parent / "poppler-bin")
    os.environ['POPPLER_PATH'] = poppler_path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Import project modules
from frontend.main_window import MainWindow
from frontend.theme import apply_theme

def main():
    """Main entry point for the Tax Document Processor application"""

    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Tax Document Processor")
    app.setOrganizationName("TaxDocProcessor")

    # Apply custom theme
    apply_theme(app)

    # Set application icon (if available)
    icon_path = Path(__file__).parent / "resources" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()