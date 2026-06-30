"""
Lightweight pattern extraction from (title, view_count, publish_date) tuples.

For each video, computes simple title-level features (word count, presence of
a number, presence of a question mark, day-of-week posted) and checks whether
those features correlate with view count by comparing the top half vs bottom
half of videos by views — similar in spirit to ViralSignal's validator.

If scipy is installed, uses chi-square (for binary/categorical features) and
Mann-Whitney U (for word count) to get a p-value. Otherwise falls back to a
plain group comparison (proportions / means), which is good enough for a
scaffold.
"""

import re
from collections import Counter
from datetime import datetime

try:
    from scipy import stats as scipy_stats

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def extract_features(title, publish_date):
    """Compute simple per-title features."""
    day_of_week = None
    if publish_date:
        try:
            dt = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
            day_of_week = DAY_NAMES[dt.weekday()]
        except ValueError:
            pass

    return {
        "word_count": len(title.split()),
        "has_number": bool(re.search(r"\d", title)),
        "has_question_mark": "?" in title,
        "day_of_week": day_of_week,
    }


def find_correlated_patterns(videos, top_n=3):
    """Given a list of (title, view_count, publish_date) tuples, return up to
    `top_n` human-readable findings about which title features correlate with
    higher views, ranked by effect size."""
    if len(videos) < 4:
        return []

    enriched = []
    for title, views, publish_date in videos:
        features = extract_features(title, publish_date)
        features["views"] = views
        enriched.append(features)

    enriched.sort(key=lambda v: v["views"], reverse=True)
    midpoint = len(enriched) // 2
    top_half = enriched[:midpoint]
    bottom_half = enriched[midpoint:]

    findings = []

    # Binary features: presence of a number / question mark in the title.
    for feature, label in (("has_number", "numbers"), ("has_question_mark", "a question mark")):
        top_rate = sum(1 for v in top_half if v[feature]) / len(top_half)
        bottom_rate = sum(1 for v in bottom_half if v[feature]) / len(bottom_half)
        diff = top_rate - bottom_rate

        p_value = None
        if HAS_SCIPY:
            table = [
                [sum(1 for v in top_half if v[feature]), sum(1 for v in top_half if not v[feature])],
                [sum(1 for v in bottom_half if v[feature]), sum(1 for v in bottom_half if not v[feature])],
            ]
            try:
                _, p_value, _, _ = scipy_stats.chi2_contingency(table)
            except ValueError:
                p_value = None

        if abs(diff) >= 0.15:  # at least a 15-percentage-point gap
            direction = "more" if diff > 0 else "less"
            findings.append(
                {
                    "feature": feature,
                    "description": (
                        f"Top-performing titles use {label} {direction} often "
                        f"({top_rate:.0%} of top half vs {bottom_rate:.0%} of bottom half)"
                    ),
                    "effect_size": abs(diff),
                    "p_value": p_value,
                }
            )

    # Continuous feature: title word count.
    top_avg_words = sum(v["word_count"] for v in top_half) / len(top_half)
    bottom_avg_words = sum(v["word_count"] for v in bottom_half) / len(bottom_half)
    word_diff = top_avg_words - bottom_avg_words

    p_value = None
    if HAS_SCIPY:
        try:
            _, p_value = scipy_stats.mannwhitneyu(
                [v["word_count"] for v in top_half],
                [v["word_count"] for v in bottom_half],
            )
        except ValueError:
            p_value = None

    if abs(word_diff) >= 1:
        direction = "longer" if word_diff > 0 else "shorter"
        findings.append(
            {
                "feature": "word_count",
                "description": (
                    f"Top-performing titles tend to be {direction} "
                    f"({top_avg_words:.1f} vs {bottom_avg_words:.1f} words on average)"
                ),
                "effect_size": abs(word_diff),
                "p_value": p_value,
            }
        )

    # Categorical feature: day of week posted.
    top_days = [v["day_of_week"] for v in top_half if v["day_of_week"]]
    if top_days:
        most_common_day, count = Counter(top_days).most_common(1)[0]
        rate = count / len(top_days)
        if rate >= 0.4:
            findings.append(
                {
                    "feature": "day_of_week",
                    "description": f"Top-performing videos are often posted on {most_common_day} ({rate:.0%} of the top half)",
                    "effect_size": rate,
                    "p_value": None,
                }
            )

    findings.sort(key=lambda f: f["effect_size"], reverse=True)
    return findings[:top_n]
