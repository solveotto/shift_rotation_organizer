"""
Shift Matcher - Find similar shifts across turnus years based on statistics

This module provides functionality to match shifts from one turnus year to another
based on their statistical characteristics (night shifts, weekend hours, early shifts, etc.)
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional

from config import conf
from app.utils import db_utils


# Stats to use for similarity comparison with their weights
# Higher weight = more important in matching
STAT_WEIGHTS = {
    'tidlig': 1.0,           # Early shifts
    'ettermiddag': 1.0,      # Afternoon shifts
    'natt': 1.5,             # Night shifts (weighted higher)
    'helgetimer': 1.5,       # Weekend hours (weighted higher)
    'helgedager': 1.0,       # Weekend days
    'before_6': 0.8,         # Very early starts
    'natt_helg': 1.2,        # Night shifts on weekends
}


def load_stats_for_turnus_set(turnus_set_id: int) -> Optional[pd.DataFrame]:
    """
    Load the statistics DataFrame for a turnus set.

    Args:
        turnus_set_id: The ID of the turnus set

    Returns:
        DataFrame with shift statistics, or None if not found
    """
    turnus_set = db_utils.get_turnus_set_by_id(turnus_set_id)
    if not turnus_set:
        return None

    year_id = turnus_set['year_identifier']

    # Try the df_file_path from database first
    df_path = turnus_set.get('df_file_path')
    if df_path and os.path.exists(df_path):
        try:
            return pd.read_json(df_path)
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback to standard location
    standard_path = os.path.join(
        conf.static_dir, 'turnusfiler',
        year_id.lower(), f'turnus_df_{year_id}.json'
    )

    if os.path.exists(standard_path):
        try:
            return pd.read_json(standard_path)
        except (json.JSONDecodeError, ValueError):
            return None

    return None


def get_shift_stats(df: pd.DataFrame, shift_title: str) -> Optional[Dict]:
    """
    Get statistics for a specific shift from the DataFrame.

    Args:
        df: Statistics DataFrame
        shift_title: Name of the shift

    Returns:
        Dictionary of stats, or None if shift not found
    """
    if df is None or 'turnus' not in df.columns:
        return None

    shift_row = df[df['turnus'] == shift_title]
    if shift_row.empty:
        return None

    return shift_row.iloc[0].to_dict()


def normalize_stats(stats: Dict, all_stats_df: pd.DataFrame) -> Dict:
    """
    Normalize statistics to 0-1 range based on min/max in the dataset.

    Args:
        stats: Dictionary of raw stats for one shift
        all_stats_df: DataFrame with all shifts to get min/max from

    Returns:
        Dictionary with normalized stats
    """
    normalized = {}

    for stat_name in STAT_WEIGHTS.keys():
        if stat_name not in stats or stat_name not in all_stats_df.columns:
            normalized[stat_name] = 0.0
            continue

        value = stats[stat_name]
        col_min = all_stats_df[stat_name].min()
        col_max = all_stats_df[stat_name].max()

        if col_max == col_min:
            normalized[stat_name] = 0.5
        else:
            normalized[stat_name] = (value - col_min) / (col_max - col_min)

    return normalized


def calculate_similarity(stats1: Dict, stats2: Dict,
                         df1: pd.DataFrame, df2: pd.DataFrame) -> float:
    """
    Calculate similarity score between two shifts based on normalized statistics.

    Args:
        stats1: Stats dictionary for first shift
        stats2: Stats dictionary for second shift
        df1: Full stats DataFrame for first turnus set (for normalization)
        df2: Full stats DataFrame for second turnus set (for normalization)

    Returns:
        Similarity score between 0 and 1 (1 = identical)
    """
    norm1 = normalize_stats(stats1, df1)
    norm2 = normalize_stats(stats2, df2)

    weighted_squared_diff = 0.0
    total_weight = 0.0

    for stat_name, weight in STAT_WEIGHTS.items():
        diff = norm1.get(stat_name, 0) - norm2.get(stat_name, 0)
        weighted_squared_diff += weight * (diff ** 2)
        total_weight += weight

    # Euclidean distance normalized by weights
    distance = np.sqrt(weighted_squared_diff / total_weight)

    # Convert distance to similarity (0-1, where 1 is identical)
    similarity = 1 / (1 + distance)

    return round(similarity, 3)


def find_similar_shifts(source_turnus_set_id: int,
                        target_turnus_set_id: int,
                        shift_title: str,
                        top_n: int = 5) -> List[Dict]:
    """
    Find shifts in target turnus set that are most similar to a shift in source set.

    Args:
        source_turnus_set_id: ID of the turnus set containing the source shift
        target_turnus_set_id: ID of the turnus set to search for similar shifts
        shift_title: Name of the source shift
        top_n: Number of top matches to return

    Returns:
        List of dicts with 'shift', 'similarity', and 'stats' keys, sorted by similarity
    """
    source_df = load_stats_for_turnus_set(source_turnus_set_id)
    target_df = load_stats_for_turnus_set(target_turnus_set_id)

    if source_df is None or target_df is None:
        return []

    source_stats = get_shift_stats(source_df, shift_title)
    if source_stats is None:
        return []

    matches = []

    for _, row in target_df.iterrows():
        target_shift = row['turnus']
        target_stats = row.to_dict()

        similarity = calculate_similarity(
            source_stats, target_stats,
            source_df, target_df
        )

        matches.append({
            'shift': target_shift,
            'similarity': similarity,
            'stats': {k: target_stats.get(k) for k in STAT_WEIGHTS.keys()}
        })

    # Sort by similarity descending
    matches.sort(key=lambda x: x['similarity'], reverse=True)

    return matches[:top_n]


def find_matches_for_favorites(user_id: int,
                               source_turnus_set_id: int,
                               target_turnus_set_id: int,
                               top_n: int = 3) -> List[Dict]:
    """
    Find similar shifts in target year for all of a user's favorites from source year.

    Args:
        user_id: The user's ID
        source_turnus_set_id: ID of the turnus set to get favorites from
        target_turnus_set_id: ID of the turnus set to find matches in
        top_n: Number of matches per favorite

    Returns:
        List of dicts, each containing:
        - source_shift: Name of the favorited shift
        - source_stats: Stats of the source shift
        - matches: List of similar shifts in target year
    """
    # Get user's favorites from source turnus set
    favorites = db_utils.get_favorite_lst(user_id, source_turnus_set_id)

    if not favorites:
        return []

    source_df = load_stats_for_turnus_set(source_turnus_set_id)
    target_df = load_stats_for_turnus_set(target_turnus_set_id)

    if source_df is None or target_df is None:
        return []

    results = []

    for shift_title in favorites:
        source_stats = get_shift_stats(source_df, shift_title)

        if source_stats is None:
            continue

        matches = find_similar_shifts(
            source_turnus_set_id,
            target_turnus_set_id,
            shift_title,
            top_n
        )

        results.append({
            'source_shift': shift_title,
            'source_stats': {k: source_stats.get(k) for k in STAT_WEIGHTS.keys()},
            'matches': matches
        })

    return results


def get_all_turnus_sets_with_stats() -> List[Dict]:
    """
    Get all turnus sets that have statistics files available.

    Returns:
        List of turnus set info dicts with 'id', 'name', 'year_identifier'
    """
    all_sets = db_utils.get_all_turnus_sets()
    sets_with_stats = []

    for ts in all_sets:
        df = load_stats_for_turnus_set(ts['id'])
        if df is not None and not df.empty:
            sets_with_stats.append({
                'id': ts['id'],
                'name': ts['name'],
                'year_identifier': ts['year_identifier']
            })

    return sets_with_stats
