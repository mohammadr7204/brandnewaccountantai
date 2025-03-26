from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt

# Modern color palette
class Colors:
    # Main colors
    PRIMARY = "#4361ee"       # Blue primary
    SECONDARY = "#3f37c9"     # Darker blue for headers
    ACCENT = "#4cc9f0"        # Light blue accent
    BACKGROUND = "#f8f9fa"    # Light gray background
    CARD_BG = "#ffffff"       # White card background
    TEXT = "#212529"          # Dark text
    TEXT_LIGHT = "#6c757d"    # Light text

    # Semantic colors
    SUCCESS = "#4ade80"       # Green for success
    WARNING = "#fb8500"       # Orange for warnings
    ERROR = "#ef476f"         # Red for errors
    INFO = "#4cc9f0"          # Blue for info

    # UI element colors
    BUTTON_HOVER = "#3a56d4"  # Darker blue for button hover
    BORDER = "#dee2e6"        # Light gray for borders
    HIGHLIGHT = "#e9ecef"     # Very light gray for highlights
    PROGRESS_BG = "#e9ecef"   # Background for progress bars

def apply_theme(app):
    """Apply the theme to the application"""
    # Set application stylesheet
    app.setStyleSheet(f"""
        /* Global styles */
        QWidget {{
            font-family: 'Segoe UI', Arial, sans-serif;
            color: {Colors.TEXT};
            background-color: {Colors.BACKGROUND};
        }}

        QMainWindow {{
            background-color: {Colors.BACKGROUND};
        }}

        /* Header styles */
        QLabel[isHeader="true"] {{
            font-size: 18px;
            font-weight: bold;
            color: {Colors.SECONDARY};
            padding: 5px;
        }}

        /* Group box styling */
        QGroupBox {{
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            margin-top: 12px;
            background-color: {Colors.CARD_BG};
            padding: 10px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {Colors.SECONDARY};
            font-weight: bold;
        }}

        /* Button styling */
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }}

        QPushButton:hover {{
            background-color: {Colors.BUTTON_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {Colors.SECONDARY};
        }}

        QPushButton:disabled {{
            background-color: {Colors.BORDER};
            color: {Colors.TEXT_LIGHT};
        }}

        /* Secondary button */
        QPushButton[secondary="true"] {{
            background-color: white;
            color: {Colors.PRIMARY};
            border: 1px solid {Colors.PRIMARY};
        }}

        QPushButton[secondary="true"]:hover {{
            background-color: {Colors.BACKGROUND};
        }}

        /* Input styling */
        QLineEdit {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }}

        QLineEdit:focus {{
            border: 1px solid {Colors.PRIMARY};
        }}

        /* Tab widget styling */
        QTabWidget::pane {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            background-color: {Colors.CARD_BG};
        }}

        QTabBar::tab {{
            background-color: {Colors.BACKGROUND};
            border: 1px solid {Colors.BORDER};
            border-bottom-color: {Colors.BORDER};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {Colors.CARD_BG};
            border-bottom-color: {Colors.CARD_BG};
            color: {Colors.PRIMARY};
            font-weight: bold;
        }}

        /* Progress bar styling */
        QProgressBar {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            text-align: center;
            background-color: {Colors.PROGRESS_BG};
        }}

        QProgressBar::chunk {{
            background-color: {Colors.PRIMARY};
            border-radius: 3px;
        }}

        /* List widget styling */
        QListWidget {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            background-color: white;
            alternate-background-color: {Colors.HIGHLIGHT};
        }}

        QListWidget::item {{
            padding: 4px;
            border-bottom: 1px solid {Colors.HIGHLIGHT};
        }}

        QListWidget::item:selected {{
            background-color: {Colors.PRIMARY};
            color: white;
        }}

        /* Text edit styling */
        QTextEdit {{
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            background-color: white;
        }}

        /* Table widget styling */
        QTableWidget {{
            gridline-color: {Colors.BORDER};
            background-color: white;
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            alternate-background-color: {Colors.HIGHLIGHT};
        }}

        QTableWidget QHeaderView::section {{
            background-color: {Colors.BACKGROUND};
            padding: 6px;
            border: 1px solid {Colors.BORDER};
            font-weight: bold;
        }}

        QTableWidget::item:selected {{
            background-color: {Colors.PRIMARY};
            color: white;
        }}

        /* Menu styling */
        QMenuBar {{
            background-color: {Colors.CARD_BG};
            border-bottom: 1px solid {Colors.BORDER};
        }}

        QMenuBar::item {{
            padding: 8px 16px;
        }}

        QMenuBar::item:selected {{
            background-color: {Colors.PRIMARY};
            color: white;
        }}

        QMenu {{
            background-color: white;
            border: 1px solid {Colors.BORDER};
        }}

        QMenu::item {{
            padding: 6px 28px 6px 20px;
        }}

        QMenu::item:selected {{
            background-color: {Colors.PRIMARY};
            color: white;
        }}

        /* Status bar styling */
        QStatusBar {{
            background-color: {Colors.CARD_BG};
            border-top: 1px solid {Colors.BORDER};
        }}

        /* Scroll bar styling */
        QScrollBar:vertical {{
            border: none;
            background-color: {Colors.BACKGROUND};
            width: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {Colors.BORDER};
            border-radius: 5px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {Colors.PRIMARY};
        }}

        QScrollBar:horizontal {{
            border: none;
            background-color: {Colors.BACKGROUND};
            height: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {Colors.BORDER};
            border-radius: 5px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {Colors.PRIMARY};
        }}
    """)

# Function to style various elements
def style_header_label(label):
    """Style a label as a header"""
    label.setProperty("isHeader", "true")
    label.setStyleSheet("")  # Force property update
    font = label.font()
    font.setBold(True)
    font.setPointSize(12)
    label.setFont(font)

def style_secondary_button(button):
    """Style a button as a secondary button"""
    button.setProperty("secondary", "true")
    button.setStyleSheet("")  # Force property update