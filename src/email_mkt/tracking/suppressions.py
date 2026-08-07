from dataclasses import dataclass


@dataclass(frozen=True)
class Suppression:
    email: str
    reason: str

