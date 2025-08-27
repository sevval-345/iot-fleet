
# app/models/enums.py
from enum import Enum

class Action(str, Enum):
    freeze_24h = "freeze_24h"
    throttle = "throttle"
    notify = "notify"

class AnomalyType(str, Enum):
    spike = "spike"
    drain = "drain"
    inactivity = "inactivity"
    roaming = "roaming"
