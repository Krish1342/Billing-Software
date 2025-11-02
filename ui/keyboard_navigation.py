"""
Keyboard Navigation Utilities for Unified Jewelry Management System

This module provides keyboard navigation helpers and mixins to improve
user experience with Enter key navigation and shortcuts.
"""

from PyQt5.QtWidgets import (
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QDateEdit,
    QTextEdit,
    QCheckBox,
    QMessageBox,
    QWidget,
)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from typing import List, Callable, Optional


class EnterKeyFilter(QWidget):
    """Event filter to handle Enter key navigation between widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigation_widgets = []
        self.action_widgets = {}  # Widget -> action function mapping

    def add_navigation_widgets(self, widgets: List[QWidget]):
        """Add widgets to navigation sequence."""
        self.navigation_widgets.extend(widgets)
        for widget in widgets:
            widget.installEventFilter(self)

    def add_action_widget(self, widget: QWidget, action: Callable):
        """Add widget that should trigger action on Enter."""
        self.action_widgets[widget] = action
        widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle key events for navigation."""
        if event.type() == QEvent.KeyPress:
            key_event = event

            if key_event.key() == Qt.Key_Return or key_event.key() == Qt.Key_Enter:
                # Check if this widget should trigger an action
                if obj in self.action_widgets:
                    self.action_widgets[obj]()
                    return True

                # Handle navigation between fields
                if obj in self.navigation_widgets:
                    current_index = self.navigation_widgets.index(obj)
                    next_index = (current_index + 1) % len(self.navigation_widgets)

                    # Move focus to next widget
                    next_widget = self.navigation_widgets[next_index]
                    next_widget.setFocus()

                    # Special handling for different widget types
                    if isinstance(next_widget, QLineEdit):
                        next_widget.selectAll()
                    elif isinstance(next_widget, QComboBox):
                        (
                            next_widget.showPopup()
                            if next_widget.isEditable()
                            else next_widget.setFocus()
                        )
                    elif isinstance(next_widget, (QSpinBox, QDoubleSpinBox)):
                        next_widget.selectAll()

                    return True

        return super().eventFilter(obj, event)


class ConfirmationDialog:
    """Utility class for creating confirmation dialogs."""

    @staticmethod
    def confirm_action(
        parent, title: str, message: str, detailed_message: str = ""
    ) -> bool:
        """Show confirmation dialog with double confirmation for critical operations."""

        # First confirmation
        reply = QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return False

        # Second confirmation for critical operations
        if detailed_message:
            confirm_reply = QMessageBox.question(
                parent,
                f"Confirm {title}",
                f"Are you absolutely sure you want to proceed?\n\n{detailed_message}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            return confirm_reply == QMessageBox.Yes

        return True

    @staticmethod
    def show_critical_confirmation(
        parent, title: str, message: str, action_name: str
    ) -> bool:
        """Show critical operation confirmation requiring typing confirmation."""
        from PyQt5.QtWidgets import QInputDialog

        # First dialog with detailed warning
        reply = QMessageBox.warning(
            parent,
            title,
            f"{message}\n\nThis action cannot be undone!",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )

        if reply != QMessageBox.Ok:
            return False

        # Second confirmation requiring user to type action name
        text, ok = QInputDialog.getText(
            parent,
            f"Confirm {title}",
            f'Type "{action_name}" to confirm this critical operation:',
        )

        return ok and text.strip().upper() == action_name.upper()


class KeyboardNavigationMixin:
    """Mixin to add keyboard navigation to tab widgets."""

    def setup_keyboard_navigation(self):
        """Initialize keyboard navigation for the tab."""
        self.enter_filter = EnterKeyFilter(self)
        self.navigation_widgets = []
        self.setup_tab_order()

    def setup_tab_order(self):
        """Setup tab order for widgets - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement setup_tab_order")

    def add_navigation_sequence(self, widgets: List[QWidget]):
        """Add widgets to navigation sequence."""
        self.navigation_widgets.extend(widgets)
        self.enter_filter.add_navigation_widgets(widgets)

    def add_action_shortcut(self, widget: QWidget, action: Callable):
        """Add Enter key action shortcut."""
        self.enter_filter.add_action_widget(widget, action)

    def focus_first_field(self):
        """Focus the first field in the navigation sequence."""
        if self.navigation_widgets:
            self.navigation_widgets[0].setFocus()
            if isinstance(self.navigation_widgets[0], QLineEdit):
                self.navigation_widgets[0].selectAll()


def create_shortcut_tooltip(base_tooltip: str, shortcut: str) -> str:
    """Create tooltip with keyboard shortcut information."""
    if base_tooltip:
        return f"{base_tooltip}\n\nKeyboard: {shortcut}"
    return f"Keyboard: {shortcut}"
