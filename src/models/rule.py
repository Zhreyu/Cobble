#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

@dataclass
class Rule:
    name: str
    category: str
    extension: Optional[str] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    keywords: Optional[List[str]] = None
    priority: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Rule':
        """
        Reconstruct a Rule object from a dictionary, converting date strings to
        datetime objects if a date_range exists.
        """
        if 'date_range' in data and data['date_range']:
            data['date_range'] = tuple(
                datetime.fromisoformat(d) if d else None
                for d in data['date_range']
            )
        return cls(**data)
