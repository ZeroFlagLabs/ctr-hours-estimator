"""Source and frozen application runtime checks."""
import sys,json,traceback
from pathlib import Path
from PySide6.QtCore import QTimer,QEventLoop
from PySide6.QtWidgets import QDialogButtonBox
from preferences import FACTORY_DEFAULTS,FACTORY_VALUES,load_rates
from app_info import APP_VERSION

def run(app,w):
    report={}
    output=Path(sys.argv[sys.argv.index("--self-test-output")+1]) if "--self-test-output" in sys.argv else None
    try:
        app.processEvents()
        assert (w.width(),w.height())==(565,335)
        assert not w.windowIcon().isNull()
        assert w.total.text()=="-" and w.fte.text()=="-"
        assert tuple(r.text() for r in w.rates)==FACTORY_DEFAULTS
        for q,v in zip(w.quantities,("10","5","8","4")):q.setText(v)
        w.additional.setText("20");w.weeks.setText("5")
        assert w.total.text()=="150 hrs" and w.fte.text()=="1.00"
        d=w.make_settings();d.show();app.processEvents()
        assert [d.settings_tabs.tabText(i) for i in range(4)]==["Defaults","Assumptions","Updates","About"]
        assert d.current_version.text()=="Current version: v"+APP_VERSION
        assert "MIT Licence" in d.about_text.text()
        assert d.github_link.openExternalLinks()
        assert d.save_defaults_button.size()==d.restore_defaults_button.size()==d.buttons.button(QDialogButtonBox.StandardButton.Close).size()
        assert len(d.default_fields)==5 and all(f.size()==d.save_defaults_button.size() for f in d.default_fields)
        d.default_fields[0].setText("6.25")
        d.default_fields[4].setText("37.5")
        d.save_defaults_button.click()
        assert w.rates[0].text()=="6.25" and w.total.text()=="190 hrs" and w.fte.text()=="1.27" and w.additional.text()=="37.5"
        assert load_rates(w.preferences)==("6.25","2","8","4","37.5")
        d.restore_defaults_button.click();d.save_defaults_button.click()
        assert w.total.text()=="130 hrs" and load_rates(w.preferences)==FACTORY_VALUES
        d.reject()
        w.reset_fields();assert w.total.text()=="-" and w.fte.text()=="-"
        w.additional.setText("300");w.weeks.setText("10")
        assert w.total.text()=="300 hrs" and w.fte.text()=="1.00"
        w.additional.setText("0");assert w.total.text()==w.fte.text()=="-"
        w.quantities[0].setText("0");assert w.total.text()=="0 hrs" and w.fte.text()=="0.00"
        w.quantities[0].clear();assert w.total.text()==w.fte.text()=="-"
        report["functional"]="passed"
        if output:w.grab().save(str(output.with_suffix(".png")))
        if "--live-update-test" in sys.argv:
            loop=QEventLoop()
            def done():
                if w.update_checker._reply is None:loop.quit()
            w.update_checker.state_changed.connect(done)
            w.update_checker.check()
            QTimer.singleShot(15000,loop.quit)
            if w.update_checker._reply is not None:loop.exec()
            report["live_update"]=w.update_checker.status
            assert w.update_checker.status in ("Up to date.","No published GitHub release found yet."),w.update_checker.status
        report["result"]="passed"
        return 0
    except Exception:
        report["result"]="failed";report["traceback"]=traceback.format_exc()
        return 1
    finally:
        if output:output.write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps(report),flush=True)
        w.close()
