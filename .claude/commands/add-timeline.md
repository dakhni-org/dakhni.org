# /add-timeline <path-to-content-file>

Add a timeline block to a content JSON file.

Usage: `/add-timeline content/sufism/bandanawaz.json`

The file path is: $ARGUMENTS

---

1. Read the file at `$ARGUMENTS`
2. Check if a `timeline` block already exists in `blocks` — if yes, output "Already has timeline." and stop
3. Read the existing `facts` and `html` blocks to understand the subject's key dates and events
4. Append a timeline block to the end of the `blocks` array:
   ```json
   {
     "type": "timeline",
     "eyebrow": "<short descriptor>",
     "title": "<Subject> in dates",
     "items": [
       { "year": "YYYY", "text": "One-sentence event description." }
     ]
   }
   ```
   Include 6–12 items using dates and facts consistent with the existing file content.
5. Run `python3 scripts/build_site.py` — must succeed
6. Commit: `git add $ARGUMENTS && git commit -m "content: add timeline to $ARGUMENTS"`
7. Push: `git push -u origin claude/agent-automation-checklists-lGrNX`
