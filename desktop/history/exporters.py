import json
from pathlib import Path
from typing import List, Dict

from fpdf import FPDF


class HistoryExporter:
    def export(self, messages: List[Dict], fmt: str, path: str):
        fmt = fmt.lower()
        if fmt == 'json':
            self._export_json(messages, path)
        elif fmt in ('md', 'markdown'):
            self._export_markdown(messages, path)
        elif fmt == 'pdf':
            self._export_pdf(messages, path)
        else:
            raise ValueError(f'Неподдерживаемый формат экспорта: {fmt}')

    def _export_json(self, messages: List[Dict], path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    def _export_markdown(self, messages: List[Dict], path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        lines = ['# История чата\n']
        for msg in messages:
            lines.append(f"## {msg['role'].title()} ({msg['timestamp']})\n")
            lines.append(f"{msg['content']}\n")
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _export_pdf(self, messages: List[Dict], path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=12)
        pdf.cell(0, 10, txt='История чата', ln=True)
        for msg in messages:
            pdf.set_font('Arial', 'B', 11)
            pdf.multi_cell(0, 8, txt=f"{msg['role'].title()} ({msg['timestamp']})")
            pdf.set_font('Arial', size=10)
            pdf.multi_cell(0, 6, txt=msg['content'])
            pdf.ln(2)
        pdf.output(path)

