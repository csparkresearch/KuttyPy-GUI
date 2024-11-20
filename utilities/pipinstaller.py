import platform
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import QProcess


class PipInstallDialog(QDialog):
    def __init__(self, package_name,parent=None):
        super().__init__(parent)

        # Setup the layout and UI elements
        self.setWindowTitle("Pip Install Package")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Input field for package name
        self.package_label = QLabel("Package to be installed:")
        self.package_input = QLineEdit(self)
        self.package_input.setText(package_name)
        layout.addWidget(self.package_label)
        layout.addWidget(self.package_input)

        # Install button
        self.install_button = QPushButton("Install", self)
        self.install_button.clicked.connect(self.start_install)
        layout.addWidget(self.install_button)

        # UnInstall button
        self.uninstall_button = QPushButton("Un-Install", self)
        self.uninstall_button.clicked.connect(self.start_uninstall)
        layout.addWidget(self.uninstall_button)

        mplayout = QHBoxLayout(self)
        self.hands_button = QPushButton("Get MP Hands model", self)
        self.hands_button.clicked.connect(self.get_hands_task)
        mplayout.addWidget(self.hands_button)
        self.face_button = QPushButton("Get MP Face model(X)", self)
        self.face_button.clicked.connect(self.get_hands_task)
        mplayout.addWidget(self.face_button)
        layout.addLayout(mplayout)

        # Output field for showing progress and messages
        self.output_field = QTextEdit(self)
        self.output_field.setReadOnly(True)
        layout.addWidget(self.output_field)

        # Progress bar for visual indication
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # QProcess to handle pip installation
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def start_install(self):
        """Start the pip installation process"""
        package_name = self.package_input.text().strip()
        if not package_name:
            self.output_field.append("Please enter a package name.")
            return

        self.output_field.append(f"Starting installation of {package_name}...\n")

        # Start pip install as a subprocess
        system = platform.system()
        if system == 'Linux' or system == 'Darwin':
            self.process.start("pip", ["install"]+package_name.split(' '))
        elif system == 'Windows':
            self.process.start("py", ["-3", "-m", "pip", "install"]+package_name.split(' '))


        # Reset progress bar
        self.progress_bar.setRange(0, 0)  # Indeterminate progress until finished

    def start_uninstall(self):
        """Start the pip uninstallation process"""
        package_name = self.package_input.text().strip()
        if not package_name:
            self.output_field.append("Please enter a package name.")
            return

        self.output_field.append(f"Uninstalling {package_name}...\n")

        system = platform.system()
        if system == 'Linux' or system == 'Darwin':
            self.process.start("pip", ["uninstall", "-y", package_name])
        elif system == 'Windows':
            self.process.start("py", ["-3", "-m", "pip", "uninstall", "-y", package_name])

        # Reset progress bar
        self.progress_bar.setRange(0, 0)  # Indeterminate progress until finished

    def get_hands_task(self):
        #!wget - q https: // storage.googleapis.com / mediapipe - models / hand_landmarker / hand_landmarker / float16 / 1 / hand_landmarker.task
        """Start the pip installation process"""
        self.output_field.append("fetching mp hands...\n")
        # Start wget as a subprocess
        system = platform.system()
        self.process.start("wget", ["-q", "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"])
        # Reset progress bar
        self.progress_bar.setRange(0, 0)  # Indeterminate progress until finished

    def handle_stdout(self):
        """Handle standard output from the process"""
        data = self.process.readAllStandardOutput().data().decode()
        self.output_field.append(data)

    def handle_stderr(self):
        """Handle standard error from the process"""
        data = self.process.readAllStandardError().data().decode()
        self.output_field.append(data)

    def process_finished(self):
        """Handle when the pip installation process finishes"""
        self.output_field.append("\nProcess complete!")
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)

