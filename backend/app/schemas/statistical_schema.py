from enum import Enum


class PeriodType(str, Enum):
    Weekly = "Weekly"
    Monthly = "Monthly"
    Yearly = "Yearly"