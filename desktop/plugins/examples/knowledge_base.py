import json
import os
from typing import List, Dict

from desktop.plugins.base import Plugin


class KnowledgeBasePlugin(Plugin):
    id = 'knowledge_base'
    name = 'База знаний'
    description = 'Отвечает на вопросы из локальной базы статей.'

    def __init__(self, config=None):
        super().__init__(config)
        self.data_path = self.config.get('data_path')
        self.articles = self._load_articles()

    def _load_articles(self) -> List[Dict[str, str]]:
        if not self.data_path or not os.path.exists(self.data_path):
            return []
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def execute(self, query: str) -> str:
        if not query:
            return 'Введите вопрос для поиска по базе знаний.'
        query_lower = query.lower()
        matches = [
            article for article in self.articles
            if query_lower in article['title'].lower() or query_lower in article['content'].lower()
        ]
        if not matches:
            return 'Подходящих статей не найдено.'
        top = matches[:3]
        lines = []
        for article in top:
            lines.append(f"• {article['title']}: {article['content']}")
        return '\n'.join(lines)

