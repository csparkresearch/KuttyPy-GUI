from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QTabWidget, QShortcut

from utilities import Qt


class MyTabBrowser(QTabWidget):
    def __init__(self):
        super().__init__()
        # Set up shortcuts for Ctrl+Left and Ctrl+Right
        self.prev_tab_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Left), self)
        self.next_tab_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Right), self)

        # Connect shortcuts to navigation functions
        self.prev_tab_shortcut.activated.connect(self.showPreviousTab)
        self.next_tab_shortcut.activated.connect(self.showNextTab)

    def keyPressEvent(self, event):
        # Override the keyPressEvent to prevent default handling of Ctrl+Tab
        if event.key() == Qt.Key_Tab and event.modifiers() == Qt.ControlModifier:
            return

        # Call the base class implementation for other key events
        super().keyPressEvent(event)

    def showPreviousTab(self):
        current_index = self.currentIndex()
        if current_index > 0:
            self.setCurrentIndex(current_index - 1)

    def showNextTab(self):
        current_index = self.currentIndex()
        if current_index < self.count() - 1:
            self.setCurrentIndex(current_index + 1)
