# /migrate-to-blocks <path-to-content-file>

Migrate a content JSON file from legacy `body_html` to block-based structure.

Usage: `/migrate-to-blocks content/heritage/cuisine.json`

The file path is: $ARGUMENTS

---

1. Read the file at `$ARGUMENTS`
2. If it already has `blocks` and `body_html` is empty, output "Already migrated." and stop
3. Capture the full current value of `body_html` — do not discard it
4. Build a new `blocks` array:
   - `{"type": "facts", "items": [...]}` — extract key facts from the existing prose
   - `{"type": "html", "html": "<verbatim body_html value>"}` — copy the existing HTML exactly
   - `{"type": "timeline", ...}` — add 6–10 dated entries for this topic
5. Set `"body_html": ""` in the JSON (keep the key, empty the value)
6. Run `python3 scripts/build_site.py` — must succeed
7. Commit: `git add $ARGUMENTS && git commit -m "content: migrate $ARGUMENTS to block-based structure"`
8. Push: `git push -u origin claude/agent-automation-checklists-lGrNX`
