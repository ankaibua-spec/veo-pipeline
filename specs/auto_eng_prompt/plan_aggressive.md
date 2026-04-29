# Plan B — AGGRESSIVE: Auto English Lessons

> Triết lý: **Làm cho ra trò.** Tách hẳn module prompt-engine, tab riêng, multi-provider LLM, diversity engine cross-session, preview UI cho phép user edit từng prompt. Ship 3-5 ngày, có thể có breaking change cấu trúc.

---

## 1. Goal

Tạo một subsystem hoàn chỉnh "**English Teaching Auto**" trong app: user vào tab riêng, chọn level + chiến lược, nhập N → app sinh N prompt chất lượng cao, có diversity engine cross-session, có preview, có multi-LLM fallback (Gemini → Groq → OpenRouter → OpenAI). Sau khi user duyệt → 1 click "Send to Render" đẩy vào tab Text→Video.

### In-scope
- Module mới `tool/prompt_engine/` (tách logic prompt-gen ra khỏi `idea_to_video.py`).
- Tab UI mới "📚 English Teaching Auto".
- Pool combo có **weight** (theo trending: ordering_food > library) + anti-repeat **cross-session** (state file).
- Multi-provider LLM: Gemini (default) → Groq (Llama 3.3 70B) → OpenRouter → OpenAI fallback.
- Diversity engine: hash character_lock + background_lock, reject prompt nếu trùng > 70% (cosine sim hoặc Jaccard) với 5 video gần nhất.
- Preview panel: list N prompt sinh ra, mỗi prompt có nút Edit / Regenerate / Delete.
- "Send to Render" → đẩy prompts đã chọn sang tab Text→Video.

### Out-of-scope
- Không gen video tự động (vẫn user click Render manual).
- Không upload YouTube tự động.

---

## 2. File list

### NEW (10 file)

| Path | Mục đích |
|------|----------|
| `tool/prompt_engine/__init__.py` | Package init, expose `PromptEngine` class |
| `tool/prompt_engine/combo.py` | Random combo từ pool, weight-aware, anti-repeat cross-session |
| `tool/prompt_engine/llm_router.py` | Multi-provider router (Gemini/Groq/OpenRouter/OpenAI) |
| `tool/prompt_engine/diversity.py` | Hash + similarity check (Jaccard 3-grams trên character_lock) |
| `tool/prompt_engine/templates.py` | LLM prompt template English teaching A1/A2/B1 |
| `tool/prompt_engine/state.py` | Cross-session state I/O (`data_general/eng_state.json`) |
| `tool/prompt_engine/engine.py` | High-level `PromptEngine.generate_batch(n, level, opts)` |
| `tool/tab_eng_auto.py` | Tab UI mới (bao gồm preview panel) |
| `tool/data_general/eng_lesson_pool.json` | Pool data, có weight |
| `tool/data_general/eng_state.json` | (Auto-tạo runtime) Cross-session memory |

### MODIFIED (3 file)

| Path | Thay đổi |
|------|----------|
| `tool/qt_ui_modern/main_window.py` | Thêm `"eng_auto": ("tab_eng_auto", "EngAutoTab", ())` vào `LEGACY_TABS` + sidebar item |
| `tool/qt_ui_modern/pages.py` | Thêm `EngAutoPage` (host cho `EngAutoTab`) |
| `tool/idea_to_video.py` | (Optional) Refactor: extract `gemini_step_1/2/3` thành adapter cho `PromptEngine`. Giữ wrapper cũ backward-compat. |

**Tổng:** 10 new + 3 modified = 13 file chạm.

---

## 3. Data structures

### `data_general/eng_lesson_pool.json` (weighted)

```json
{
  "version": "2.0",
  "schema": "weighted_pool_v2",
  "levels": {
    "A1": {"label": "Beginner", "vocab": "300-600", "grammar": "present simple, imperatives", "weight": 1.0},
    "A2": {"label": "Elementary", "vocab": "600-1200", "grammar": "past simple, future will", "weight": 1.2},
    "B1": {"label": "Intermediate", "vocab": "1500-2500", "grammar": "perfect tenses, conditionals", "weight": 0.8}
  },
  "topics": [
    {"id": "ordering_food", "label": "Ordering food", "vocab": ["menu","waiter","bill"], "weight": 2.0, "applicable_levels": ["A1","A2","B1"]},
    {"id": "asking_directions", "label": "Asking directions", "vocab": ["block","corner","straight"], "weight": 2.5, "applicable_levels": ["A1","A2"]},
    {"id": "job_interview", "label": "Job interview", "vocab": ["experience","skills","salary"], "weight": 1.5, "applicable_levels": ["A2","B1"]},
    {"id": "library_research", "label": "Library research", "vocab": ["citation","reference","abstract"], "weight": 0.5, "applicable_levels": ["B1"]}
  ],
  "scenarios": [
    {"id": "classroom", "label": "Classroom dialog", "weight": 1.5, "lighting": "natural daylight"},
    {"id": "street", "label": "Street meeting", "weight": 2.0, "lighting": "outdoor mid-day"},
    {"id": "cafe", "label": "Café chat", "weight": 1.8, "lighting": "warm interior"}
  ],
  "character_archetypes": [
    {"id": "teacher_male", "desc_template": "Young male teacher, {age}, {accessory}, {personality}", "age_range": [25,40], "accessories": ["glasses","beard","tie"], "personalities": ["friendly","strict","witty"]}
  ],
  "camera_styles": [
    {"id": "two_shot_eye", "desc": "Medium two-shot, eye-level, soft daylight", "weight": 1.5},
    {"id": "ots_shallow", "desc": "Over-the-shoulder, shallow DOF", "weight": 1.0}
  ],
  "diversity_rules": {
    "min_unique_topics_per_batch": 0.7,
    "min_unique_scenarios_per_batch": 0.6,
    "max_same_archetype_per_batch": 2
  }
}
```

### `data_general/eng_state.json` (cross-session memory)

```json
{
  "version": "1.0",
  "last_updated": "2026-04-29T10:00:00Z",
  "recent_batches": [
    {
      "batch_id": "20260429_100000",
      "timestamp": "2026-04-29T10:00:00Z",
      "n": 10,
      "level": "A2",
      "combos_used": [
        {"key": "A2|ordering_food|cafe|teacher_male|two_shot_eye", "char_hash": "a3f2", "bg_hash": "b1e9"}
      ]
    }
  ],
  "global_combo_count": {"A2|ordering_food|cafe|teacher_male|two_shot_eye": 3},
  "char_hashes_recent": ["a3f2","b1e9","c4d5"],
  "max_recent_batches": 5,
  "max_char_hashes": 50
}
```

### Char hash

```python
def char_hash(character_lock: dict) -> str:
    """Hash deterministic 4-ký-tự từ name+species+age+gender."""
    s = f"{c['name']}|{c['species']}|{c['age']}|{c['gender']}"
    return hashlib.sha1(s.encode()).hexdigest()[:4]
```

### Diversity Jaccard

```python
def jaccard_3gram(s1: str, s2: str) -> float:
    """0..1, 1 = identical."""
    g1 = {s1[i:i+3] for i in range(len(s1)-2)}
    g2 = {s2[i:i+3] for i in range(len(s2)-2)}
    return len(g1 & g2) / max(1, len(g1 | g2))
```

Reject nếu `jaccard_3gram(new_prompt, prev_prompt) > 0.7` so với mỗi prompt trong 5 prompt gần nhất.

---

## 4. UI mockup ASCII

### Sidebar

```
┌─────────────┐
│ 🏠 Home     │
│ ✏️  Text→Vid │
│ 🖼️  Img→Vid  │
│ 💡 Idea→Vid │
│ 📚 Eng Auto │ ◄── MỚI
│ 👤 Character│
│ ⚙️  Settings │
└─────────────┘
```

### Tab "Eng Auto"

```
┌────────────────────── 📚 English Teaching Auto ──────────────────────┐
│                                                                       │
│ ┌─── Config ───────────────────────────────────────────────────────┐ │
│ │ Số bài: [10▼]   Level: [A1▼ ✅A2 ✅B1☐]                          │ │
│ │ Topic filter: [All ▼ Restaurant✅ Travel✅ Office✅ Library☐]    │ │
│ │ LLM: [Gemini ▼ Groq☐ OpenRouter☐ OpenAI☐]  Auto-fallback ✅     │ │
│ │ Diversity: [Strict ●] [Loose ○]                                  │ │
│ │ Cross-session avoid: ✅ (avoid 50 chars from last 5 batches)     │ │
│ │                                                                   │ │
│ │ [🚀 Generate]      [⏹ Stop]      [🗑 Clear preview]              │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ ┌─── Preview (10 prompts) ─────────────────────────────────────────┐ │
│ │ [✅] #1  A2 Ordering Food   [Edit] [Regen] [✕]                   │ │
│ │      "A young waitress greets a tourist couple at a cozy..."     │ │
│ │ ─────────────────────────────────────────────────────────────────│ │
│ │ [✅] #2  A1 Asking Directions [Edit] [Regen] [✕]                 │ │
│ │      "An elderly man points to a map for a confused..."          │ │
│ │ ─────────────────────────────────────────────────────────────────│ │
│ │ [☐] #3  B1 Job Interview    [Edit] [Regen] [✕]                  │ │
│ │      "A nervous young woman in office attire facing..."          │ │
│ │ ...                                                               │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ ┌─── Stats ─────────────────────────────────────────────────────────┐│
│ │ Generated: 10/10  ✅Accepted: 9  ❌Rejected (similarity): 1       ││
│ │ Avg Jaccard with last batch: 0.31                                  ││
│ │ LLM used: Gemini (8) Groq (2)                                     ││
│ └────────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  [📤 Send N selected to Text→Video]   [💾 Export JSON]                │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 5. Algorithm pseudocode

```python
# tool/prompt_engine/engine.py
class PromptEngine:
    def __init__(self):
        self.pool = load_pool()
        self.state = load_state()
        self.llm = LLMRouter()  # multi-provider

    def generate_batch(self, n, level_filter, topic_filter, on_progress):
        results = []
        used_combos: set[str] = set()
        used_char_hashes: set[str] = set(self.state["char_hashes_recent"])
        prev_prompts: list[str] = self._load_recent_prompts()

        attempts = 0
        while len(results) < n and attempts < n * 3:
            attempts += 1

            # 1) Sample combo (weighted, respect filters, avoid used)
            combo = weighted_sample(self.pool, level_filter, topic_filter, used_combos)
            if not combo: break

            # 2) Build idea string
            idea = render_idea_template(combo, self.pool["templates"])

            # 3) Call LLM (Step 1+2+3) via router
            try:
                step1 = self.llm.call_step1(idea, combo)
                ch = char_hash(step1["character_lock"][0])
                if ch in used_char_hashes:
                    on_progress({"reject": "char_hash_collision", "combo": combo})
                    continue
                step2 = self.llm.call_step2(step1, idea, combo)
                step3 = self.llm.call_step3(step1, step2, idea, combo)
            except LLMAllProvidersFailed as e:
                on_progress({"error": str(e)}); break

            prompt_text = step3["prompts"][0]["prompt"]

            # 4) Diversity check
            max_sim = max((jaccard_3gram(prompt_text, p) for p in prev_prompts), default=0.0)
            if max_sim > 0.7:
                on_progress({"reject": "similarity", "score": max_sim, "combo": combo})
                continue

            # 5) Accept
            used_combos.add(combo["key"])
            used_char_hashes.add(ch)
            results.append({
                "combo": combo,
                "char_hash": ch,
                "step1": step1, "step2": step2,
                "prompt": prompt_text,
                "similarity": max_sim,
            })
            prev_prompts.append(prompt_text)
            on_progress({"accept": True, "idx": len(results), "n": n})

        # 6) Update state
        self.state["recent_batches"].append({
            "batch_id": now_iso(), "n": len(results),
            "combos_used": [r["combo"]["key"] for r in results],
        })
        self.state["char_hashes_recent"].extend([r["char_hash"] for r in results])
        trim_state(self.state)
        save_state(self.state)
        return results
```

```python
# tool/prompt_engine/llm_router.py
class LLMRouter:
    PROVIDERS = ["gemini", "groq", "openrouter", "openai"]

    def call_step1(self, idea, combo):
        last_err = None
        for prov in self.PROVIDERS:
            try:
                return self._call(prov, "step1", idea, combo)
            except (QuotaError, AuthError) as e:
                last_err = e; continue
        raise LLMAllProvidersFailed(last_err)
```

```python
# tool/prompt_engine/combo.py
def weighted_sample(pool, level_filter, topic_filter, used):
    eligible = []
    weights = []
    for lv in pool["levels"]:
        if lv not in level_filter: continue
        for tp in pool["topics"]:
            if tp["id"] not in topic_filter: continue
            if lv not in tp["applicable_levels"]: continue
            for sc in pool["scenarios"]:
                for ar in pool["character_archetypes"]:
                    for cm in pool["camera_styles"]:
                        key = f"{lv}|{tp['id']}|{sc['id']}|{ar['id']}|{cm['id']}"
                        if key in used: continue
                        eligible.append((lv, tp, sc, ar, cm, key))
                        weights.append(lv_weight * tp["weight"] * sc["weight"] * cm["weight"])
    if not eligible: return None
    idx = random.choices(range(len(eligible)), weights=weights, k=1)[0]
    lv, tp, sc, ar, cm, key = eligible[idx]
    return materialize_combo(lv, tp, sc, ar, cm, key)  # roll random age/personality
```

---

## 6. LLM prompt template (English teaching)

`prompt_engine/templates.py` — đè/extend Step 1 idea với block sau:

```
ENGLISH-TEACHING SHORT VIDEO BRIEF
==================================
Target learner level: CEFR {level_code} ({level_label})
Vocab budget: {vocab_size} words active
Grammar focus: {grammar_focus}
Real-life topic: {topic_label}
Scenario: {scenario_label}
Lighting hint: {scenario_lighting}

CHARACTER (use as base, expand):
{character_archetype_desc}

CAMERA STYLE: {camera_desc}

CRITICAL DIALOGUE RULES:
- ALL dialogue MUST be in English at level {level_code}.
- Each line ≤ 12 words for A1, ≤ 16 for A2, ≤ 22 for B1.
- Use ONLY grammar structures appropriate for {level_code}.
- Vocabulary: stay within {vocab_size} most common English words +
  these topic-specific terms: {vocab_focus}.
- Pronunciation: avoid silent-letter traps for A1-A2 (no "Worcestershire" etc.)
- Each scene must include 1 "teaching moment" — a key phrase repeated
  with slight variation so learner can absorb pattern.
- Subtitles ready: lines must be self-contained, no half-sentences across cuts.

OUTPUT FORMAT: same JSON schema as base Step 1.
```

Step 2 thêm: yêu cầu mỗi scene `dialogue_text_en` rõ ràng + `key_phrase` được highlight.

Step 3 thêm: closing scene có "Recap card" with key vocab list.

---

## 7. Diversity strategy

**4 lớp bảo vệ:**

| Lớp | Mechanism | Reject khi |
|-----|-----------|-----------|
| 1. Combo key | Hash 5-trục unique trong batch | key collision trong same batch |
| 2. Char hash cross-session | sha1 4-char trên character_lock | hash trùng 1 trong 50 hash gần nhất |
| 3. Jaccard 3-gram prompt | similarity với 5 prompt gần nhất | max_sim > 0.7 |
| 4. Per-batch diversity | min 70% unique topic, max 2 same archetype | rule trong `pool.diversity_rules` |

Retry tối đa `n * 3` lần. Nếu pool cạn → break, warn user.

**State:** lưu vào `data_general/eng_state.json`. Trim sau N=5 batch.

---

## 8. Test plan

| Test | Expected |
|------|----------|
| **Unit:** `weighted_sample` trả về combo theo weight (chạy 1000 lần, mean count khớp distribution) | KS-test p > 0.05 |
| **Unit:** `jaccard_3gram("hello world","hello earth")` ≈ 0.4 | OK |
| **Unit:** `char_hash` deterministic | identical input → identical output |
| **Integration:** N=10, level=A2, no filter | 10 prompt accept rate ≥ 80%, mỗi prompt khác nhau |
| **Integration:** Chạy 5 batch × N=10 = 50 prompt | 0 char_hash collision cross-batch |
| **Integration:** Disable Gemini key → fallback | Groq được dùng, log "fallback to groq" |
| **Integration:** Gen 10 → click Regen prompt #3 | Chỉ prompt #3 đổi, các prompt khác giữ nguyên |
| **Integration:** Click "Send N selected" với 7 prompts ✅ + 3 ☐ | Tab Text→Video append đúng 7 dòng |
| **Visual:** Mở 10 video render từ 10 prompt | Manual check: ≥ 8/10 character/setting khác biệt rõ ràng |
| **Stress:** N=50, no LLM available (offline) | Graceful error, button enable lại |

---

## 9. Risk + mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Refactor `idea_to_video.py` làm vỡ tab Idea→Video cũ | High | High | Adapter pattern: giữ `idea_to_video_workflow()` như facade, internal gọi `PromptEngine`. Test regression tab Idea→Video sau refactor. |
| Multi-provider LLM khó test (Groq/OpenRouter cần key) | High | Med | Mock providers trong unit test. Real test chỉ với Gemini, đánh dấu `@requires_groq_key` để skip. |
| Jaccard 3-gram quá strict / quá loose | Med | Med | Threshold 0.7 là default, expose vào config UI ("Strict/Loose"). |
| State file corrupt giữa session | Low | Med | Try/except load + backup file, schema versioning. |
| UI preview list lag khi N=50 | Low | Low | Lazy render rows, hoặc QListView model-based. |
| User edit prompt rồi Regen → mất edit | Med | Low | Confirm dialog "Bạn đã edit prompt #3, regen sẽ ghi đè. Tiếp tục?". |
| Character archetype template "fill-in-the-blank" sinh prompt awkward | Med | Med | Step 1 LLM tự rewrite, archetype chỉ là gợi ý. |
| Time creep > 5 ngày | High | High | Phase ship: P1 (engine + tab no preview, ngày 1-2), P2 (preview, ngày 3), P3 (multi-LLM, ngày 4-5). |

---

## 10. Time estimate

| Task | Days |
|------|------|
| `prompt_engine/` package skeleton + `combo.py` + `state.py` | 0.5 |
| `llm_router.py` Gemini-only first, then Groq/OpenRouter wrappers | 1.0 |
| `templates.py` English-teaching prompts (3 levels × 3 steps tuned) | 0.8 |
| `diversity.py` Jaccard + char_hash | 0.3 |
| `engine.py` orchestration + retry | 0.5 |
| Refactor `idea_to_video.py` thành adapter (test regression Idea→Video) | 0.7 |
| Tab UI `tab_eng_auto.py` config + preview + actions | 1.5 |
| Sidebar wire + main_window registration | 0.2 |
| Unit tests (combo + diversity + state) | 0.5 |
| Integration test N=10 with real Gemini | 0.5 |
| Polish + Vietnamese log + error handling | 0.5 |
| **TỔNG** | **~7 days. Tight = 5 days nếu skip P3 multi-LLM, fallback dùng chỉ Gemini.** |

---

## 11. Files: new vs modified

- **New:** 10 (engine package + tab + 2 JSON)
- **Modified:** 3 (`main_window`, `pages.py`, `idea_to_video.py` adapter)
- **Lines touched:** ~+1,800 / -200 (refactor)
- **Breaking change:** Internal refactor `idea_to_video.py`. Nếu adapter pattern OK → external API zero breaking.

---

## Tóm tắt 1 câu

> "Build hẳn 1 subsystem prompt-engine + tab riêng + multi-LLM + diversity 4-lớp + preview/edit. Quality cao nhất nhưng risk timeline + regression rủi ro do refactor."
