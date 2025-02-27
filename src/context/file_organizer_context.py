#!/usr/bin/env python3

import json
from datetime import datetime
from typing import Dict, List

from src.models.rule import Rule

class FileOrganizerContext:
    def __init__(self):
        self.rules: List[Rule] = []
        self.category_history: Dict[str, str] = {}
        self.conversation_history: List[Dict] = []
        # You can add/change default categories here:
        self.default_categories = ["Personal", "Uncategorized"]
        
    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        # Sort rules by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
    def get_matching_rules(self, file_path: str, content: str, metadata: dict) -> List[Rule]:
        matching_rules = []
        for rule in self.rules:
            if self._rule_matches(rule, file_path, content, metadata):
                matching_rules.append(rule)
        return matching_rules
    
    def _rule_matches(self, rule: Rule, file_path: str, content: str, metadata: dict) -> bool:
        from datetime import datetime
        
        # Match by file extension
        if rule.extension and not file_path.lower().endswith(rule.extension.lower()):
            return False

        # Match by date range
        if rule.date_range:
            file_date = metadata.get('modified_date', datetime.now())
            start_date, end_date = rule.date_range
            if start_date and end_date and not (start_date <= file_date <= end_date):
                return False

        # Match by keywords
        if rule.keywords:
            content_lower = content.lower()
            if not any(kw.lower() in content_lower for kw in rule.keywords):
                return False

        return True

    def add_conversation_entry(self, role: str, content: str) -> None:
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def to_json(self) -> str:
        data = {
            'rules': [rule.to_dict() for rule in self.rules],
            'category_history': self.category_history,
            'conversation_history': self.conversation_history,
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FileOrganizerContext':
        data = json.loads(json_str)
        context = cls()
        # Rebuild rules
        context.rules = [Rule.from_dict(rule_data) for rule_data in data['rules']]
        context.category_history = data['category_history']
        context.conversation_history = data['conversation_history']
        return context
