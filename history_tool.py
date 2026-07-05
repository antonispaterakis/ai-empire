import os
import json
import datetime
import uuid

from crewai.tools import tool

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HISTORY_PATH = os.path.join(DATA_DIR, 'production_history.json')


def _load_history() -> dict:
    """Load the production history from disk."""
    if not os.path.exists(HISTORY_PATH):
        return {'runs': []}
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_history(history: dict) -> None:
    """Write the production history back to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


@tool("production_history")
def history_tool() -> str:
    """
    Reads the production history and returns a summary of all past content runs.
    Use this to understand what X (Twitter) threads, hooks, and topics have been generated before.
    """
    history = _load_history()
    runs = history.get('runs', [])

    if not runs:
        return (
            "No production history yet. This is the first run. "
            "Produce a strategy based on general X/Twitter best practices."
        )

    lines = [f"Production History ({len(runs)} past runs):\n"]
    # Show the most recent 10 runs
    for run in runs[-10:]:
        linked = run.get('linked_tweet_id')
        link_status = f" -> published as tweet {linked}" if linked else " (not yet published)"
        lines.append(
            f"- [{run.get('created_at', '?')}] Topic: \"{run.get('topic', '?')}\" | "
            f"Hook: \"{run.get('hook', 'N/A')}\" | "
            f"Strategy used: \"{run.get('strategy_brief', 'N/A')[:80]}...\""
            f"{link_status}"
        )

    lines.append(
        "\nUse this data to find patterns: which topics and hook styles "
        "have been tried, and (if linked) how they correlated with X (Twitter) performance."
    )
    return '\n'.join(lines)


def save_run(topic: str, strategy_brief: str, hook: str, thread_summary: str) -> str:
    """
    Save a completed production run to the history.
    Returns the run ID.
    """
    history = _load_history()
    run_id = f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    run_entry = {
        'id': run_id,
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'topic': topic,
        'strategy_brief': strategy_brief,
        'hook': hook,
        'thread_summary': thread_summary,
        'linked_tweet_id': None,
    }

    history['runs'].append(run_entry)
    _save_history(history)
    return run_id


def link_tweet(run_id: str, tweet_id: str) -> bool:
    """
    Link a published X tweet ID to a past production run.
    """
    history = _load_history()
    for run in history['runs']:
        if run['id'] == run_id:
            run['linked_tweet_id'] = tweet_id
            _save_history(history)
            return True
    return False


def list_unpublished_runs() -> list[dict]:
    """Return runs that haven't been linked to an X post yet."""
    history = _load_history()
    return [r for r in history['runs'] if r.get('linked_tweet_id') is None]
