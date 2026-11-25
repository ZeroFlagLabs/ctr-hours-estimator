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
from PySide6.QtWidgets import QStyleOptionSpinBox,QStyle
a=make_app();w=Window(_test_settings);w.show();w.activateWindow();QTest.qWait(60)
assert w.additional.text()==w.weeks.text()=="0"
def state(s):
    e=s.lineEdit()
    im=s.grab().toImage()
    # dark numeric glyphs, not the border or arrow gutter
    dpr=im.devicePixelRatio()
    xs=[]
    for x in range(int(3*dpr),int((s.width()-19)*dpr)):
        for y in range(int(8*dpr),int(23*dpr)):
            c=im.pixelColor(x,y)
            if c.red()<100 and c.green()<120 and c.blue()<160:
                xs.append(x);break
    opt=QStyleOptionSpinBox();s.initStyleOption(opt)
    arrow=s.style().subControlRect(QStyle.ComplexControl.CC_SpinBox,opt,QStyle.SubControl.SC_SpinBoxUp,s)
    return (e.geometry(),e.textMargins(),s.unit.geometry() if s.unit.text() else None,min(xs) if xs else None,max(xs) if xs else None,arrow)
for s in w.fields:
    s.setText("999" if s.integer else "9999.99")
    w.quantities[1 if s is w.quantities[0] else 0].setFocus();QTest.qWait(25)
    s.lineEdit().deselect()
    before=state(s)
    QTest.mouseClick(s.lineEdit(),Qt.MouseButton.LeftButton,pos=QPoint(s.lineEdit().width()-3,s.lineEdit().height()//2))
    QTest.qWait(25);s.lineEdit().deselect()
    after=state(s)
    # Cursor may add one dark pixel; geometry and margins must never shift.
    assert before[:3]==after[:3],(s.accessibleName(),before,after)
    assert before[3]==after[3],(s.accessibleName(),before,after)
    assert before[-1]==after[-1],(s.accessibleName(),before,after)
    e=s.lineEdit()
    assert e.fontMetrics().horizontalAdvance(s.text())+e.textMargins().left()+e.textMargins().right()+3<=e.width(),(s.accessibleName(),e.width())
    if s.unit.text():
        assert e.cursorPosition()==len(e.text())
        assert s.unit.geometry().right()<e.width()
        QTest.keyClick(e,Qt.Key.Key_Delete);assert s.text()=="9999.99"
    print(s.accessibleName(),s.width(),"stable",before[3],after[3])
for lab in w.work_group.findChildren(QLabel):
    if lab.text() and not lab.parent().inherits("QLineEdit"):
        assert lab.fontMetrics().horizontalAdvance(lab.text())<=lab.width(),(lab.text(),lab.width())
assert w.grab().save(str(EVIDENCE/"maximum_all.png"))
w.reset_fields()
assert w.additional.text()==w.weeks.text()=="0"
assert all(not q.text() for q in w.quantities)
assert w.total.text()=="0 hrs" and w.fte.text()=="-"
assert w.grab().save(str(EVIDENCE/"startup_final.png"))
print("PASS: stable focus geometry, text inset, arrow positions, all maximum inputs fit, labels fit, zero defaults and reset")
w.close()
