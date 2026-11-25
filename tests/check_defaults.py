import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from main import *
EVIDENCE=Path(__file__).resolve().parents[1]/"docs/private/release-validation"
EVIDENCE.mkdir(parents=True,exist_ok=True)
from preferences import KEY, LEGACY_KEY, FACTORY_VALUES, DEFAULT_NAMES
from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from uuid import uuid4
import subprocess,json
app=make_app()
name="CTR Hours Estimator Test "+uuid4().hex
def store():
    return QSettings(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,"ZeroFlagLabs",name)
settings=store()
def defaults(w):return (*[x.text() for x in w.rates],w.additional.text())
def draft(d):return tuple(x.text() for x in d.default_fields)
def click(btn):
    QTest.mouseClick(btn,Qt.MouseButton.LeftButton);app.processEvents()
def open_dialog(w):
    d=w.make_settings();d.show();d.activateWindow();QTest.qWait(50);return d
def read_fresh():
    command="from PySide6.QtCore import QSettings; from preferences import load_rates; import json; s=QSettings(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,'ZeroFlagLabs',"+repr(name)+"); print(json.dumps(load_rates(s)))"
    return tuple(json.loads(subprocess.check_output([sys.executable,"-B","-c",command],cwd=HERE,text=True)))
try:
    assert read_fresh()==FACTORY_VALUES
    settings.setValue(LEGACY_KEY,json.dumps(["5","3","7.5","2.25"]));settings.sync()
    assert read_fresh()==("5","3","7.5","2.25","0")
    settings.remove(LEGACY_KEY);settings.sync()
    w=Window(settings);w.show();app.processEvents()
    assert defaults(w)==FACTORY_VALUES
    assert w.work_group.title()=="Work breakdown"
    assert any(g.title()=="Project duration" for g in w.findChildren(QGroupBox))
    w.quantities[0].setText("10");w.rates[0].setText("5");w.weeks.setText("5");w.additional.setText("20")
    before=(tuple(q.text() for q in w.quantities),w.weeks.text())
    d=open_dialog(w)
    assert [d.settings_tabs.tabText(i) for i in range(4)]==["Defaults","Assumptions","Updates","About"]
    assert len(d.default_fields)==5 and draft(d)==FACTORY_VALUES and not d.save_defaults_button.isEnabled()
    close=d.buttons.button(QDialogButtonBox.StandardButton.Close)
    assert close.size()==d.restore_defaults_button.size()==d.save_defaults_button.size()==QSize(112,30)
    assert all(f.size()==d.save_defaults_button.size() for f in d.default_fields)
    assert d.grab().save(str(EVIDENCE/"defaults_factory.png"))
    proposed=("6.25","0","9999.99","3.5","37.5")
    for f,v in zip(d.default_fields,proposed):f.setText(v)
    for f in d.default_fields:
        e=f.lineEdit();assert e.fontMetrics().horizontalAdvance(f.text())+e.textMargins().left()+e.textMargins().right()+3<=e.width()
        assert f.unit.geometry().right()<e.width()
    assert d.grab().save(str(EVIDENCE/"defaults_max.png"))
    d.default_fields[4].clear();assert not d.save_defaults_button.isEnabled()
    d.default_fields[4].setText(".");assert not d.save_defaults_button.isEnabled()
    d.default_fields[4].setText("9999.99")
    assert d.save_defaults_button.isEnabled()
    d.default_fields[4].setText(proposed[4]);click(d.save_defaults_button)
    assert w.saved_defaults==proposed and read_fresh()==proposed and defaults(w)==proposed
    assert (tuple(q.text() for q in w.quantities),w.weeks.text())==before
    assert w.total.text()=="100 hrs" and w.fte.text()=="0.67"
    assert not d.save_defaults_button.isEnabled()
    assert "Defaults saved" in d.defaults_status.text()
    assert d.grab().save(str(EVIDENCE/"defaults_saved.png"))
    click(d.restore_defaults_button)
    assert draft(d)==FACTORY_VALUES and read_fresh()==proposed and defaults(w)==proposed
    d.reject()
    d=open_dialog(w)
    assert draft(d)==proposed
    d.reject()
    w.reset_fields()
    assert defaults(w)==proposed and w.weeks.text()=="0"
    assert w.total.text()=="37.5 hrs"
    assert all(not q.text() for q in w.quantities)
    w2=Window(store());assert defaults(w2)==proposed
    d=open_dialog(w2);click(d.restore_defaults_button);click(d.save_defaults_button)
    assert read_fresh()==FACTORY_VALUES and defaults(w2)==FACTORY_VALUES
    d.reject();w2.reset_fields();assert defaults(w2)==FACTORY_VALUES
    settings.setValue(KEY,'["4","2","8","4","-1"]');settings.sync()
    assert read_fresh()==FACTORY_VALUES
    settings.setValue(KEY,'not-json');settings.sync()
    assert read_fresh()==FACTORY_VALUES
    assert not valid_rates(("4","2","8","4","10000"))
    assert not valid_rates(("4","2","8","4","1.234"))
    assert not valid_rates(("4","2","8","4",""))
    w2.close();w.close()
    print("PASS: five defaults, four-value migration, registry persistence, immediate recalculation, reset, restore/discard, equal dimensions, numeric validation")
finally:
    settings.clear();settings.sync()
