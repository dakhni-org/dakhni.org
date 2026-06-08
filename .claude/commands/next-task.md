# /next-task — pick one task, complete it, commit, push, stop

You are running unattended. Complete **exactly one** task from PLAN.md then stop.
Doing more than one task in a single run wastes plan quota — stop after the first.

---

## Step 1 — Read the plan

Read `PLAN.md`. Find the **first line** that matches `- [ ]` (the first unchecked checkbox).
That is your task. Note the file path it mentions.

If there are **no unchecked boxes**, output "All tasks in PLAN.md are complete." and stop immediately.

---

## Step 2 — Read the target file

Read the JSON file named in the task. Understand its current structure:
- What `page_type` is it?
- What `blocks` does it already have?
- What prose is in the existing `html` block or `body_html`?

---

## Step 3 — Implement the task

Follow the task's phase instructions exactly:

**Phase 1 & 2 — Add timeline block:**
Append a new block object at the end of the `blocks` array:
```json
{
  "type": "timeline",
  "eyebrow": "<short descriptor, e.g. 'A Dynastic Chronology'>",
  "title": "<subject> in dates",
  "items": [
    { "year": "YYYY", "text": "One sentence describing the event." },
    ...
  ]
}
```
Include 6–12 items. Use dates and facts consistent with existing content in the file.
Write accurate historical content; do not invent dates or names not supported by the file.

**Phase 3, 4, 5 — Migrate body_html to blocks:**
1. Read the current `body_html` value (it will be a long HTML string).
2. Replace the `blocks` array with:
   ```json
   [
     { "type": "facts", "items": [ ... ] },
     { "type": "html", "html": "<existing body_html value verbatim>" },
     { "type": "timeline", "eyebrow": "...", "title": "...", "items": [ ... ] }
   ]
   ```
3. Set `"body_html": ""` — the value must remain in the JSON as an empty string, not removed.
4. The `facts` block: extract key facts already mentioned in the prose (dates, key people, key places).
5. Do NOT alter the existing HTML prose content — copy it verbatim into the html block.

**Phase 6 — Hub and new pages:**
Follow the specific task description in PLAN.md.

---

## Step 4 — Validate

Run the build:
```bash
python3 scripts/build_site.py
```

It must print `Rendered N pages` with no errors. If it fails:
- Read the error message
- Fix the JSON (likely a syntax error or missing required field)
- Re-run the build
- Do not proceed until the build is clean

---

## Step 5 — Mark done and commit

1. Edit `PLAN.md`: change the completed task's `- [ ]` to `- [x]`. Change only that one line.
2. Stage both files:
   ```bash
   git add <content-file-path> PLAN.md
   ```
3. Commit:
   ```bash
   git commit -m "content: <brief description of what was added>"
   ```
4. Push:
   ```bash
   git push -u origin claude/agent-automation-checklists-lGrNX
   ```

---

## Step 6 — Stop

Output a one-line summary: what file was changed and what was added.
Then stop. Do not pick another task.
