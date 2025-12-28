"""
retrieval.py - Episode search and ranking algorithms

Provides keyword search and scoring functions for episode retrieval.
Embedding-based search is handled separately in embeddings.py.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .storage import get_sophia_dir, get_episode_index, read_episode
from .models import Episode


def keyword_search(query: str, k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
    """
    Search episode index by keywords.

    Args:
        query: Search query string
        k: Maximum number of results to return

    Returns:
        List of (index_entry, match_score) tuples, sorted by score descending
    """
    # Tokenize query into keywords
    query_keywords = set(re.findall(r'\w+', query.lower()))

    if not query_keywords:
        return []

    # Get episode index
    index = get_episode_index()
    entries = index.get("entries", [])

    scored_entries = []

    for entry in entries:
        # Build searchable text from entry
        searchable = []
        if entry.get("goal_summary"):
            searchable.append(entry["goal_summary"].lower())
        if entry.get("keywords"):
            searchable.extend(k.lower() for k in entry["keywords"])

        text = " ".join(searchable)

        # Count keyword matches
        matches = sum(1 for kw in query_keywords if kw in text)

        if matches > 0:
            # Normalize score by number of query keywords
            match_score = matches / len(query_keywords)
            scored_entries.append((entry, match_score))

    # Sort by score descending
    scored_entries.sort(key=lambda x: x[1], reverse=True)

    return scored_entries[:k]


def compute_retrieval_score(
    entry: Dict[str, Any],
    similarity: float,
    episode: Optional[Episode] = None
) -> float:
    """
    Composite score for retrieval ranking.
    High-reward successful episodes surface first.

    Args:
        entry: Episode index entry
        similarity: Base similarity/match score (0-1)
        episode: Full episode object if available

    Returns:
        Composite score (capped at 1.0)
    """
    base_score = similarity

    # Boost successful episodes
    outcome = entry.get("outcome") or (episode.outcome if episode else None)
    if outcome == 'SUCCESS':
        base_score *= 1.2

    # Boost episodes with heuristics
    heuristics_count = entry.get("heuristics_count", 0)
    if episode and episode.heuristics:
        heuristics_count = len(episode.heuristics)
    if heuristics_count:
        base_score += 0.1 * heuristics_count

    # Penalize consolidated (already abstracted)
    if entry.get("consolidated", False):
        base_score *= 0.8

    # Recency boost
    timestamp_str = entry.get("timestamp")
    if timestamp_str:
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            days_old = (datetime.now(timestamp.tzinfo) - timestamp).days
            if days_old < 7:
                base_score += 0.1
            elif days_old < 30:
                base_score += 0.05
        except (ValueError, TypeError):
            pass

    return min(1.0, base_score)


def get_recent_episodes(n: int = 5) -> List[Dict[str, Any]]:
    """
    Get the N most recent episodes from the index.

    Args:
        n: Number of episodes to return

    Returns:
        List of episode index entries
    """
    index = get_episode_index()
    entries = index.get("entries", [])

    # Entries are already sorted by recency (newest first)
    return entries[:n]


def search_episodes(
    query: str,
    k: int = 5,
    include_full: bool = False
) -> List[Dict[str, Any]]:
    """
    Search episodes with scoring and optional full episode loading.

    Args:
        query: Search query
        k: Maximum results
        include_full: Whether to load full episode data

    Returns:
        List of result dicts with scores
    """
    results = []

    # Perform keyword search
    matches = keyword_search(query, k=k*2)

    for entry, match_score in matches[:k]:
        # Compute retrieval score
        score = compute_retrieval_score(entry, match_score)

        result = {
            "episode_id": entry.get("id"),
            "relevance_score": round(score, 2),
            "goal_summary": entry.get("goal_summary", ""),
            "outcome": entry.get("outcome", "UNKNOWN"),
            "timestamp": entry.get("timestamp"),
            "tool_call_count": entry.get("tool_call_count", 0),
            "heuristics_count": entry.get("heuristics_count", 0),
        }

        # Optionally load full episode
        if include_full:
            episode = read_episode(entry.get("id"))
            if episode:
                result["heuristics"] = episode.heuristics
                result["keywords"] = episode.keywords
                result["chain_of_thought"] = episode.chain_of_thought
                result["error_analysis"] = episode.error_analysis

        results.append(result)

    return results


def get_episodes_for_reflection(
    episode_ids: Optional[List[str]] = None,
    recent: int = 5
) -> List[Episode]:
    """
    Get episodes for reflection analysis.

    Args:
        episode_ids: Specific episode IDs to load
        recent: Number of recent episodes if no IDs specified

    Returns:
        List of full Episode objects
    """
    episodes = []

    if episode_ids:
        for ep_id in episode_ids:
            episode = read_episode(ep_id)
            if episode:
                episodes.append(episode)
    else:
        # Get recent episodes
        recent_entries = get_recent_episodes(recent)
        for entry in recent_entries:
            episode = read_episode(entry.get("id"))
            if episode:
                episodes.append(episode)

    return episodes


def get_unconsolidated_episodes(min_count: int = 5) -> List[Episode]:
    """
    Get episodes that haven't been consolidated yet.

    Args:
        min_count: Minimum number of unconsolidated episodes to return

    Returns:
        List of unconsolidated Episode objects
    """
    index = get_episode_index()
    entries = index.get("entries", [])

    unconsolidated = []
    for entry in entries:
        if not entry.get("consolidated", False) and not entry.get("trivial", False):
            episode = read_episode(entry.get("id"))
            if episode:
                unconsolidated.append(episode)
            if len(unconsolidated) >= min_count:
                break

    return unconsolidated
