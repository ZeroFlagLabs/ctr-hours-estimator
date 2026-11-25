import sys
import os
import ctypes

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QIcon

from calculator import calculate_total_hours, calculate_employees


# -------------------------
# Resource path (PyInstaller safe)
# -------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


# -------------------------
# Windows App ID (taskbar icon fix)
# -------------------------
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    "ctr.hours.estimator"
)


# --------------------------
# DEFAULT VALUES
# --------------------------
DEFAULT_NEW_PN_HRS = 4
DEFAULT_REV_PN_HRS = 2
DEFAULT_NEW_DWG_HRS = 8
DEFAULT_REV_DWG_HRS = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # UPDATED PATHS
        uic.loadUi(resource_path("ui/main_window.ui"), self)

        self.setWindowTitle("CTR Hours Estimator")
        self.setWindowIcon(QIcon(resource_path("resources/images/icon.png")))
        
        self.setFixedSize(self.size())

        # --------------------------
        # Validators
        # --------------------------
        int_validator = QIntValidator(0, 999999)
        double_validator = QDoubleValidator(0.0, 9999999.0, 2)

        self.lineEdit_new_pn_qty.setValidator(int_validator)
        self.lineEdit_rev_pn_qty.setValidator(int_validator)
        self.lineEdit_new_dwg_qty.setValidator(int_validator)
        self.lineEdit_rev_dwg_qty.setValidator(int_validator)

        decimal_fields = [
            self.lineEdit_weeks,
            self.lineEdit_manual_hours,
            self.lineEdit_new_pn_hrs,
            self.lineEdit_rev_pn_hrs,
            self.lineEdit_new_dwg_hrs,
            self.lineEdit_rev_dwg_hrs,
            self.lineEdit_additional_hours,
        ]

        for field in decimal_fields:
            field.setValidator(double_validator)

        # --------------------------
        # Defaults
        # --------------------------
        self.set_defaults()

        self.label_total_hours.setText("-")
        self.label_fte.setText("-")

        # --------------------------
        # Signals
        # --------------------------
        input_fields = [
            self.lineEdit_weeks,
            self.lineEdit_manual_hours,
            self.lineEdit_new_pn_qty,
            self.lineEdit_new_pn_hrs,
            self.lineEdit_rev_pn_qty,
            self.lineEdit_rev_pn_hrs,
            self.lineEdit_new_dwg_qty,
            self.lineEdit_new_dwg_hrs,
            self.lineEdit_rev_dwg_qty,
            self.lineEdit_rev_dwg_hrs,
            self.lineEdit_additional_hours,
        ]

        for field in input_fields:
            field.textChanged.connect(self.calculate)

        self.checkBox_manual_mode.toggled.connect(self.toggle_manual_mode)
        self.checkBox_manual_mode.toggled.connect(self.calculate)

        self.pushButton_reset.clicked.connect(self.reset_fields)

        self.toggle_manual_mode(self.checkBox_manual_mode.isChecked())

    # --------------------------
    def set_defaults(self):
        self.lineEdit_new_pn_qty.clear()
        self.lineEdit_rev_pn_qty.clear()
        self.lineEdit_new_dwg_qty.clear()
        self.lineEdit_rev_dwg_qty.clear()

        self.lineEdit_new_pn_hrs.setText(str(DEFAULT_NEW_PN_HRS))
        self.lineEdit_rev_pn_hrs.setText(str(DEFAULT_REV_PN_HRS))
        self.lineEdit_new_dwg_hrs.setText(str(DEFAULT_NEW_DWG_HRS))
        self.lineEdit_rev_dwg_hrs.setText(str(DEFAULT_REV_DWG_HRS))

        self.lineEdit_additional_hours.clear()

    # --------------------------
    def toggle_manual_mode(self, checked):
        self.lineEdit_manual_hours.setEnabled(checked)

        breakdown_fields = [
            self.lineEdit_new_pn_qty,
            self.lineEdit_new_pn_hrs,
            self.lineEdit_rev_pn_qty,
            self.lineEdit_rev_pn_hrs,
            self.lineEdit_new_dwg_qty,
            self.lineEdit_new_dwg_hrs,
            self.lineEdit_rev_dwg_qty,
            self.lineEdit_rev_dwg_hrs,
            self.lineEdit_additional_hours,
        ]

        for field in breakdown_fields:
            field.setEnabled(not checked)

    # --------------------------
    def calculate(self):
        try:
            weeks_text = self.lineEdit_weeks.text().strip()
            weeks = float(weeks_text) if weeks_text else None

            has_input = False

            if self.checkBox_manual_mode.isChecked():
                manual_text = self.lineEdit_manual_hours.text().strip()
                if manual_text != "":
                    has_input = True
                else:
                    self.label_total_hours.setText("-")
                    self.label_fte.setText("-")
                    return
            else:
                new_pn_qty = float(self.lineEdit_new_pn_qty.text() or 0)
                rev_pn_qty = float(self.lineEdit_rev_pn_qty.text() or 0)
                new_dwg_qty = float(self.lineEdit_new_dwg_qty.text() or 0)
                rev_dwg_qty = float(self.lineEdit_rev_dwg_qty.text() or 0)
                additional_hours = float(self.lineEdit_additional_hours.text() or 0)

                if (
                    new_pn_qty > 0 or
                    rev_pn_qty > 0 or
                    new_dwg_qty > 0 or
                    rev_dwg_qty > 0 or
                    additional_hours > 0
                ):
                    has_input = True

            if not has_input:
                self.label_total_hours.setText("-")
                self.label_fte.setText("-")
                return

            if self.checkBox_manual_mode.isChecked():
                total_hours = float(self.lineEdit_manual_hours.text())
            else:
                total_hours = calculate_total_hours(
                    float(self.lineEdit_new_pn_qty.text() or 0),
                    float(self.lineEdit_new_pn_hrs.text() or 0),
                    float(self.lineEdit_rev_pn_qty.text() or 0),
                    float(self.lineEdit_rev_pn_hrs.text() or 0),
                    float(self.lineEdit_new_dwg_qty.text() or 0),
                    float(self.lineEdit_new_dwg_hrs.text() or 0),
                    float(self.lineEdit_rev_dwg_qty.text() or 0),
                    float(self.lineEdit_rev_dwg_hrs.text() or 0),
                    float(self.lineEdit_additional_hours.text() or 0)
                )

            self.label_total_hours.setText(
                f"{int(total_hours)}" if total_hours.is_integer() else f"{total_hours:.2f}"
            )

            if weeks is not None and weeks > 0:
                fte = calculate_employees(total_hours, weeks)
                self.label_fte.setText(f"{fte:.2f}")
            else:
                self.label_fte.setText("-")

        except ValueError:
            self.label_total_hours.setText("-")
            self.label_fte.setText("-")

    # --------------------------
    def reset_fields(self):
        for field in [
            self.lineEdit_weeks,
            self.lineEdit_manual_hours,
            self.lineEdit_new_pn_qty,
            self.lineEdit_new_pn_hrs,
            self.lineEdit_rev_pn_qty,
            self.lineEdit_rev_pn_hrs,
            self.lineEdit_new_dwg_qty,
            self.lineEdit_new_dwg_hrs,
            self.lineEdit_rev_dwg_qty,
            self.lineEdit_rev_dwg_hrs,
            self.lineEdit_additional_hours,
        ]:
            field.clear()

        self.set_defaults()
        self.label_total_hours.setText("-")
        self.label_fte.setText("-")


# --------------------------
# ENTRY POINT
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(resource_path("resources/images/icon.png")))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())