# 🚀 Setup Guide — Auto Streak Engine

Get this running in under 5 minutes.

---

## Step 1 — Create the GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name it something like `streak` or `daily-engine`
3. Set visibility: **Public** (required for contribution graph to count)
4. Don't initialize with anything — we'll push manually

---

## Step 2 — Clone & Push This Code

```bash
# Clone this template
git clone https://github.com/YOUR_USERNAME/streak.git
cd streak

# Copy all files from this folder into the repo
# (or just initialize fresh):

git init
git add -A
git commit -m "feat: initialize auto-streak engine"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/streak.git
git push -u origin main
```

---

## Step 3 — Enable Workflow Permissions

GitHub Actions needs write access to push commits back.

1. Go to your repo on GitHub
2. **Settings → Actions → General**
3. Scroll to **Workflow permissions**
4. Select: ✅ **Read and write permissions**
5. Click **Save**

That's it. `GITHUB_TOKEN` is auto-injected — no secrets to configure.

---

## Step 4 — Trigger a Test Run

1. Go to **Actions** tab in your repo
2. Click **🔥 Auto Streak** workflow
3. Click **Run workflow → Run workflow**
4. Watch it pass ✅

---

## Step 5 — Verify on Contribution Graph

After the workflow runs, visit your GitHub profile. The green square for today should appear within ~5 minutes.

---

## ⚙️ Configuration Options

### Change the schedule
Edit `.github/workflows/auto-streak.yml`:
```yaml
- cron: "47 2 * * *"   # Every day at 02:47 UTC
```
Use [crontab.guru](https://crontab.guru) to pick your preferred time.

### Change commit frequency (commits per day)
The script randomly picks 1–3 commits. To force exactly 1:
```yaml
- name: 🎲 Decide Commit Count (1–3)
  id: commit_count
  run: echo "count=1" >> $GITHUB_OUTPUT
```

### Add your own quotes
Edit `scripts/generate.py` — find the `QUOTES` list and add your own.

### Disable the README rewrite
Comment out `README_FILE.write_text(readme)` in `generate.py` if you want to manage README manually.

---

## 🔍 How the Contribution Graph Works

GitHub counts a commit toward your contribution graph if:
- It's pushed to the **default branch** (`main`/`master`)
- The repo is **public** OR you have a private contributions setting enabled
- The commit author email matches your GitHub account email

This workflow uses `streak-bot[bot]` as the author, which counts because it's pushing to **your** repo using your `GITHUB_TOKEN`.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| Workflow fails with `403` | Enable read+write permissions (Step 3) |
| No green square on profile | Make repo public, check "Private contributions" setting |
| Workflow not running on schedule | GitHub may delay cron jobs by up to 1hr. Wait or trigger manually. |
| `generate.py` error | Run `python scripts/generate.py` locally to debug |

---

## 📁 File Structure

```
.
├── .github/
│   └── workflows/
│       └── auto-streak.yml   ← Cron scheduler + Git push logic
├── scripts/
│   └── generate.py           ← Daily content generator
├── activity-log.json         ← Append-only activity log (last 90 days)
├── stats.json                ← Streak counter, longest streak, totals
├── README.md                 ← Auto-generated profile card
└── SETUP.md                  ← This file
```

---

*Built with GitHub Actions · Zero dependencies on your local machine*
