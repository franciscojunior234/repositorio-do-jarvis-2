from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime


class JarvisUI(QWidget):

    def __init__(self):

        super().__init__()

        # JANELA
        self.setWindowTitle("JARVIS AI")

        self.setGeometry(250, 80, 1000, 650)

        self.setStyleSheet("""
            background-color: #020412;
        """)

        # TÍTULO
        self.title = QLabel("JARVIS", self)

        self.title.setGeometry(0, 30, 1000, 80)

        self.title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.title.setFont(
            QFont("Arial", 42)
        )

        self.title.setStyleSheet("""
            color: #00F5FF;
            font-weight: bold;
        """)

        # STATUS
        self.status = QLabel(
            "SYSTEM ONLINE",
            self
        )

        self.status.setGeometry(
            0, 95, 1000, 40
        )

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status.setFont(
            QFont("Arial", 15)
        )

        self.status.setStyleSheet("""
            color: #00FFAA;
        """)

        # RELÓGIO
        self.clock = QLabel(self)

        self.clock.setGeometry(
            0, 140, 1000, 40
        )

        self.clock.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.clock.setFont(
            QFont("Consolas", 18)
        )

        self.clock.setStyleSheet("""
            color: #7DF9FF;
        """)

        # NÚCLEO CENTRAL
        self.core = QLabel("◉", self)

        self.core.setGeometry(
            0, 180, 1000, 300
        )

        self.core.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.core.setFont(
            QFont("Arial", 160)
        )

        self.core.setStyleSheet("""
            color: #00F5FF;
        """)

        # TEXTO INFERIOR
        self.bottom_text = QLabel(
            "VOICE ASSISTANT ACTIVE",
            self
        )

        self.bottom_text.setGeometry(
            0, 500, 1000, 40
        )

        self.bottom_text.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.bottom_text.setFont(
            QFont("Arial", 14)
        )

        self.bottom_text.setStyleSheet("""
            color: #7DF9FF;
            letter-spacing: 2px;
        """)

        # BARRA INFERIOR
        self.footer = QLabel(
            "STARK INDUSTRIES SYSTEMS",
            self
        )

        self.footer.setGeometry(
            0, 590, 1000, 30
        )

        self.footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.footer.setFont(
            QFont("Arial", 10)
        )

        self.footer.setStyleSheet("""
            color: #00F5FF;
        """)

        # TIMER DE ANIMAÇÃO
        self.animation_timer = QTimer()

        self.animation_timer.timeout.connect(
            self.animate_core
        )

        self.animation_timer.start(80)

        # TIMER DO RELÓGIO
        self.clock_timer = QTimer()

        self.clock_timer.timeout.connect(
            self.update_clock
        )

        self.clock_timer.start(1000)

        self.growing = True

    def animate_core(self):

        size = self.core.font().pointSize()

        if self.growing:

            size += 1

            if size >= 185:
                self.growing = False

        else:

            size -= 1

            if size <= 150:
                self.growing = True

        self.core.setFont(
            QFont("Arial", size)
        )

    def update_clock(self):

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.clock.setText(current_time) 