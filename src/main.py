"""CTR Hours Estimator desktop application; legacy calculations preserved."""
from status_bar import CenteredStatusBar
from pathlib import Path
import sys, ctypes, math
from PySide6.QtCore import QTimer, QUrl, Qt, QRegularExpression, QSize, QSignalBlocker, QFile, QIODevice, Signal
from PySide6.QtGui import QDesktopServices, QIcon, QRegularExpressionValidator, QFont, QShortcut, QKeySequence
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QRadioButton, QPushButton,
    QDialog, QTabWidget, QStatusBar, QButtonGroup, QAbstractSpinBox, QDialogButtonBox)
from PySide6.QtUiTools import QUiLoader
from dialog_position import exec_centered
from preferences import FACTORY_DEFAULTS, FACTORY_VALUES, TASK_NAMES, DEFAULT_NAMES, app_settings, load_rates, save_rates, valid_rates
from app_info import APP_TITLE, APP_VERSION, GITHUB_URL
from update_checker import UpdateChecker
from calculator import calculate_total_hours, calculate_employees

HERE = Path(__file__).resolve().parent
TITLE = APP_TITLE
VERSION = "v" + APP_VERSION
ICONS = HERE / "resources/icons"
DEFAULTS = FACTORY_DEFAULTS
STYLE = """
QWidget#surface, QDialog {background:#f3f7fb;color:#1b3452;font-family:'Segoe UI';font-size:12px;}
QLabel {color:#174675;font-weight:normal;}
QLabel#title {color:#123b7c;font-size:19px;font-weight:700;}
QLabel#version, QLabel#muted {color:#6c7e94;font-size:11px;}
QLabel#column {color:#667c94;font-size:11px;font-weight:600;}
QLabel#result {color:#123b7c;font-size:18px;font-weight:700;}
QLabel:disabled {color:#8190a1;}
QGroupBox {background:#ffffff;border:1px solid #d8e4f0;border-radius:6px;margin-top:13px;padding:5px 7px 5px;font-weight:600;color:#174675;}
QGroupBox::title {subcontrol-origin:margin;subcontrol-position:top left;left:10px;top:2px;padding:0 4px;color:#164f8a;}
QAbstractSpinBox {background:white;border:1px solid #b9cce1;border-radius:4px;padding:1px 18px 1px 4px;color:#243d58;}
QAbstractSpinBox QLineEdit {background:transparent;border:0;color:#243d58;selection-background-color:#258aca;}
QAbstractSpinBox:focus {border:2px solid #258aca;padding:0 17px 0 3px;}
QAbstractSpinBox:disabled {background:#e3e8ee;color:#8190a1;border-color:#c4cdd8;}
QAbstractSpinBox:disabled QLineEdit {color:#8190a1;}
QAbstractSpinBox::up-button,QAbstractSpinBox::down-button {subcontrol-origin:border;width:14px;background:transparent;border:none;right:4px;}
QAbstractSpinBox::up-button {subcontrol-position:top right;top:2px;}
QAbstractSpinBox::down-button {subcontrol-position:bottom right;bottom:2px;}
QAbstractSpinBox::up-arrow {image:url(@ICONS@/spin-chevron-up.png);width:12px;height:8px;}
QAbstractSpinBox::down-arrow {image:url(@ICONS@/spin-chevron-down.png);width:12px;height:8px;}
QAbstractSpinBox::up-arrow:disabled {image:url(@ICONS@/spin-chevron-up-disabled.png);}
QAbstractSpinBox::down-arrow:disabled {image:url(@ICONS@/spin-chevron-down-disabled.png);}
QRadioButton {color:#1b3452;spacing:5px;}
QPushButton {background:#eaf3fc;color:#144b83;border:1px solid #9ebfe2;border-radius:5px;min-height:24px;padding:2px 8px;font-weight:600;}
QPushButton:hover {background:#d9ecff;}
QPushButton:pressed {background:#c6def7;}
QPushButton#gear {background:transparent;border:1px solid transparent;padding:0;min-height:0;}
QPushButton#gear:hover {background:#e5f1fc;border-color:#bfd4e9;}
QTabWidget::pane {background:white;border:1px solid #d8e4f0;}
QTabBar::tab {padding:6px 10px;background:#eaf3fc;border:1px solid #d8e4f0;}
QTabBar::tab:selected {background:white;color:#164f8a;}
""".replace("@ICONS@",ICONS.as_posix())
def label(text, name=""):
    w = QLabel(text)
    if name: w.setObjectName(name)
    return w

class OptionalSpin(QAbstractSpinBox):
    """Native Qt arrows with a genuinely blank state, distinct from numeric zero."""
    textChanged = Signal(str)
    def __init__(self,integer=False,suffix=""):
        super().__init__()
        self.integer=integer
        self.maximum=999 if integer else 9999.99
        self.setFixedSize(106 if suffix else 64,30)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.unit=QLabel(suffix,self.lineEdit())
        self.unit.setStyleSheet("color:#243d58;background:transparent;border:0;padding:0;")
        self.unit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.unit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.unit.setVisible(bool(suffix))
        self.suffix_width=self.lineEdit().fontMetrics().horizontalAdvance(" "+suffix)+2 if suffix else 0
        self.lineEdit().setTextMargins(4,0,self.suffix_width,0)
        self.lineEdit().textChanged.connect(self.position_unit)
        pattern=r"[0-9]{0,3}" if integer else r"[0-9]{0,4}(?:\.[0-9]{0,2})?"
        self.lineEdit().setValidator(QRegularExpressionValidator(QRegularExpression(pattern),self))
        self.lineEdit().textChanged.connect(self.textChanged)
        self.setKeyboardTracking(True)
    def position_unit(self,*_):
        if not self.unit.text(): return
        e=self.lineEdit()
        self.unit.setFont(e.font())
        fm=e.fontMetrics()
        self.unit.adjustSize()
        x=e.textMargins().left()+2+fm.horizontalAdvance(e.text())+fm.horizontalAdvance(" ")
        self.unit.move(x,(e.height()-self.unit.height())//2)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,"unit"): self.position_unit()
    def setText(self,text):
        self.lineEdit().setText(str(text))
    def clear(self):
        self.lineEdit().clear()
    def hasAcceptableInput(self):
        return self.lineEdit().hasAcceptableInput()
    def stepEnabled(self):
        try: v=number(self)
        except ValueError: v=None
        flags=QAbstractSpinBox.StepEnabledFlag.StepNone
        if v is None or v<self.maximum: flags |= QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        if v is not None and v>0: flags |= QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        return flags
    def stepBy(self,steps):
        try: v=number(self)
        except ValueError: v=None
        step=1
        value=max(0,min(self.maximum,(v or 0)+steps*step))
        self.setText(str(int(value)) if self.integer else hours(value).replace(",",""))
    def focusInEvent(self,event):
        super().focusInEvent(event)
        self.lineEdit().setTextMargins(4,0,self.suffix_width,0)
        self.position_unit()
    def focusOutEvent(self,event):
        super().focusOutEvent(event)
        self.lineEdit().setTextMargins(4,0,self.suffix_width,0)
        self.position_unit()
    def wheelEvent(self,event):
        event.ignore()
def editor(width=None, integer=False, suffix=""):
    return OptionalSpin(integer,suffix)

def group(title):
    w = QGroupBox(title)
    l = QVBoxLayout(w)
    l.setContentsMargins(8,7,8,7)
    l.setSpacing(4)
    return w,l

def number(w):
    t = w.text().strip()
    if not t: return None
    if not w.hasAcceptableInput(): raise ValueError("Invalid number")
    n = float(t)
    if not math.isfinite(n) or n < 0: raise ValueError("Invalid number")
    return n

def hours(n):
    return f"{n:,.2f}".rstrip("0").rstrip(".")

class Window(QMainWindow):
    def __init__(self, preferences=None):
        super().__init__()
        self.preferences = app_settings() if preferences is None else preferences
        self.saved_defaults = load_rates(self.preferences)
        self.update_checker = UpdateChecker(self)
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(str(ICONS/"icon.ico")))
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        surface = QWidget(objectName="surface")
        surface.setStyleSheet(STYLE)
        self.setCentralWidget(surface)
        root = QVBoxLayout(surface)
        root.setContentsMargins(10,8,10,8)
        root.setSpacing(6)
        header = QHBoxLayout()
        header.addWidget(label(TITLE,"title"))
        header.addStretch()
        header.addWidget(label(VERSION,"version"))
        self.gear = QPushButton(objectName="gear")
        self.gear.setIcon(QIcon(str(ICONS/"settings-gear.png")))
        self.gear.setIconSize(QSize(18,18))
        self.gear.setFixedSize(28,28)
        self.gear.setToolTip("Settings (Ctrl+,)")
        self.gear.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.gear.clicked.connect(self.settings)
        header.addWidget(self.gear)
        root.addLayout(header)

        panels = QHBoxLayout()
        panels.setSpacing(8)
        self.work_group,l = group("Work breakdown")
        grid = QGridLayout()
        grid.setHorizontalSpacing(5)
        grid.setVerticalSpacing(5)
        grid.setColumnStretch(0,1)
        grid.setColumnMinimumWidth(0,96)
        grid.setColumnMinimumWidth(3,64)
        for col, title in enumerate(("Task","Qty","Hours/task","Total hours")):
            w = label(title,"column")
            if col: w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(w,0,col)
        self.quantities, self.rates, self.subtotals = [], [], []
        for i,title in enumerate(TASK_NAMES):
            q,r,subtotal = editor(integer=True),editor(),label("-")
            q.setAccessibleName(title+" quantity")
            r.setAccessibleName(title+" hours per task")
            r.setText(self.saved_defaults[i])
            subtotal.setFixedWidth(64)
            subtotal.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.quantities.append(q); self.rates.append(r); self.subtotals.append(subtotal)
            grid.addWidget(label(title),i+1,0)
            grid.addWidget(q,i+1,1)
            grid.addWidget(r,i+1,2)
            grid.addWidget(subtotal,i+1,3)
        self.additional = editor()
        self.additional.setText(self.saved_defaults[4])
        self.additional.setAccessibleName("Other hours")
        tip = "Enter additional project hours, or a known total with task quantities blank or zero."
        other_label=label("Other hours")
        other_label.setToolTip(tip)
        self.additional.setToolTip(tip)
        grid.addWidget(other_label,5,0,1,2)
        grid.addWidget(self.additional,5,2)
        l.addLayout(grid)
        l.addStretch()
        # Preserve the approved column at 100% but accommodate font rounding
        # at fractional display scaling (largest subtotal: 9,989,990.01).
        for subtotal in self.subtotals: subtotal.ensurePolished()
        subtotal_width=max(64,max(s.fontMetrics().horizontalAdvance("9,989,990.01")+1 for s in self.subtotals))
        for subtotal in self.subtotals:subtotal.setFixedWidth(subtotal_width)
        grid.setColumnMinimumWidth(3,subtotal_width)
        self.work_group.setFixedWidth(335+subtotal_width-64)
        panels.addWidget(self.work_group)

        side=QVBoxLayout()
        side.setSpacing(6)
        g,l = group("Project duration")
        row=QHBoxLayout()
        row.addWidget(label("Duration"))
        row.addStretch()
        self.weeks=editor(suffix="weeks")
        self.weeks.setText("0")
        self.weeks.setAccessibleName("Project duration in weeks")
        row.addWidget(self.weeks)
        l.addLayout(row)
        side.addWidget(g)
        g,l=group("Results")
        g.setMinimumWidth(194)
        for title,attr in (("Total hours","total"),("FTEs required*","fte")):
            l.addWidget(label(title))
            result=label("-","result")
            result.setMinimumWidth(150)
            result.setAlignment(Qt.AlignmentFlag.AlignRight)
            setattr(self,attr,result)
            l.addWidget(result)
            if attr=="total":
                rule=QLabel()
                rule.setFixedHeight(1)
                rule.setStyleSheet("background:#d8e4f0;")
                l.addWidget(rule)
        l.addStretch()
        note=label("* 37.5 hrs/week at 80% efficiency.","muted")
        note.setWordWrap(False)
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(note)
        side.addWidget(g,1)
        panels.addLayout(side)
        root.addLayout(panels)
        row = QHBoxLayout()
        row.addStretch()
        self.reset = QPushButton("Reset")
        self.reset.setFixedSize(106,30)
        self.reset.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.reset.setToolTip("Reset all inputs (Ctrl+R)")
        self.reset.clicked.connect(self.reset_fields)
        row.addWidget(self.reset)
        root.addLayout(row)
        self.setStatusBar(CenteredStatusBar(self))
        self.fields = [*[w for pair in zip(self.quantities,self.rates) for w in pair],self.additional,self.weeks]
        for w in self.fields: w.textChanged.connect(self.calculate)
        for a,b in zip(self.fields,self.fields[1:]): QWidget.setTabOrder(a,b)
        self.shortcuts = [QShortcut(QKeySequence("Ctrl+R"),self,activated=self.reset_fields),
                          QShortcut(QKeySequence("Ctrl+,"),self,activated=self.settings)]
        self.calculate()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        self.quantities[0].setFocus()

    def calculate(self,*_):
        self.total.setText("-")
        self.fte.setText("-")
        for s in self.subtotals: s.setText("-")
        try:
            args = []
            any_input = bool(self.additional.text().strip())
            incomplete = False
            for q,r,s in zip(self.quantities,self.rates,self.subtotals):
                qty = number(q)
                rate = number(r)
                any_input |= qty is not None
                if qty is not None:
                    if qty > 0 and rate is None:
                        incomplete = True
                    else:
                        s.setText(hours(qty*(rate or 0)))
                args.extend((qty or 0,rate or 0))
            additional = number(self.additional)
            if incomplete:
                self.statusBar().showMessage("Enter hours per task for each non-zero quantity.")
                return
            total = calculate_total_hours(*args,additional or 0) if any_input else None
            if total is None:
                self.statusBar().showMessage("Ready")
                return
            self.total.setText(hours(total)+" hrs")
            try:
                weeks = number(self.weeks)
            except ValueError:
                self.statusBar().showMessage("Enter a valid project duration.")
                return
            if weeks is None:
                self.statusBar().showMessage("Enter duration to calculate FTEs.")
            elif weeks == 0:
                self.statusBar().showMessage("Enter duration to calculate FTEs.")
            else:
                self.fte.setText(f"{calculate_employees(total,weeks):,.2f}")
                self.statusBar().showMessage("Calculated")
        except ValueError:
            for s in self.subtotals: s.setText("-")
            self.statusBar().showMessage("Enter valid numeric values.")

    def reset_fields(self):
        blockers = [QSignalBlocker(w) for w in self.fields]
        for w in self.fields: w.clear()
        for w,v in zip(self.rates,self.saved_defaults): w.setText(v)
        self.additional.setText(self.saved_defaults[4])
        self.weeks.setText("0")
        del blockers
        self.calculate()
        self.quantities[0].setFocus()

    def make_settings(self):
        f=QFile(str(HERE/"ui/settings_dialog.ui"))
        if not f.open(QIODevice.OpenModeFlag.ReadOnly): raise RuntimeError("Settings form missing")
        try: d=QUiLoader().load(f,self)
        finally: f.close()
        d.setWindowIcon(self.windowIcon())
        d.resize(526,500)
        d.setStyleSheet("""
            QPushButton { background:#eaf3fc; color:#144b83; border:1px solid #9ebfe2; border-radius:5px; min-height:24px; padding:2px 8px; font-weight:600; }
            QPushButton:hover { background:#d9ecff; }
            QPushButton:disabled { color:#8795a5; background:#eff2f5; }
            QFrame#settings_heading_rule { color:#858585; }
            QTabWidget::pane { background:white; border:1px solid #e7e7e7; border-radius:4px; }
            QTabBar::tab { background:#f1f1f1; border:1px solid #e5e5e5; border-top-left-radius:5px; border-top-right-radius:5px; padding:4px 11px; color:#344556; }
            QTabBar::tab:selected { background:white; color:#1b3452; border-bottom-color:white; }
        """)
        self.add_defaults_tab(d)
        d.setWindowModality(Qt.WindowModality.ApplicationModal)
        d.buttons.button(QDialogButtonBox.StandardButton.Close).setFixedSize(106,30)
        d.buttons.rejected.connect(d.reject)
        checker=self.update_checker
        d.check_on_launch.setChecked(checker.enabled())
        d.check_on_launch.toggled.connect(checker.set_enabled)
        d.check_now_button.clicked.connect(checker.check)
        d.github_link.setText(f'<a href="{GITHUB_URL}">Project on GitHub</a>')
        d.github_link.setOpenExternalLinks(True)
        def refresh():
            d.update_status.setText(checker.status)
            d.check_now_button.setEnabled(checker._reply is None)
            d.open_release_button.setEnabled(checker.release_url is not None)
        def open_release():
            if checker.release_url:QDesktopServices.openUrl(QUrl(checker.release_url))
        def disconnect(*_):
            try:checker.state_changed.disconnect(refresh)
            except (RuntimeError,TypeError):pass
        d.open_release_button.clicked.connect(open_release)
        checker.state_changed.connect(refresh)
        d.finished.connect(disconnect)
        refresh()
        return d

    def add_defaults_tab(self,d):
        page=QWidget(objectName="defaults_tab")
        page.setStyleSheet("QWidget#defaults_tab {background:white;}")
        l=QVBoxLayout(page)
        l.setContentsMargins(15,14,15,14)
        l.setSpacing(10)
        heading=label("Default hours")
        heading.setStyleSheet("font-weight:600;color:#164f8a;")
        l.addWidget(heading)
        intro=label("Set your preferred hours per task and other hours for current and future estimates.")
        intro.setStyleSheet("color:#243d58;")
        intro.setWordWrap(True)
        l.addWidget(intro)
        grid=QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0,1)
        d.default_fields=[]
        for i,name in enumerate(DEFAULT_NAMES):
            lab=label(name)
            lab.setStyleSheet("color:#243d58;")
            spin=editor(suffix="hrs")
            spin.setFixedWidth(106)
            spin.setStyleSheet("\n".join(line for line in STYLE.splitlines() if line.startswith("QAbstractSpinBox")))
            spin.setAccessibleName(name+" default hours")
            spin.setText(self.saved_defaults[i])
            lab.setBuddy(spin)
            grid.addWidget(lab,i,0)
            grid.addWidget(spin,i,1)
            d.default_fields.append(spin)
        l.addLayout(grid)
        rule=QLabel()
        rule.setFixedHeight(1)
        rule.setStyleSheet("background:#e0e0e0;")
        l.addWidget(rule)
        row=QHBoxLayout()
        d.restore_defaults_button=QPushButton("Restore defaults")
        d.save_defaults_button=QPushButton("Save defaults")
        for btn in (d.restore_defaults_button,d.save_defaults_button):
            btn.setFixedSize(106,30)
        row.addWidget(d.restore_defaults_button)
        row.addStretch()
        row.addWidget(d.save_defaults_button)
        l.addLayout(row)
        d.defaults_status=label("Saved defaults apply immediately.", "muted")
        d.defaults_status.setStyleSheet("color:#6c7e94;font-size:11px;")
        d.defaults_status.setWordWrap(True)
        l.addWidget(d.defaults_status)
        l.addStretch()
        def values():
            return tuple(spin.text() for spin in d.default_fields)
        def refresh(*_):
            valid=valid_rates(values())
            d.save_defaults_button.setEnabled(valid and values()!=self.saved_defaults)
            d.defaults_status.setText("Unsaved changes. Select Save defaults to apply." if valid and values()!=self.saved_defaults else
                "Saved defaults apply immediately." if valid else "Enter all five defaults (0 to 9999.99 hrs).")
        def restore():
            for spin,val in zip(d.default_fields,FACTORY_VALUES):spin.setText(val)
            refresh()
        def save():
            try:
                save_rates(self.preferences,values())
            except (ValueError,OSError) as exc:
                d.defaults_status.setText(str(exc))
                return
            self.saved_defaults=values()
            blockers=[QSignalBlocker(w) for w in [*self.rates,self.additional]]
            for w,v in zip(self.rates,self.saved_defaults):w.setText(v)
            self.additional.setText(self.saved_defaults[4])
            del blockers
            self.calculate()
            refresh()
            d.defaults_status.setText("Defaults saved and applied.")
        for spin in d.default_fields:spin.textChanged.connect(refresh)
        d.restore_defaults_button.clicked.connect(restore)
        d.save_defaults_button.clicked.connect(save)
        d.settings_tabs.insertTab(0,page,"Defaults")
        d.settings_tabs.setCurrentIndex(0)
        refresh()

    def settings(self):
        d=self.make_settings()
        try:exec_centered(d,self)
        finally:d.deleteLater()

def make_app():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(TITLE)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI",9))
    app.setWindowIcon(QIcon(str(ICONS/"icon.ico")))
    return app

if __name__=="__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ZeroFlagLabs.CTRHoursEstimator")
    app=make_app()
    if "--self-test" in sys.argv:
        from tempfile import TemporaryDirectory
        from PySide6.QtCore import QSettings
        temp=TemporaryDirectory()
        w=Window(QSettings(str(Path(temp.name)/"self-test.ini"), QSettings.Format.IniFormat))
    else:w=Window()
    w.show()
    if "--self-test" in sys.argv:
        from runtime_check import run
        sys.exit(run(app,w))
    QTimer.singleShot(0,w.update_checker.check_on_launch)
    sys.exit(app.exec())
