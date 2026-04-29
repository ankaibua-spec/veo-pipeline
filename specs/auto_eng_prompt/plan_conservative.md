# Plan A — CONSERVATIVE: Auto English Lessons

> Triết lý: **Đụng ít nhất có thể.** Reuse 100% pipeline 3-step có sẵn, chỉ thêm 1 nút và 1 module combo. Backward-compat tuyệt đối — user cũ mở app vẫn thấy y nguyên.

---

## 1. Goal

User nhập số N → app tự sinh N prompt khác nhau (English teaching, level A1–B1) → ghi vào `PromptEditor` của tab Text→Video → user bấm Render hiện tại.

### In-scope
- Random combo từ JSON pool (level × topic × scenario × character × camera).
- Mỗi combo → gọi `gemini_step_1 + 2 + 3` y nguyên với combo lắp thành 1 chuỗi `idea` (string).
- Append text vào `PromptEditor` qua `editor.appendPlainText(...)`.
- Anti-repeat trong batch hiện tại (in-memory set).

### Out-of-scope
- KHÔNG refactor `idea_to_video.py`.
- KHÔNG thêm tab mới.
- KHÔNG đổi UI tab Idea→Video.
- KHÔNG state file cross-session.
- KHÔNG multi-provider LLM (chỉ Gemini).
- KHÔNG preview / edit prompt trước khi render.

---

## 2. File list

### NEW (3 file)
| Path | Mục đích |
|------|----------|
| `tool/eng_lesson_combo.py` | Module random combo + dedupe in-memory. ~120 dòng. |
| `tool/data_general/eng_lesson_pool.json` | Pool data (level/topic/scenario/character/camera). |
| `specs/auto_eng_prompt/plan_conservative.md` | File này. |

### MODIFIED (1 file)
| Path | Thay đổi |
|------|----------|
| `tool/tab_text_to_video.py` | Thêm 1 hàng button row trên đỉnh tab: `[N: ___] [Auto Generate English Lessons]`. Click → background QThread chạy loop, append từng prompt vào editor. ~+80 dòng, không động `PromptEditor`. |

**Tổng:** 3 new + 1 modified = 4 file chạm.

---

## 3. Data structure

### `data_general/eng_lesson_pool.json`

```json
{
  "version": "1.0",
  "levels": [
    {"code": "A1", "label": "Beginner", "vocab_size": "300-600", "grammar": "present simple, basic to be"},
    {"code": "A2", "label": "Elementary", "vocab_size": "600-1200", "grammar": "past simple, present continuous"},
    {"code": "B1", "label": "Intermediate", "vocab_size": "1500-2500", "grammar": "present perfect, conditionals"}
  ],
  "topics": [
    {"id": "ordering_food", "label": "Ordering food at restaurant", "vocab_focus": ["menu", "waiter", "bill", "order"]},
    {"id": "asking_directions", "label": "Asking for directions", "vocab_focus": ["turn left", "straight", "block", "corner"]},
    {"id": "shopping_clothes", "label": "Shopping for clothes", "vocab_focus": ["size", "fit", "try on", "discount"]},
    {"id": "job_interview", "label": "Job interview basics", "vocab_focus": ["experience", "skills", "salary", "position"]},
    {"id": "travel_airport", "label": "At the airport", "vocab_focus": ["boarding pass", "gate", "luggage", "delay"]},
    {"id": "doctor_visit", "label": "Visiting the doctor", "vocab_focus": ["symptoms", "prescription", "appointment", "feel"]},
    {"id": "phone_call", "label": "Phone conversation", "vocab_focus": ["leave message", "hold on", "call back", "speak to"]},
    {"id": "weather_smalltalk", "label": "Weather small talk", "vocab_focus": ["forecast", "humid", "freezing", "drizzle"]},
    {"id": "hotel_checkin", "label": "Hotel check-in", "vocab_focus": ["reservation", "key card", "wi-fi", "check-out"]},
    {"id": "describing_people", "label": "Describing appearance", "vocab_focus": ["tall", "curly", "wearing", "looks like"]},
    {"id": "daily_routine", "label": "Daily routine", "vocab_focus": ["wake up", "commute", "lunch break", "go to bed"]},
    {"id": "asking_help", "label": "Asking for help politely", "vocab_focus": ["could you", "would you mind", "excuse me"]}
  ],
  "scenarios": [
    {"id": "classroom", "label": "Classroom dialog teacher–student"},
    {"id": "street", "label": "Two strangers meeting on street"},
    {"id": "office", "label": "Office co-workers chat"},
    {"id": "cafe", "label": "Friends at café"},
    {"id": "phone", "label": "Phone call between two people"},
    {"id": "shop", "label": "Customer and shopkeeper"},
    {"id": "park", "label": "Two friends jogging at park"},
    {"id": "library", "label": "Quiet library dialog whisper"}
  ],
  "characters": [
    {"id": "young_male_teacher", "desc": "Young male teacher, 28, glasses, friendly"},
    {"id": "elderly_female_shopkeeper", "desc": "Elderly female shopkeeper, 60, warm smile"},
    {"id": "teen_student_girl", "desc": "Teenage student girl, 16, ponytail, curious"},
    {"id": "businessman_30s", "desc": "Businessman, 35, suit, in a hurry"},
    {"id": "tourist_couple", "desc": "Tourist couple, mid 20s, backpacks"},
    {"id": "cafe_barista", "desc": "Café barista, 24, apron, cheerful"},
    {"id": "doctor_female", "desc": "Female doctor, 40, white coat, calm"},
    {"id": "child_8yo", "desc": "Child, 8, hoodie, energetic"}
  ],
  "camera_styles": [
    "Medium two-shot, eye-level, soft daylight",
    "Over-the-shoulder cuts, shallow depth of field",
    "Static wide shot, warm interior light",
    "Handheld walk-and-talk, natural light",
    "Close-up on speaker, tight framing, cinematic"
  ]
}
```

### Combo hash (anti-repeat)

```python
hash_key = f"{level}|{topic}|{scenario}|{char_id}|{camera_idx}"
```

5 trục × 3×12×8×8×5 = **11,520 combos** → đủ cho N=10..50 không trùng.

---

## 4. UI mockup ASCII

```
┌─────────────────── Tab "Text → Video" ────────────────────┐
│ [Số bài: 10▼]  [📚 Auto English Lessons]  ──────────────  │  ← row mới (40px)
├───────────────────────────────────────────────────────────┤
│ Nhập prompt (mỗi dòng là 1 prompt)                        │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ 1│ A young male teacher and a teenage student in...   │ │  ← editor cũ
│ │ 2│ A businessman talking to barista at a cafe...      │ │     append
│ │ 3│ Tourist couple asking shopkeeper for directions... │ │     vào đây
│ │  │                                                    │ │
│ └───────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

Button click flow:
1. Disable button, show "⏳ Đang sinh 10 bài học…"
2. Mỗi prompt sinh xong → append 1 dòng → editor scroll xuống.
3. Xong N → enable button, show "✅ Đã sinh 10 bài học (10 prompts)".

---

## 5. Algorithm pseudocode

```python
# tool/eng_lesson_combo.py
def random_combo(pool: dict, used: set[str]) -> dict:
    """Random 1 combo chưa nằm trong used. Tối đa 50 retry."""
    for _ in range(50):
        lv  = random.choice(pool["levels"])
        tp  = random.choice(pool["topics"])
        sc  = random.choice(pool["scenarios"])
        ch  = random.choice(pool["characters"])
        cam = random.randrange(len(pool["camera_styles"]))
        key = f"{lv['code']}|{tp['id']}|{sc['id']}|{ch['id']}|{cam}"
        if key not in used:
            used.add(key)
            return {"level": lv, "topic": tp, "scenario": sc,
                    "character": ch, "camera": pool["camera_styles"][cam], "key": key}
    return None  # cực hiếm

def combo_to_idea(combo: dict) -> str:
    """Lắp combo thành chuỗi idea cho gemini_step_1."""
    return (
        f"English teaching short video, level {combo['level']['code']} "
        f"({combo['level']['label']}). Topic: {combo['topic']['label']}. "
        f"Scenario: {combo['scenario']['label']}. "
        f"Main character: {combo['character']['desc']}. "
        f"Camera: {combo['camera']}. "
        f"Grammar focus: {combo['level']['grammar']}. "
        f"Key vocab: {', '.join(combo['topic']['vocab_focus'])}. "
        f"Goal: teach learners through natural dialogue, "
        f"each line clear and pronounceable, subtitles ready."
    )
```

```python
# tool/tab_text_to_video.py — extend
def _on_auto_generate_clicked(self):
    n = int(self.spin_count.value())
    self.btn_auto.setEnabled(False)
    self.worker = AutoEngWorker(n)
    self.worker.prompt_ready.connect(self._append_prompt)
    self.worker.finished.connect(lambda: self.btn_auto.setEnabled(True))
    self.worker.start()

class AutoEngWorker(QThread):
    prompt_ready = pyqtSignal(str)
    def run(self):
        from eng_lesson_combo import load_pool, random_combo, combo_to_idea
        from idea_to_video import idea_to_video_workflow
        pool = load_pool()
        used = set()
        for i in range(self.n):
            combo = random_combo(pool, used)
            idea = combo_to_idea(combo)
            project = f"eng_auto_{int(time.time())}_{i:03d}"
            result = idea_to_video_workflow(
                idea=idea, scene_count=1, style="3d_Pixar",
                language="English (en-US)", project_name=project
            )
            if result.get("success"):
                for p in result["prompts"]:
                    self.prompt_ready.emit(p["prompt"])
```

`scene_count=1` vì mỗi prompt = 1 video độc lập. Reuse `idea_to_video_workflow` nguyên xi.

---

## 6. LLM prompt template

Reuse 100% Step 1/2/3 hiện tại. Chỉ thay đổi `idea` đầu vào (string `combo_to_idea`).

Step 1 sẽ tự sinh `character_lock` + `background_lock` từ idea này. Vì idea đã chứa "English teaching" + level + topic + character desc → Step 1 prompt hiện tại đủ sức bao quát.

**Nếu** cần tinh chỉnh, đính thêm 1 đoạn sau idea (optional, NOT in this conservative scope):

```
LANGUAGE LEARNING REQUIREMENTS:
- Dialogue MUST be in English at level {level_code}.
- Sentences ≤ 12 words, vocabulary from CEFR {level_code} list.
- Use grammar: {grammar_focus}.
- Pronunciation: each line subtitle-friendly, no slang.
```

→ Gắn vào `combo_to_idea()`. Nếu Conservative thì để mặc định, không can thiệp Step 1/2/3 prompt template.

---

## 7. Diversity strategy

**1 lớp duy nhất:** in-memory `used: set[str]` cho mỗi batch.

Hash 5 trục đảm bảo: cùng level cùng topic nhưng khác scenario/character/camera vẫn được tính khác. Pool 11,520 → xác suất N=10 trùng = 0.

**KHÔNG có:**
- Cross-session anti-repeat (next batch có thể trùng batch trước).
- Hash character_lock từ Step 1 output (không validate).
- Reject prompt nếu Step 3 output trùng cũ.

→ Điểm yếu: nếu user spam liên tục 5 batch × 10 = 50 prompt, có thể trùng combo cũ. Chấp nhận đổi lấy đơn giản.

---

## 8. Test plan

| Test | Expected |
|------|----------|
| Click button N=1 | Editor +1 dòng, button enable lại sau ~30s |
| Click button N=10 | Editor +10 dòng, mỗi dòng khác nhau (manual eyeball check) |
| Click 2 lần liên tiếp N=5+5 | 10 combo trong batch 1 unique, batch 2 unique nội bộ (có thể trùng batch 1 — chấp nhận) |
| Mất Gemini key | Lỗi popup, button enable lại |
| Stop giữa chừng (Ctrl+C / close tab) | QThread `.requestInterruption()` → stop_check trong gemini_* dừng |
| N=10, mở 10 prompt random vào VEO/Sora | 10 video phải khác character + setting (manual review 3/10) |

**Sanity check thủ công sau khi ship:**
- Chạy N=20 → mở `data_general/eng_lesson_pool.json` đếm: ≥15 unique level/topic/scenario combo.

---

## 9. Risk + mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Gemini quota cạn giữa batch | Med | Med | `idea_to_video_workflow` đã có rotate key — kế thừa. |
| Step 1 output không liên quan English teaching (vì idea quá generic) | Med | High | combo_to_idea bơm thẳng "English teaching short video, level X" vào câu đầu — Gemini đủ thông minh. Nếu test fail → escalate sang Pragmatic plan. |
| 11k combo nhưng character/scenario lặp lại visual giống nhau | Low | Low | Step 1 sinh `signature_feature` ngẫu nhiên → đủ phân biệt. |
| User nhấn button khi đang chạy → spawn nhiều thread | Low | Med | Disable button khi worker chạy. |
| Editor kẹt lag khi append 50 dòng | Low | Low | `appendPlainText` đã tối ưu, không vấn đề. |

---

## 10. Time estimate

| Task | Hours |
|------|-------|
| Viết `eng_lesson_pool.json` (12 topic × 8 scenario × 8 char) | 1.5 |
| Viết `eng_lesson_combo.py` (load+random+hash) | 0.5 |
| Sửa `tab_text_to_video.py` thêm row + worker | 1.5 |
| Test N=1, N=10, N=stop | 1.0 |
| Polish + log message tiếng Việt | 0.5 |
| **TỔNG** | **~5h, ship trong 1 ngày** |

---

## 11. Files: new vs modified

- **New:** 3 (combo module + JSON pool + spec)
- **Modified:** 1 (`tab_text_to_video.py`)
- **Lines touched:** ~+220 / -0
- **Breaking change:** None

---

## Tóm tắt 1 câu

> "Reuse `idea_to_video_workflow` nguyên xi, chỉ thêm 1 button + 1 combo randomizer. Ship trong 1 ngày, zero risk cho user cũ."
