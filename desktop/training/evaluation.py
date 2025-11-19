from typing import Dict, Any

from transformers import Trainer, EvalPrediction
import math


class EvaluationRunner:
    def __init__(self, trainer: Trainer, metric: str = 'perplexity'):
        self.trainer = trainer
        self.metric = metric

    def run(self) -> Dict[str, Any]:
        results = self.trainer.evaluate()
        metrics = {}
        if 'eval_loss' in results and self.metric == 'perplexity':
            metrics['perplexity'] = math.exp(results['eval_loss'])
        metrics.update({k: v for k, v in results.items() if k.startswith('eval_')})
        return metrics


