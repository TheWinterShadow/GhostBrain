---
> **Template Guide — Project Index Note**
> **Lives in:** `20_Active_Work/ProjectName/` (this is the main note inside a project's subfolder)
> **Filename:** `ProjectName.md` (same as the folder name)
> **Folder structure for a project:**
> ```
> 20_Active_Work/ProjectName/
> ├── ProjectName.md          ← this file (index + status)
> ├── architecture.md         ← design docs (no prefix needed, folder gives context)
> ├── Decision - Topic.md     ← decision logs (use Decision_Template)
> ├── Chat - Topic - Date.md  ← AI chat captures (use Chat_Template)
> └── ...
> ```
> **When done:** Move the entire `ProjectName/` folder to `60_Archives/`
> **Tags:** `#project` + `#status/active` + domain tags
---

#project #status/active #

---

# {{title}}

## Overview

**Status:** Active | On Hold | Blocked | Complete
**Priority:** High | Medium | Low
**Started:** {{date:YYYY-MM-DD}}
**Target:**
**Owner:**

*What is this project? What does success look like?*


---

## Goals

- [ ]
- [ ]
- [ ]

---

## Active Tasks

```tasks
(tag includes #task) OR (description includes #task)
path includes {{title}}
not done
```

---

## Task Capture

*Add tasks here. Use `#task` so they show on the dashboard.*

### Priority / Next Up
- [ ] #task 📅
- [ ] #task 📅

### In Progress
- [/] #task

### Waiting On
- [-] #task

### Backlog
- [ ] #task
- [ ] #task

---

## Documents in This Folder

*List key files for quick navigation. Update as you add files.*

- [[{{title}}]] ← this file
-

---

## Key Decisions

*For important decisions, create a `Decision - Topic.md` file. Log quick decisions here.*

| Date | Decision | Why |
|------|----------|-----|
|  |  |  |

---

## Notes & Updates

*Running log. Newest at top.*

### {{date:YYYY-MM-DD}}


---

## People & Resources

**Stakeholders:**
**Links:**
**Related projects:**

---

*Created: {{date:YYYY-MM-DD}}*
