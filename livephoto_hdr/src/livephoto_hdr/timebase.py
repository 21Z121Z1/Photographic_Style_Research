"""Exact rational presentation-time mapping."""
from __future__ import annotations

from fractions import Fraction


def rational(value: int, scale: int) -> Fraction:
    if scale <= 0:
        raise ValueError(f"timescale must be positive, got {scale}")
    return Fraction(int(value), int(scale))


def alpha(time: Fraction, left: Fraction, right: Fraction) -> Fraction:
    if right < left:
        raise ValueError("right timestamp precedes left")
    if left == right:
        return Fraction(0)
    if time < left or time > right:
        raise ValueError("time is outside the bracket")
    return Fraction(time - left, right - left)


def expand_deltas(entries: list[tuple[int, int]]) -> list[int]:
    times: list[int] = []
    cursor = 0
    for count, delta in entries:
        if count < 0 or delta < 0:
            raise ValueError("sample counts and deltas must be non-negative")
        for _ in range(count):
            times.append(cursor)
            cursor += delta
    return times


def composition_times(decode_times: list[int], offsets: list[int]) -> list[int]:
    if len(decode_times) != len(offsets):
        raise ValueError("ctts and stts sample counts differ")
    return [decode + offset for decode, offset in zip(decode_times, offsets)]


def edit_presentation(media_pts: int, edits: list[tuple[int, int]], media_scale: int, movie_scale: int) -> Fraction | None:
    """Map one media timestamp through an edit list.

    Durations are in movie timescale. media_time is in media timescale.
    media_time < 0 is an empty edit. Returns None when the sample is outside
    every media edit.
    """
    if media_scale <= 0 or movie_scale <= 0:
        raise ValueError("timescales must be positive")
    presentation = 0
    for duration, media_time in edits:
        if duration < 0:
            raise ValueError("edit duration must be non-negative")
        if media_time < 0:
            presentation += duration
            continue
        delta_media = media_pts - media_time
        if delta_media < 0:
            presentation += duration
            continue
        delta_movie = Fraction(delta_media, media_scale) * movie_scale
        if delta_movie < duration:
            return Fraction(presentation, movie_scale) + Fraction(delta_media, media_scale)
        presentation += duration
    return None


def bracket(times: list[Fraction], time: Fraction) -> dict:
    """Classify one main-frame time against sorted thumbnail times."""
    if not times:
        raise ValueError("no thumbnail times")
    if any(later < earlier for earlier, later in zip(times, times[1:])):
        raise ValueError("thumbnail times must be sorted")
    lower = [stamp for stamp in times if stamp <= time]
    upper = [stamp for stamp in times if stamp >= time]
    if lower and upper:
        left = lower[-1]
        right = upper[0]
        policy = "exact" if left == right else "interpolation"
    elif lower:
        left = right = lower[-1]
        policy = "one_sided_tail"
    else:
        left = right = upper[0]
        policy = "one_sided_head"
    positive = [later - earlier for earlier, later in zip(times, times[1:]) if later > earlier]
    median = _median_fraction(positive) if positive else Fraction(0)
    gap = right - left
    long_gap = bool(positive) and policy == "interpolation" and gap > 2 * median
    return {
        "policy": policy,
        "left": left,
        "right": right,
        "alpha": alpha(time, left, right),
        "gap": gap,
        "medianInterval": median,
        "longGap": long_gap,
    }


def _median_fraction(values: list[Fraction]) -> Fraction:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
