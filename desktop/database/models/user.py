from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    full_name: str
    email: str
    organization: str
    role: str
    created_at: datetime


