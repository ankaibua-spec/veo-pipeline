# Tournament Judgement — Auto English Lessons Plan

> Lead-engineer review. Score 1–10 mỗi cột. Tổng = sum 4 cột (tối đa 40).

---

## 1. Bảng điểm

| Tiêu chí (10 = tốt nhất)                                    | Plan A — Conservative | Plan B — Aggressive | Plan C — Pragmatic |
|--------------------------------------------------------------|----------------------:|--------------------:|-------------------:|
| **Risk** (10 = ít rủi ro nhất)                              | **9**                 | 4                   | **8**              |
| **Time-to-ship** (10 = nhanh nhất)                          | **9**                 | 3                   | **8**              |
| **Quality** (10 = output diversity + UX tốt nhất)           | 5                     | **9**               | 7                  |
| **Maintainability** (10 = code sạch, dễ mở rộng)            | 5                     | **9**               | 7                  |
| **TỔNG / 40**                                                | **28**                | **25**              | **30** ⭐          |

### Diễn giải điểm

**Plan A — Conservative (28/40)**
- Risk 9: Chỉ chạm 1 file UI. Zero refactor.
- Time 9: 5h. Có thể ship trước trưa.
- Quality 5: Nhồi button vào tab Text→Video làm UI "ô nhiễm". Không có log riêng. Không có anti-collision dựa Step 1 char_lock. User N=20 sẽ phàn nàn "vài cái nhân vật lặp".
- Maintain 5: Tab Text→Video bắt đầu phình to với logic không thuộc về nó. Sau này muốn thêm option (level filter, topic filter) sẽ rối.

**Plan B — Aggressive (25/40)**
- Risk 4: Refactor `idea_to_video.py` là rủi ro cao nhất — có thể vỡ tab Idea→Video đang chạy ổn. Multi-LLM thêm nhiều surface lỗi (Groq rate, OpenRouter dead theo memory `openrouter_dead_use_groq.md`). Jaccard threshold cần tune.
- Time 3: 5–7 ngày. User chờ 1 tuần cho 1 feature dạy tiếng Anh là quá dài.
- Quality 9: Diversity 4 lớp + cross-session + preview/edit là chuẩn production. Output chắc chắn không trùng.
- Maintain 9: Tách package `prompt_engine/` rõ ràng, dễ thêm tiếng khác (Spanish, Japanese) sau.

**Plan C — Pragmatic (30/40)** ⭐ WINNING
- Risk 8: Tab riêng → không đụng UI tab khác. KHÔNG refactor `idea_to_video.py`. KHÔNG sửa Step 1/2/3 prompt template. Chỉ +1 method `append_prompts` vào tab Text→Video.
- Time 8: 1 ngày làm việc (8.5h). Ship 2026-04-30.
- Quality 7: 2 lớp dedupe (combo key + char_hash từ Step 1 output) đủ cho N=10–20. Tab riêng có log box → user thấy progress, professional hơn Plan A. Vẫn chưa có preview/edit như Plan B nhưng đó là "nice to have", không phải MVP requirement.
- Maintain 7: Wrapper `eng_auto_prompt.py` đứng riêng → sau này nâng cấp lên Aggressive (multi-LLM + state) chỉ cần extend wrapper, không sửa UI tab.

---

## 2. Quyết định

### 🥇 WINNING: **Plan C — Pragmatic** (30/40)

### 🥈 FALLBACK: **Plan A — Conservative** (28/40)

---

## 3. Reasoning (10 dòng)

1. User yêu cầu rõ "user nhập N → app tự sinh N prompt khác hoàn toàn → gen N video". MVP requirement, KHÔNG đòi preview/edit, KHÔNG đòi multi-LLM.
2. Plan B over-engineer cho yêu cầu này: 5-7 ngày, refactor `idea_to_video.py` rủi ro vỡ tab Idea→Video đang chạy ổn. Kèm theo `openrouter_dead_use_groq.md` đã ghi nhớ — multi-provider thật sự khó duy trì.
3. Plan A ship nhanh nhưng nhồi button vào tab Text→Video → UX kém, sau này thêm level/topic filter sẽ rối. Tab Text→Video nên giữ vai trò "render từ prompt list", không phải "generator".
4. Plan C cân bằng: tab riêng (clean separation), reuse `idea_to_video_workflow` 100% (zero refactor risk), 2 lớp dedupe (combo key + char_hash) đủ chống trùng cho user dùng N=10–20.
5. Plan C có "exit ramp": nếu sau ship user phàn nàn diversity yếu → nâng cấp wrapper `eng_auto_prompt.py` lên có Jaccard + state file mà không sửa UI. Path migration sang Plan B mượt.
6. Char hash từ Step 1 output (Plan C) giải quyết được rủi ro lớn nhất: 2 archetype khác nhưng Gemini sinh "Anna 28 Female" cho cả hai. Plan A KHÔNG có lớp này → có thể trùng nhân vật.
7. Bơm "ALL dialogue MUST be in English" + "CEFR level X" vào idea string đủ ép Gemini sinh English đúng level — không cần sửa Step 1/2/3 prompt template.
8. Plan A fallback lý do: nếu trong quá trình ship Plan C gặp vấn đề khó với `push_to_text_to_video` (race / signal bus phức tạp), có thể quick-pivot xuống Plan A: nhồi button vào tab Text→Video, append trực tiếp vào `self.editor` — bỏ qua signal bus. Mất 1h là xong.
9. KHÔNG chọn Plan B làm fallback vì timeline 5 ngày là blocker — không thể fallback nhanh.
10. Sau ship Plan C, đo: nếu N=20 batch user chạy 5 lần vẫn không phàn nàn trùng → giữ. Nếu phàn nàn → upgrade Plan B trong sprint sau.

---

## 4. Hand-off cho executor

Khi executor bắt đầu code Plan C, plan đã duyệt:

1. Bắt đầu từ `tool/data_general/eng_lesson_pool.json` — copy nguyên data từ Plan C section 3.
2. `tool/eng_auto_prompt.py` — copy pseudocode Section 5 thành code thật.
3. `tool/tab_eng_auto.py` — UI Section 4 + worker Section 5.
4. Wire vào main_window + pages.py.
5. Thêm `append_prompts` vào `tab_text_to_video.py`.
6. Test theo bảng Section 8.

**Test gate đầu tiên (BẮT BUỘC trước khi mở rộng):** Run N=1 với Gemini real. Verify:
- Step 1 output `language` = English.
- Step 3 prompt chứa "English" + level code.
- Editor tab Text→Video có +1 dòng đúng.

Nếu fail bước này → KHÔNG tiếp tục, debug idea string trước.

**Reviewer:** trước khi merge, `inspector` + `security-auditor` review:
- inspector: check thread safety (worker stop_check), check `push_to_text_to_video` không null-deref khi tab Text→Video chưa khởi tạo.
- security-auditor: check JSON pool path không bị path-traversal nếu user edit pool sau này; check log không leak Gemini key.
- performance-auditor: N=50 không freeze UI (worker thread + signal đúng cách).

---

## Files produced

- `/root/veo-pipeline/specs/auto_eng_prompt/plan_conservative.md`
- `/root/veo-pipeline/specs/auto_eng_prompt/plan_aggressive.md`
- `/root/veo-pipeline/specs/auto_eng_prompt/plan_pragmatic.md` ⭐ WINNER
- `/root/veo-pipeline/specs/auto_eng_prompt/judge.md` (file này)
