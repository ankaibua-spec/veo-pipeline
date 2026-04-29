"""eng_auto_prompt.py — Batch English teaching prompt generator.

Wrapper around idea_to_video_workflow() that picks random combos
from eng_lesson_pool.json and produces diverse prompts.

Combo space: 3 levels x 12 topics x 8 scenarios x 8 archetypes x 5 cameras = 11,520.
2-layer dedup: combo key (in-memory, batch only) + char hash from Step1 output.
"""
from __future__ import annotations

import json
import random
import hashlib
import time
from pathlib import Path

from settings_manager import DATA_GENERAL_DIR, WORKFLOWS_DIR, BUNDLE_DIR
from idea_to_video import idea_to_video_workflow


def _resolve_pool_path() -> Path:
    bundled = BUNDLE_DIR / "data_general" / "eng_lesson_pool.json"
    if bundled.exists():
        return bundled
    return DATA_GENERAL_DIR / "eng_lesson_pool.json"


POOL_PATH = _resolve_pool_path()


def load_pool() -> dict:
    """Load pool JSON. Raise if file missing."""
    return json.loads(POOL_PATH.read_text(encoding="utf-8"))


def _hash6(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:6]


def random_combo(
    pool: dict,
    level_filter: list[str],
    topic_filter: str,
    used_keys: set,
    max_try: int = 80,
) -> dict | None:
    """Pick a random combo not yet in used_keys.

    Args:
        pool: Loaded pool dict.
        level_filter: List of level codes e.g. ["A1", "B1"].
        topic_filter: Topic id or "all".
        used_keys: Set of already-used combo key strings (mutated in place).
        max_try: Max random attempts before giving up.

    Returns:
        Dict with keys level/topic/scenario/archetype/camera/key, or None if pool exhausted.
    """
    levels = [lv for lv in pool["levels"] if lv["code"] in level_filter]
    if not levels:
        levels = pool["levels"]  # fallback: all levels

    if topic_filter == "all":
        topics = pool["topics"]
    else:
        topics = [t for t in pool["topics"] if t["id"] == topic_filter]
    if not topics:
        topics = pool["topics"]

    for _ in range(max_try):
        lv = random.choice(levels)
        tp = random.choice(topics)
        sc = random.choice(pool["scenarios"])
        ar = random.choice(pool["character_archetypes"])
        cam_idx = random.randrange(len(pool["camera_styles"]))
        key = f"{lv['code']}|{tp['id']}|{sc['id']}|{ar['id']}|{cam_idx}"
        if key not in used_keys:
            used_keys.add(key)
            return {
                "level": lv,
                "topic": tp,
                "scenario": sc,
                "archetype": ar,
                "camera": pool["camera_styles"][cam_idx],
                "key": key,
            }
    return None  # pool exhausted for given filters


def combo_to_idea(combo: dict) -> str:
    """Build English-teaching idea string to inject into Step 1 prompt.

    This string is passed as the `idea` argument to idea_to_video_workflow().
    Step 1/2/3 LLM templates are NOT modified.
    """
    lv = combo["level"]
    tp = combo["topic"]
    sc = combo["scenario"]
    ar = combo["archetype"]
    return (
        f"English teaching short video for CEFR level {lv['code']} ({lv['label']}). "
        f"REAL-LIFE TOPIC: {tp['label']}. SCENARIO: {sc['label']}, lighting {sc['lighting']}. "
        f"MAIN CHARACTER: {ar['desc']}. CAMERA: {combo['camera']}. "
        f"\n\nLANGUAGE-LEARNING REQUIREMENTS (CRITICAL):\n"
        f"- ALL dialogue MUST be natural English at CEFR {lv['code']}.\n"
        f"- Vocab: {lv['vocab_hint']}. Topic vocab: {', '.join(tp['vocab'])}.\n"
        f"- Grammar focus: {lv['grammar_hint']}.\n"
        f"- Each line must be 16 words or fewer, subtitle-friendly, clearly pronounceable.\n"
        f"- Include 1 teaching moment: a key phrase repeated with slight variation.\n"
        f"- No slang, no idioms beyond level, no real brand names.\n"
        f"- Goal: learner understands and can mimic naturally."
    )


def generate_batch(
    n: int,
    level_filter: list[str],
    topic_filter: str,
    log_callback,
    stop_check,
) -> list[str]:
    """Generate up to N English teaching prompts.

    Args:
        n: Number of lessons to generate.
        level_filter: List of CEFR codes e.g. ["A2", "B1"].
        topic_filter: Topic id or "all".
        log_callback: Callable(str) for progress messages.
        stop_check: Callable() -> bool; return True to abort.

    Returns:
        List of prompt strings (may be fewer than n if skipped/stopped).
    """
    pool = load_pool()
    used_keys: set[str] = set()
    used_char_hashes: set[str] = set()
    prompts_out: list[str] = []
    skipped = 0

    for i in range(n):
        if stop_check and stop_check():
            log_callback(f"Stopped at lesson #{i + 1}")
            break

        combo = random_combo(pool, level_filter, topic_filter, used_keys)
        if combo is None:
            log_callback("Pool exhausted — no more unique combos, stopping early.")
            break

        log_callback(f"#{i + 1} combo: {combo['key']}")
        idea = combo_to_idea(combo)
        project = f"eng_auto_{int(time.time())}_{i:03d}"

        # NOTE: actual signature is idea_to_video_workflow(project_name, idea, ...)
        result = idea_to_video_workflow(
            project_name=project,
            idea=idea,
            scene_count=1,
            style="3d_Pixar",
            language="English (en-US)",
            log_callback=log_callback,
            stop_check=stop_check,
        )

        if not result.get("success"):
            log_callback(f"#{i + 1} FAIL: {result.get('message', 'unknown error')}")
            skipped += 1
            continue

        # Layer 2 dedup: sha1[:6] of Step1 main character fields
        step1_path = WORKFLOWS_DIR / project / "step1_char_file.json"
        try:
            step1 = json.loads(step1_path.read_text(encoding="utf-8"))
            chars = step1.get("character_lock", [])
            if chars:
                c = chars[0]
                ch = _hash6(
                    f"{c.get('name', '')}|{c.get('species', '')}|"
                    f"{c.get('age', '')}|{c.get('gender', '')}"
                )
                if ch in used_char_hashes:
                    log_callback(
                        f"#{i + 1} duplicate character (hash={ch}), "
                        "skipping prompt (pragmatic: no retry)"
                    )
                    skipped += 1
                    continue
                used_char_hashes.add(ch)
        except Exception as e:
            log_callback(f"   (warn: cannot read step1: {e})")

        # Collect prompts from result
        for p in result.get("prompts", []):
            text = p.get("prompt", "").strip() if isinstance(p, dict) else str(p).strip()
            if text:
                prompts_out.append(text)

        log_callback(f"#{i + 1} OK ({len(result.get('prompts', []))} prompts)")

    log_callback(
        f"Done: {len(prompts_out)} prompts generated, {skipped} skipped."
    )
    return prompts_out
