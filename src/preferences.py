"""Validated, explicitly saved estimate defaults."""
import json
import re
from PySide6.QtCore import QSettings

FACTORY_DEFAULTS = ("4", "2", "8", "4")
TASK_NAMES = ("New P/Ns", "Revised P/Ns", "New drawings", "Revised drawings")
DEFAULT_NAMES = (*TASK_NAMES, "Other hours")
FACTORY_VALUES = (*FACTORY_DEFAULTS, "0")
LEGACY_KEY = "defaults/task_hours"
KEY = "defaults/hours"
PATTERN = re.compile(r"[0-9]{1,4}(?:\.[0-9]{1,2})?")

def valid_rates(values, count=5):
    return (isinstance(values, (tuple,list)) and len(values)==count
            and all(isinstance(v,str) and PATTERN.fullmatch(v) for v in values))

def app_settings():
    # Stable per-user identity across production releases.
    return QSettings(QSettings.Format.NativeFormat, QSettings.Scope.UserScope,
                     "ZeroFlagLabs", "CTR Hours Estimator")

def load_rates(settings):
    settings.sync()
    try:
        if settings.contains(KEY):
            values=json.loads(settings.value(KEY,"",type=str))
            if valid_rates(values): return tuple(values)
        else:
            values=json.loads(settings.value(LEGACY_KEY,"",type=str))
            if valid_rates(values,4): return (*values,"0")
    except (ValueError,TypeError):
        pass
    return FACTORY_VALUES

def save_rates(settings, values):
    if not valid_rates(values):
        raise ValueError("Enter all five defaults, from 0 to 9999.99 hours.")
    settings.setValue(KEY,json.dumps(list(values)))
    settings.sync()
    if settings.status()!=QSettings.Status.NoError:
        raise OSError("Unable to save defaults.")
