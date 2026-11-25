import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from tempfile import TemporaryDirectory
from PySide6.QtCore import QSettings
from pathlib import Path
_test_dir=TemporaryDirectory()
_test_settings=QSettings(str(Path(_test_dir.name)/"test.ini"),QSettings.Format.IniFormat)
from main import *
EVIDENCE=Path(__file__).resolve().parents[1]/"docs/private/release-validation"
EVIDENCE.mkdir(parents=True,exist_ok=True)
from PySide6.QtTest import QTest
from PySide6.QtCore import QPoint
app=make_app(); w=Window(_test_settings); w.show(); w.activateWindow(); app.processEvents()
assert w.total.text()=="0 hrs" and w.fte.text()=="-"
assert w.additional.text()==w.weeks.text()=="0"
assert [r.text() for r in w.rates]==list(DEFAULTS)
assert w.grab().save(str(EVIDENCE/"startup.png"))
for q,v in zip(w.quantities,["10","5","8","4"]):q.setText(v)
w.additional.setText("20");w.weeks.setText("5")
assert w.total.text()=="150 hrs" and w.fte.text()=="1.00"
assert [s.text() for s in w.subtotals]==["40","10","64","16"]
app.processEvents();assert w.grab().save(str(EVIDENCE/"calculated.png"))
w.rates[0].clear();assert w.total.text()==w.fte.text()=="-"
w.rates[0].setText("0");assert w.total.text()=="110 hrs"
w.reset_fields();w.additional.setText("300");w.weeks.setText("10")
assert w.total.text()=="300 hrs" and w.fte.text()=="1.00"
w.weeks.clear();assert w.total.text()=="300 hrs" and w.fte.text()=="-"
w.weeks.setText("0");assert w.fte.text()=="-"
w.weeks.setText("10");w.additional.setText("0");assert w.total.text()=="0 hrs" and w.fte.text()=="0.00"
w.reset_fields();w.quantities[0].setText("0");assert w.total.text()=="0 hrs"
w.reset_fields()
q=w.quantities[0];q.setFocus();QTest.keyClicks(q.lineEdit(),"1234");assert q.text()=="123"
QTest.keyClicks(q.lineEdit(),".5");assert q.text()=="123"
q.clear();QTest.keyClicks(q.lineEdit(),"999");QTest.keyClick(q,Qt.Key.Key_Up);assert number(q)==999
QTest.keyClick(q,Qt.Key.Key_Down);assert number(q)==998
q.clear();QTest.mouseClick(q,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(52,7));assert number(q)==1
a=w.additional;a.clear();a.setFocus();QTest.keyClicks(a.lineEdit(),"9999.99");assert a.text()=="9999.99"
QTest.keyClicks(a.lineEdit(),"9");assert a.text()=="9999.99"
QTest.keyClick(a,Qt.Key.Key_Up);assert number(a)==9999.99
a.clear();QTest.mouseClick(a,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(a.width()-12,7));assert number(a)==1
QTest.mouseClick(a,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(a.width()-12,23));assert number(a)==0
w.reset_fields()
for q,r in zip(w.quantities,w.rates):q.setText("999");r.setText("9999.99")
w.additional.setText("9999.99");w.weeks.setText("0.01");app.processEvents()
assert w.total.text()=="39,969,960.03 hrs"
for lab in [*w.subtotals,w.total,w.fte]:
    print(lab.text(),lab.fontMetrics().horizontalAdvance(lab.text()),lab.width())
    assert lab.fontMetrics().horizontalAdvance(lab.text())<=lab.width()
for spin in [w.weeks]:
    e=spin.lineEdit()
    print(spin.text(),spin.unit.text(),e.width(),spin.unit.geometry(),e.textMargins())
    assert spin.unit.geometry().right()<e.width(),spin.unit.text()
assert w.grab().save(str(EVIDENCE/"maximum.png"))
w.reset_fields()
def trace(n,modifier):
    a=[]
    for _ in range(n):
        a.append(app.focusWidget().accessibleName())
        QTest.keyClick(app.focusWidget(),Qt.Key.Key_Tab,modifier);app.processEvents()
    return a
w.activateWindow(); w.raise_(); QTest.qWait(100); w.quantities[0].setFocus();app.processEvents()
expected=[x.accessibleName() for x in w.fields]
assert trace(len(expected),Qt.KeyboardModifier.NoModifier)==expected
assert trace(len(expected),Qt.KeyboardModifier.ShiftModifier)==[expected[0],*reversed(expected[1:])]
d=w.make_settings();d.show();app.processEvents()
assert d.windowTitle()=="Settings | CTR Hours Estimator"
assert d.check_now_button.isEnabled()
assert d.grab().save(str(EVIDENCE/"settings.png"))
d.close();print("Window",w.width(),w.height())
print("PASS: calculations, other-only estimate, zero/missing inputs, reset, numeric bounds, actual arrow events, maximum widths, tab navigation, Settings")
w.close()
