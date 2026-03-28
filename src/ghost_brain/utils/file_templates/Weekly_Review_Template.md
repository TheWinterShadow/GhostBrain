#weekly-review #date/{{date:YYYY-MM-DD}}

---

# Weekly Review - Week of {{date:YYYY-MM-DD}}

---

## 🎯 Weekly Focus

**This week's theme/goal:**


**Top 3 priorities for the week:**
1. 
2. 
3. 

---

## 📋 Task Review

### ⚠️ Overdue Tasks (Need Attention)

```tasks
(tag includes #task) OR (description includes #task)
not done
due before {{date:YYYY-MM-DD}}
short mode
```

**Action:** Reschedule or delete these tasks now.

---

### 📥 Tasks Without Due Dates (Process These)

```tasks
(tag includes #task) OR (description includes #task)
not done
no due date
limit 50
group by filename
short mode
```

**Action:** Add due dates or move to someday/maybe.

---

### ✅ Completed This Week

```tasks
(tag includes #task) OR (description includes #task)
done after {{date-7:YYYY-MM-DD}}
sort by done reverse
short mode
```

**Wins this week:**
- 
- 
- 

---

## 🎯 Active Projects Review

```dataview
TABLE WITHOUT ID
  file.link as "Project",
  length(file.tasks.text) as "Total Tasks",
  length(filter(file.tasks, (t) => !t.completed)) as "Open",
  round((length(filter(file.tasks, (t) => t.completed)) / length(file.tasks.text)) * 100, 0) + "%" as "Done %"
FROM "20_Active_Work"
WHERE file.tasks
SORT file.name ASC
```

### Project Notes
**Projects on track:**
- 

**Projects needing attention:**
- 

**Projects to archive:**
- 

---

## 🧹 Cleanup Checklist

- [ ] Processed all items in `00_Inbox`
- [ ] Reviewed and updated active project notes
- [ ] Archived completed projects to `40_Archives`
- [ ] Added due dates to undated tasks or deleted them
- [ ] Cleared out old daily notes (>30 days if not needed)
- [ ] Updated recurring tasks that need adjustment
- [ ] Reviewed "Waiting On" tasks - followed up?

---

## 📊 This Week's Stats

**Total tasks completed:** 
**New projects started:** 
**Projects completed:** 
**Tasks still open:** 

---

## 💭 Reflection

### What worked well this week?


### What didn't work?


### What am I learning about my workflow?


### What needs to change?


---

## 📅 Next Week Planning

### Week of {{date+7:YYYY-MM-DD}}

**Weekly goal/theme:**


**Top 3 priorities:**
1. [ ] #task 📅 {{date+7:YYYY-MM-DD}}
2. [ ] #task 📅 {{date+7:YYYY-MM-DD}}
3. [ ] #task 📅 {{date+7:YYYY-MM-DD}}

**Big rocks for next week:**
- Monday: 
- Tuesday: 
- Wednesday: 
- Thursday: 
- Friday: 

**Upcoming deadlines:**
- 

---

## 🎨 Lifestyle & Wellbeing

**Energy level this week:** ⚡⚡⚡⚡⚡

**Work-life balance:** ⭐⭐⭐⭐⭐

**Exercise/Movement:**
- [ ] Monday
- [ ] Tuesday  
- [ ] Wednesday
- [ ] Thursday
- [ ] Friday
- [ ] Weekend

**Self-care highlights:**
- 
- 

**Social connections:**
- 

---

## 💡 Ideas & Insights

### New ideas captured this week
- 

### Articles/Books that inspired me
- 

### Skills I want to develop
- 

---

## 🔗 Quick Links

- [[Tasks Dashboard]]
- **Last Week:** [[{{date-7:YYYY-MM-DD}}]]
- **Next Week:** [[{{date+7:YYYY-MM-DD}}]]
- [[Task Management Guide]]

---

## 📝 Additional Notes


---

*Weekly review completed: {{date:YYYY-MM-DD}} at {{time}}*

**Remember:** You can't do everything. Focus on what matters most.
