import argparse
import glob
import json
import os

from desktop.training.reports.plotter import ReportPlotter


def load_history_from_reports(report_dir: str):
    history = {}
    for path in sorted(glob.glob(os.path.join(report_dir, 'report-*.json'))):
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        metrics = payload.get('metrics', {})
        step = payload.get('timestamp')
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                history.setdefault(key, []).append({'step': step, 'value': value})
    return history


def main():
    parser = argparse.ArgumentParser(description='Построение графиков по готовым отчётам')
    parser.add_argument('--reports', default=os.path.join('data', 'reports'))
    parser.add_argument('--output', default=os.path.join('data', 'reports'))
    args = parser.parse_args()

    history = load_history_from_reports(args.reports)
    if not history:
        raise SystemExit('Не найдено отчётов с метриками')
    plotter = ReportPlotter(args.output)
    plot_path = plotter.plot_metrics(history, 'summary-metrics.png')
    print(f'График сохранён в {plot_path}')


if __name__ == '__main__':
    main()

