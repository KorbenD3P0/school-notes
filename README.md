# School Notes

Personal course notes, kept in plain Markdown and versioned with git.

## Structure

```
courses/
  <course-name>/
    YYYY-MM-DD-topic.md
templates/
  note-template.md
```

Each course gets its own folder under `courses/`. Notes are named
`YYYY-MM-DD-short-topic.md` so they sort chronologically. Start a new note
from `templates/note-template.md`.

## Adding a course

```
mkdir -p courses/course-name
cp templates/note-template.md courses/course-name/$(date +%F)-topic.md
```

Then edit, `git add`, `git commit`.

---
This repo is public. Don't put personal identifiers (student ID, address,
phone number, etc.) in any note.
