import json
import os
from datetime import datetime
from typing import Any


def save_execution_report(response: Any, user_prompt: str, session_id: str) -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    session_dir = os.path.join(project_root, "sessions", f"session_{session_id}")
    os.makedirs(session_dir, exist_ok=True)

    usage = response.usage
    input_t = usage.input_tokens
    output_t = usage.output_tokens
    total_t = usage.total_tokens

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(session_dir, f"reporte_{timestamp}.json")

    reporte_individual = {
        "timestamp": timestamp,
        "prompt": user_prompt,
        "tokens": {"entrada": input_t, "salida": output_t, "total": total_t},
        "historial": json.loads(response.all_messages_json().decode("utf-8")),
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(reporte_individual, f, indent=2, ensure_ascii=False)

    summary_path = os.path.join(session_dir, "tokens_summary.json")

    summary = {
        "total_input": 0,
        "total_output": 0,
        "total_tokens_acumulados": 0,
        "total_llamados": 0,
    }

    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)

    summary["total_input"] += input_t
    summary["total_output"] += output_t
    summary["total_tokens_acumulados"] += total_t
    summary["total_llamados"] += 1

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
