---
> **Template Guide — Weekly Review**
> **Lives in:** `10_Daily_Log/`
> **Filename:** `YYYY-MM-DD Weekly Review.md` (use the Monday date of the week)
> **Cadence:** Once a week, ideally Friday afternoon or Sunday evening
> **Tags:** `#weekly-review`
---

#weekly-review #date/{{date:YYYY-MM-DD}}

---

# Weekly Review — Week of {{date:YYYY-MM-DD}}

---

## This Week's Focus

**Theme / goal:**

**Top 3 I committed to:**
1.
2.
3.

**Did I hit them? Why / why not:**


---

## Task Review

### Overdue (deal with these now)

```tasks
(tag includes #task) OR (description includes #task)
not done
due before {{date:YYYY-MM-DD}}
short mode
```

*For each: reschedule, delegate, or delete.*

---

### No Due Date (process these)

```tasks
(tag includes #task) OR (description includes #task)
not done
no due date
limit 30
group by filename
short mode
```

*Add a date, move to someday, or delete.*

---

### Completed This Week

```tasks
(tag includes #task) OR (description includes #task)
done after {{date-7:YYYY-MM-DD}}
sort by done reverse
short mode
```

**Wins worth noting:**
-
-

---

## Project Health Check

```dataview
TABLE WITHOUT ID
  file.link as "Project",
  length(filter(file.tasks, (t) => !t.completed)) as "Open Tasks"
FROM "20_Active_Work"
WHERE file.tasks
SORT file.name ASC
```

**On track:**
-

**Needs attention:**
-

**Ready to archive → move to `60_Archives/`:**
-

---

## Folder Sweep

- [ ] `00_Inbox` — processed everything, nothing >30 days old
- [ ] `20_Active_Work` — all active projects still active? Archive any that are done.
- [ ] `40_Career` — any job search material to archive?
- [ ] `45_Life_Admin` — any outdated info to delete or update?
- [ ] Reviewed "Waiting On" tasks — followed up where needed

---

## Reflection

**What worked well:**

**What didn't:**

**What I'm learning about how I work:**

---

## Next Week Planning

**Week of {{date+7:YYYY-MM-DD}}**

**Theme:**

**Top 3:**
1. [ ] #task 📅 {{date+7:YYYY-MM-DD}}
2. [ ] #task 📅 {{date+7:YYYY-MM-DD}}
3. [ ] #task 📅 {{date+7:YYYY-MM-DD}}

**Upcoming deadlines:**
-

---

**Last week:** [[{{date-7:YYYY-MM-DD}}]] | **Next week:** [[{{date+7:YYYY-MM-DD}}]] | [[Tasks Dashboard]]
