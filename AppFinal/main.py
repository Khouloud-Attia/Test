from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
import sys


if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
