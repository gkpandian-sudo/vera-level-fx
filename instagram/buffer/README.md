# Instagram Content Buffer

Drop pre-made 1080×1080 PNG images into the matching subfolder.
The pipeline picks the **oldest image first** (FIFO), uses it for
the post, then **moves it to `instagram/posts/`** (not deleted).

If a folder is empty, the pipeline auto-generates the image as normal.

---

## Folder Map

| Folder | Used for | Post day |
|--------|----------|----------|
| `daily/` | Live positions card | Wed & Fri |
| `weekly/` | Weekly performance card | Mon |
| `monthly/` | Monthly P&L chart | 1st of month |
| `trust/` | Win rate / trust card | (manual trigger) |
| `edu/risk/` | Risk management rule posts | Tue / Thu |
| `edu/pairs/` | Pair spotlight posts | Tue / Thu |
| `edu/setup/` | Trade setup breakdown posts | Tue / Thu |

---

## Rules

- **File format:** PNG, 1080×1080 px recommended (Instagram square)
- **Naming:** anything you like — e.g. `gold-chart-June.png`, `eurusd-setup-01.png`
- **FIFO order:** oldest file is used first (sorted by filename alphabetically
  if timestamps match — prefix with `01_`, `02_` to control order)
- **After use:** file is moved to `instagram/posts/YYYY-MM-DD-{type}-buffered.png`
- **Caption:** always generated live from real account data — only the image is buffered

---

## How to Add Images

1. Create your 1080×1080 PNG on your phone, Canva, or any design tool.
2. Drop the file into the correct subfolder on your laptop.
3. Commit and push:
   ```
   git add instagram/buffer/
   git commit -m "buffer: add [description] image"
   git push
   ```
4. GitHub Actions will use it on the next scheduled post for that type.

---

## Tips

- You can queue multiple images — they drain one per post day.
- For `edu/` posts, drop into the correct sub-type folder (`risk/`, `pairs/`, or `setup/`)
  so it matches the caption that gets auto-generated.
- Leave a folder empty to fall back to auto-generated graphics anytime.
