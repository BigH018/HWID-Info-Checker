import sys
from PyQt5.QtWidgets import QApplication
from ui import HWIDWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = HWIDWindow()
    window.show()
    sys.exit(app.exec_())
