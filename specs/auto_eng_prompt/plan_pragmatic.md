# Plan C — PRAGMATIC: Auto English Lessons

> Triết lý: **Ship trong 1 ngày, đủ tốt cho 90% case.** Reuse `idea_to_video_workflow()` không refactor, thêm 1 tab nhỏ riêng (không nhồi vào Text→Video tránh ô nhiễm UI), in-memory dedupe, single-provider Gemini, output append vào tab Text→Video qua signal Qt.

---

## 1. Goal

User mở tab "📚 Auto English Lessons" → chọn level + topic + N → click Generate → app sinh N prompt → append vào tab Text→Video → user bấm Render hiện tại.

### In-scope
- Tab UI mới riêng (panel nhỏ, ~200px height nội dung).
- Wrapper `tool/eng_auto_prompt.py` gọi `idea_to_video_workflow()` y nguyên.
- Pool combo JSON: 5 trục (level × topic × scenario × character_archetype × camera).
- Anti-repeat in-memory cho batch hiện tại (set hash combo + char_lock từ Step 1 output).
- Single Gemini với rotate key (kế thừa từ `idea_to_video.py`).
- Append output vào `PromptEditor` của tab Text→Video qua signal hoặc shared reference.
- English-teaching prompt template **bơm vào idea string** (không sửa Step 1/2/3 LLM template gốc).

### Out-of-scope
- KHÔNG refactor `idea_to_video.py`.
- KHÔNG multi-provider LLM.
- KHÔNG cross-session state.
- KHÔNG preview/edit UI.
- KHÔNG Jaccard similarity (chỉ hash dedupe).

### Bonus (nếu tiện)
- Fix bug nếu thấy trên đường đi (ví dụ stop_check chưa bind đúng).

---

## 2. File list

### NEW (4 file)

| Path | Mục đích |
|------|----------|
| `tool/eng_auto_prompt.py` | Wrapper sinh batch English lessons. ~200 dòng. |
| `tool/tab_eng_auto.py` | Tab UI nhỏ (config row + run button + log box). ~250 dòng. |
| `tool/data_general/eng_lesson_pool.json` | Pool data (5 trục, không weight). |
| `specs/auto_eng_prompt/plan_pragmatic.md` | File này. |

### MODIFIED (3 file)

| Path | Thay đổi |
|------|----------|
| `tool/qt_ui_modern/main_window.py` | +1 dòng vào `LEGACY_TABS`: `"eng_auto": ("tab_eng_auto", "EngAutoTab", ())` + 1 nav item sidebar |
| `tool/qt_ui_modern/pages.py` | +`EngAutoPage` host (~25 dòng, copy mẫu từ `Idea2VideoPage`) |
| `tool/tab_text_to_video.py` | +1 method `append_prompts(list[str])` để tab khác push prompt vào (~10 dòng) |

**Tổng:** 4 new + 3 modified = 7 file chạm.

---

## 3. Data structures

### `data_general/eng_lesson_pool.json`

```json
{
  "version": "1.0",
  "levels": [
    {"code": "A1", "label": "Beginner", "vocab_hint": "300-600 most common words",
     "grammar_hint": "present simple, basic to-be, imperatives"},
    {"code": "A2", "label": "Elementary", "vocab_hint": "600-1200 words",
     "grammar_hint": "past simple, present continuous, future will"},
    {"code": "B1", "label": "Intermediate", "vocab_hint": "1500-2500 words",
     "grammar_hint": "present perfect, conditionals, modals"}
  ],
  "topics": [
    {"id":"food","label":"Ordering food","vocab":["menu","waiter","bill","ordering","main course"]},
    {"id":"directions","label":"Asking directions","vocab":["turn left","straight","block","corner"]},
    {"id":"shopping","label":"Shopping for clothes","vocab":["size","fit","try on","discount","cashier"]},
    {"id":"interview","label":"Job interview","vocab":["experience","skills","salary","position","resume"]},
    {"id":"airport","label":"At the airport","vocab":["boarding pass","gate","luggage","delay"]},
    {"id":"doctor","label":"Doctor visit","vocab":["symptoms","prescription","appointment","feel"]},
    {"id":"phone","label":"Phone conversation","vocab":["leave message","hold on","call back"]},
    {"id":"weather","label":"Weather small talk","vocab":["forecast","humid","freezing","drizzle"]},
    {"id":"hotel","label":"Hotel check-in","vocab":["reservation","key card","wi-fi","check-out"]},
    {"id":"appearance","label":"Describing appearance","vocab":["tall","curly","wearing","looks like"]},
    {"id":"routine","label":"Daily routine","vocab":["wake up","commute","lunch break","go to bed"]},
    {"id":"help","label":"Asking help politely","vocab":["could you","would you mind","excuse me"]}
  ],
  "scenarios": [
    {"id":"classroom","label":"Classroom dialog teacher–student","lighting":"natural daylight"},
    {"id":"street","label":"Two strangers on street","lighting":"outdoor mid-day"},
    {"id":"office","label":"Office co-workers chat","lighting":"fluorescent indoor"},
    {"id":"cafe","label":"Friends at café","lighting":"warm interior"},
    {"id":"phone_setup","label":"Phone call split-screen","lighting":"two locations"},
    {"id":"shop","label":"Customer and shopkeeper","lighting":"shop interior"},
    {"id":"park","label":"Park bench dialog","lighting":"golden hour"},
    {"id":"library","label":"Library whisper dialog","lighting":"soft warm"}
  ],
  "character_archetypes": [
    {"id":"young_male_teacher","desc":"Young male English teacher, 28, glasses, friendly tone"},
    {"id":"elderly_female_shop","desc":"Elderly female shopkeeper, 62, warm smile, apron"},
    {"id":"teen_student_girl","desc":"Teenage student girl, 16, ponytail, curious eyes"},
    {"id":"businessman_30s","desc":"Businessman, 35, suit, slightly hurried"},
    {"id":"tourist_couple","desc":"Tourist couple, mid-20s, backpacks, holding map"},
    {"id":"barista_24","desc":"Café barista, 24, apron, cheerful tone"},
    {"id":"doctor_female","desc":"Female doctor, 40, white coat, calm voice"},
    {"id":"child_8yo","desc":"Child, 8, hoodie, energetic and inquisitive"}
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

**Combo space:** 3 × 12 × 8 × 8 × 5 = **11,520 unique combos.**

### Combo hash (in-memory, batch only)

```python
combo_key = f"{level}|{topic_id}|{scenario_id}|{archetype_id}|{camera_idx}"
char_lock_hash = sha1(f"{name}|{species}|{age}|{gender}").hexdigest()[:6]
```

**State:** `self._used_keys: set[str]`, `self._used_char_hashes: set[str]` reset mỗi batch.

---

## 4. UI mockup ASCII

### Sidebar

```
🏠 Home
✏️  Text → Video
🖼️  Image → Video
💡 Idea → Video
📚 Auto English ◄── MỚI
👤 Character
⚙️  Settings
```

### Tab "Auto English Lessons"

```
┌──────────────── 📚 Auto English Lessons ─────────────────┐
│                                                           │
│ Level:       [A1 ▼ A2 ✅ B1 ✅]   (multi-select)         │
│ Topic:       [Tất cả ▼]   (single dropdown, "Tất cả" =   │
│              random tất, hoặc chọn 1 topic cố định)      │
│ Số bài:      [10 ▼]  (1..50)                             │
│                                                           │
│ [🚀 Generate]    [⏹ Stop]    [🗑 Clear log]              │
│                                                           │
│ ┌─── Log ───────────────────────────────────────────────┐│
│ │ [10:00:01] 🎯 Bắt đầu sinh 10 bài, level=A2,B1        ││
│ │ [10:00:03] ⏳ #1 combo: A2|food|cafe|barista_24|0     ││
│ │ [10:00:18] ✅ #1 prompt: "A young café barista..."     ││
│ │ [10:00:19] 📤 Đã append vào tab Text→Video             ││
│ │ [10:00:22] ⏳ #2 combo: B1|interview|office|...        ││
│ │ [10:00:38] ✅ #2 prompt: "A nervous candidate..."      ││
│ │ ...                                                     ││
│ │ [10:04:55] 🎉 Hoàn thành 10/10 bài.                   ││
│ └────────────────────────────────────────────────────────┘│
│                                                           │
│ ℹ️ Prompts đã được thêm vào tab "Text → Video".          │
│    Mở tab đó và bấm Render để gen video.                 │
└───────────────────────────────────────────────────────────┘
```

---

## 5. Algorithm pseudocode

```python
# tool/eng_auto_prompt.py
import json, random, hashlib, time
from pathlib import Path
from settings_manager import DATA_GENERAL_DIR, WORKFLOWS_DIR
from idea_to_video import idea_to_video_workflow

POOL_PATH = DATA_GENERAL_DIR / "eng_lesson_pool.json"

def load_pool() -> dict:
    return json.loads(POOL_PATH.read_text(encoding="utf-8"))

def _hash6(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:6]

def random_combo(pool, level_filter, topic_filter, used_keys, max_try=80):
    """Random 1 combo chưa nằm trong used_keys."""
    levels = [lv for lv in pool["levels"] if lv["code"] in level_filter]
    topics = pool["topics"] if topic_filter == "all" else \
             [t for t in pool["topics"] if t["id"] == topic_filter]
    for _ in range(max_try):
        lv  = random.choice(levels)
        tp  = random.choice(topics)
        sc  = random.choice(pool["scenarios"])
        ar  = random.choice(pool["character_archetypes"])
        cam = random.randrange(len(pool["camera_styles"]))
        key = f"{lv['code']}|{tp['id']}|{sc['id']}|{ar['id']}|{cam}"
        if key not in used_keys:
            used_keys.add(key)
            return {
                "level": lv, "topic": tp, "scenario": sc,
                "archetype": ar, "camera": pool["camera_styles"][cam],
                "key": key,
            }
    return None  # pool cạn

def combo_to_idea(combo: dict) -> str:
    """Build idea string ENG-teaching, bơm vào gemini_step_1."""
    lv = combo["level"]; tp = combo["topic"]
    sc = combo["scenario"]; ar = combo["archetype"]
    return (
        f"English teaching short video for CEFR level {lv['code']} ({lv['label']}). "
        f"REAL-LIFE TOPIC: {tp['label']}. SCENARIO: {sc['label']}, lighting {sc['lighting']}. "
        f"MAIN CHARACTER: {ar['desc']}. CAMERA: {combo['camera']}. "
        f"\n\nLANGUAGE-LEARNING REQUIREMENTS (CRITICAL):\n"
        f"- ALL dialogue MUST be natural English at CEFR {lv['code']}.\n"
        f"- Vocab: {lv['vocab_hint']}. Topic vocab: {', '.join(tp['vocab'])}.\n"
        f"- Grammar focus: {lv['grammar_hint']}.\n"
        f"- Each line ≤ 16 words, subtitle-friendly, clearly pronounceable.\n"
        f"- Include 1 'teaching moment': a key phrase repeated with slight variation.\n"
        f"- No slang, no idioms beyond level, no real brand names.\n"
        f"- Goal: learner understands and can mimic naturally."
    )

def generate_batch(n, level_filter, topic_filter, log_callback, stop_check):
    pool = load_pool()
    used_keys: set[str] = set()
    used_char_hashes: set[str] = set()
    prompts_out: list[str] = []
    skipped = 0

    for i in range(n):
        if stop_check and stop_check():
            log_callback(f"⏹ Đã dừng tại bài #{i+1}")
            break

        combo = random_combo(pool, level_filter, topic_filter, used_keys)
        if combo is None:
            log_callback("⚠️ Pool cạn combo unique, dừng sớm.")
            break

        log_callback(f"⏳ #{i+1} combo: {combo['key']}")
        idea = combo_to_idea(combo)
        project = f"eng_auto_{int(time.time())}_{i:03d}"

        result = idea_to_video_workflow(
            idea=idea,
            scene_count=1,
            style="3d_Pixar",
            language="English (en-US)",
            project_name=project,
            log_callback=log_callback,
            stop_check=stop_check,
        )
        if not result.get("success"):
            log_callback(f"❌ #{i+1} fail: {result.get('message')}")
            skipped += 1
            continue

        # Char-hash dedupe (đọc step1_char_file.json từ project_dir)
        step1_path = WORKFLOWS_DIR / project / "step1_char_file.json"
        try:
            step1 = json.loads(step1_path.read_text(encoding="utf-8"))
            chars = step1.get("character_lock", [])
            if chars:
                c = chars[0]
                ch = _hash6(f"{c.get('name','')}|{c.get('species','')}|{c.get('age','')}|{c.get('gender','')}")
                if ch in used_char_hashes:
                    log_callback(f"⚠️ #{i+1} char trùng (hash={ch}), skip prompt này, retry không thực hiện (giữ pragmatic)")
                    skipped += 1
                    continue
                used_char_hashes.add(ch)
        except Exception as e:
            log_callback(f"   (warn: không đọc được step1: {e})")

        # Lấy prompts từ result
        for p in result.get("prompts", []):
            prompts_out.append(p["prompt"])

        log_callback(f"✅ #{i+1} OK ({len(result.get('prompts', []))} prompts)")

    log_callback(f"🎉 Hoàn thành: {len(prompts_out)} prompts, skip {skipped}")
    return prompts_out
```

```python
# tool/tab_eng_auto.py — UI skeleton
class _Worker(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal(list)  # list[str]
    def __init__(self, n, levels, topic):
        super().__init__()
        self._n, self._lv, self._tp = n, levels, topic
        self._stop = False
    def stop(self): self._stop = True
    def run(self):
        from eng_auto_prompt import generate_batch
        prompts = generate_batch(
            n=self._n, level_filter=self._lv, topic_filter=self._tp,
            log_callback=lambda m: self.log.emit(m),
            stop_check=lambda: self._stop,
        )
        self.done.emit(prompts)

class EngAutoTab(QWidget):
    # ... combo widgets, log box, btn Generate
    def _on_generate(self):
        n = int(self.spin_n.value())
        levels = [code for code, cb in self.level_checks.items() if cb.isChecked()]
        topic = self.topic_combo.currentData() or "all"
        self.btn_run.setEnabled(False)
        self.worker = _Worker(n, levels, topic)
        self.worker.log.connect(self._append_log)
        self.worker.done.connect(self._on_batch_done)
        self.worker.start()
    def _on_batch_done(self, prompts: list[str]):
        # Tìm tab Text→Video qua main_window registry hoặc signal bus
        from qt_ui_modern.main_window import push_to_text_to_video
        push_to_text_to_video(prompts)
        self._append_log(f"📤 Đã append {len(prompts)} prompts vào tab Text→Video.")
        self.btn_run.setEnabled(True)
```

```python
# tool/tab_text_to_video.py — thêm method
class TextToVideoTab(QWidget):
    def append_prompts(self, prompts: list[str]):
        """Append từ tab khác (Eng Auto). Mỗi prompt 1 dòng."""
        if not prompts: return
        cur = self.editor.toPlainText() or ""
        if cur and not cur.endswith("\n"):
            cur += "\n"
        cur += "\n".join(p.strip() for p in prompts if p.strip()) + "\n"
        self.editor.setPlainText(cur)
        # Move cursor to end
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.editor.setTextCursor(cursor)
```

```python
# tool/qt_ui_modern/main_window.py — +helper
def push_to_text_to_video(prompts: list[str]):
    """Tìm TextToVideoTab instance đang sống và append."""
    app = QApplication.instance()
    for w in app.allWidgets():
        if w.__class__.__name__ == "TextToVideoTab":
            try: w.append_prompts(prompts); return True
            except Exception: pass
    return False
```

---

## 6. LLM prompt template (English teaching)

Reuse Step 1/2/3 nguyên xi. **KHÔNG sửa template LLM.**

`combo_to_idea()` đã bơm "ENG-teaching" + level + grammar + vocab hint vào idea string. Step 1 prompt hiện tại (`gemini_step_1`) ở `idea_to_video.py:332` dùng `{script}` placeholder → toàn bộ idea string này được nhúng → Gemini sinh character + background phù hợp.

Step 2 sẽ tự sinh dialogue tiếng Anh vì `language="English (en-US)"` truyền vào.

Step 3 format prompt detail.

→ Zero rủi ro chạm Step 1/2/3 prompt template gốc, không break tab Idea→Video.

---

## 7. Diversity strategy

**2 lớp, in-memory only:**

| Lớp | Mechanism | Reject |
|-----|-----------|--------|
| 1. Combo key | Hash 5-trục (level\|topic\|scenario\|archetype\|cam) | Trùng trong batch hiện tại |
| 2. Char hash | sha1[:6] trên `name+species+age+gender` từ Step 1 output | Trùng trong batch hiện tại |

Lớp 2 chỉ reject (skip), KHÔNG retry (giữ pragmatic, đỡ chi phí Gemini). Nếu skip nhiều thì user chỉ cần tăng N.

**Cross-session:** không có. Batch sau có thể trùng batch trước. Khi user phàn nàn → upgrade lên Aggressive plan sau.

Pool 11,520 → N=10 trong batch: xác suất trùng combo key ≈ 0. Char hash collision phụ thuộc Gemini sinh nhân vật giống nhau cho 2 archetype khác → khả năng thấp.

---

## 8. Test plan

| Test | Expected |
|------|----------|
| Click Generate N=1 | Log có "🎉 Hoàn thành: 1 prompts", tab Text→Video có +1 dòng |
| Click Generate N=10 | 10 dòng append, mỗi dòng khác nhau (manual eyeball 5/10) |
| Click Stop giữa chừng | Log "⏹ Đã dừng tại bài #X", button Run enable lại |
| Pool cạn (force test: levels=A1, topic=interview, scenario chỉ 1) | Log "Pool cạn combo unique" rồi dừng |
| Mất Gemini key | Log fail per prompt, tổng kết "skip N", button enable lại |
| Char hash collision (force: chạy 20 lần, hy vọng 1-2 case collision) | Log "char trùng, skip", tổng prompts < 20 |
| Open tab Text→Video sau Generate | Editor có prompts mới, prompt cũ giữ nguyên (append không clear) |
| Render 5 video từ 5 prompt random của batch N=10 | Manual check: 5 video character + setting khác nhau rõ |
| Không vỡ tab Idea→Video | Mở tab Idea→Video, gen 1 idea → vẫn chạy bình thường |

---

## 9. Risk + mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `push_to_text_to_video` không tìm thấy tab (chưa khởi tạo) | Med | Low | Lazy init: nếu không thấy, log warning + lưu prompts vào file `.tmp` để user copy thủ công. |
| Gemini sinh dialogue tiếng Việt thay vì tiếng Anh dù `language="English (en-US)"` | Med | High | Idea string đã ép "ALL dialogue MUST be in English". Nếu vẫn ra tiếng Việt → bơm thêm "RESPONSE LANGUAGE: English ONLY" vào idea. Test sớm. |
| Step 1 không tôn trọng character archetype, sinh nhân vật khác | Low | Low | Idea string ép "MAIN CHARACTER: {desc}". Step 1 tự rewrite expand thì OK, không vấn đề. |
| Char hash collision quá thường xuyên (Gemini lặp tên "Anna" liên tục) | Med | Med | Hash `name+species+age+gender` đủ phân biệt cho hầu hết case. Nếu collision rate > 30% thì upgrade hash thêm `signature_feature`. |
| User Generate N=50 → mất 25 phút | High | Low | Hiển thị progress "i/N" trên log. Chấp nhận, đây là chi phí Gemini, không phải bug. |
| stop_check chưa wire vào worker | Low | High | Test cụ thể bằng case "Stop giữa chừng" trên. Bug thì fix ngay. |
| `idea_to_video_workflow` ghi `WORKFLOWS_DIR/eng_auto_*` không clean lên | Low | Low | Đó là behavior bình thường của tool, user clean định kỳ. Không xử lý. |
| Concurrent click Generate (race) | Low | Med | Disable button khi worker chạy. |

---

## 10. Time estimate

| Task | Hours |
|------|-------|
| Viết `eng_lesson_pool.json` (12 topic × 8 scenario × 8 char) | 1.5 |
| Viết `eng_auto_prompt.py` (load+random+generate_batch) | 2.0 |
| Viết `tab_eng_auto.py` (UI + worker thread) | 2.0 |
| Sửa `tab_text_to_video.py` thêm `append_prompts` | 0.3 |
| Sửa `main_window.py` + `pages.py` đăng ký tab + nav item | 0.7 |
| Test N=1, N=5 (real Gemini call) | 1.0 |
| Test stop, collision, regression Idea→Video | 0.5 |
| Polish + log message tiếng Việt + edge case | 0.5 |
| **TỔNG** | **~8.5h, ship trong 1 ngày làm việc** |

---

## 11. Files: new vs modified

- **New:** 4 (wrapper + tab + JSON + spec)
- **Modified:** 3 (`main_window`, `pages`, `tab_text_to_video`)
- **Lines touched:** ~+550 / -0
- **Breaking change:** None. Tab cũ y nguyên, `idea_to_video.py` không đụng.

---

## Tóm tắt 1 câu

> "Tab riêng nhỏ, reuse nguyên `idea_to_video_workflow`, in-memory dedupe 2 lớp, Gemini-only, output đẩy sang tab Text→Video. Ship 1 ngày, đủ tốt cho user yêu cầu cơ bản."
