
# 🌿 green-squares-bot

> **A fun and educational GitHub Actions bot that automatically commits on weekdays to keep your contribution graph active.**

![GitHub Workflow Status](https://img.shields.io/badge/GitHub%20Actions-Auto%20Commit%20Bot-brightgreen?logo=github)

---

## 💡 What is `green-squares-bot`?

Welcome to **green-squares-bot** — a simple yet creative bot that automatically generates commits to make your GitHub contribution graph colorful and active 🌱.

This is a **demo project** that showcases how you can use **GitHub Actions** to automate routine tasks, like generating commits on a schedule. It’s a great way to explore GitHub automation, scheduled workflows (via CRON), and Git operations — all within a lightweight and transparent project.

---

## ✨ Key Features

- 🔁 **Automated Commits on 3–5 Random Days per Week**  
  Each week, the bot picks 3 to 5 random days (including weekends) to commit.

- 🔢 **Multiple Commits per Day**  
  Generates between **3 to 15 commits** on each commit day, with natural variation.

- 🕒 **Runs Three Times Daily**  
  Scheduled runs spread throughout the day (Morning, Afternoon, Evening) to simulate organic activity.

- 🧠 **Human-like Commit Messages and Quotes**  
  Uses randomly selected inspirational quotes and emojis to simulate real development habits.

- 📜 **Commit History Logging**  
  Logs all commits in `commit_log.txt` for transparency and tracking.

- 🧪 **Educational Use Only**  
  Designed as a learning tool for GitHub Actions, automation, and CI/CD workflows.

---

## ⚙️ How It Works

This project uses a `commit.py` Python script executed through a scheduled GitHub Actions workflow (`.github/workflows/activity.yml`).

The workflow runs daily at three times:

- 🌅 **Morning:** `06:00 UTC` (11:30 AM IST)  
- 🌞 **Afternoon:** `12:00 UTC` (5:30 PM IST)  
- 🌙 **Evening:** `15:45 UTC` (9:15 PM IST)  

Each run performs:

1. 🧾 Git checkout  
2. ⚙️ Git identity setup  
3. 🎲 Weekly randomization of 3–5 commit days  
4. ✍️ Running `commit.py` to generate 3–15 commits on commit days  
5. 🗂️ Updating random files with quotes and messages  
6. 🔄 Pull latest changes with rebase  
7. 📤 Push commits if ahead  

---

## 🎨 Bonus: draw pixel art on your contribution graph

`pixel_art.py` is a small, separate, opt-in tool for the classic **"gitfiti"** trick:
GitHub's contribution graph is a 7-row (Sun–Sat) grid, one column per week, and it
only cares about a commit's *recorded* date — not when it was actually pushed. So
to light up a specific cell, you just need a commit backdated to that day.

It ships with a few hand-verified built-in shapes (`heart`, `diamond`, `square`,
`frame`), or you can pass your own 7-row pattern file (any non-space/`.`/`·`
character counts as "on").

```bash
# See a shape as ASCII, no git involved at all
python3 pixel_art.py --preview heart

# Dry run: prints the exact dates + commit counts, but touches nothing
python3 pixel_art.py --pattern heart --start-date 2026-08-02

# Actually make the backdated commits locally (still doesn't push)
python3 pixel_art.py --pattern heart --start-date 2026-08-02 --commit

# ...and push once you're happy with `git log`
python3 pixel_art.py --pattern heart --start-date 2026-08-02 --commit --push
```

`--start-date` must be a Sunday (it'll auto-snap forward to the next one if
not), and `--intensity 1..4` controls roughly how dark each lit cell renders
(more commits = darker green — GitHub's exact thresholds aren't published, so
treat this as approximate). This never touches or rewrites existing commits;
it only ever appends new ones, same as any other history backfill.

---

## 🚀 Getting Started

### Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/green-squares-bot.git
cd green-squares-bot
```

### Push to your own GitHub repository:

```bash
git remote rename origin old-origin
git remote add origin https://github.com/YOUR_USERNAME/green-squares-bot.git
git push -u origin master
```

Make sure the repository is **public** so commits show up on your GitHub profile contribution graph!

---

## 🔧 File Structure

```
green-squares-bot/
├── commit.py             # Main commit generator script
├── pixel_art.py          # Optional: draw shapes on the contribution graph
├── test_pixel_art.py     # Tests for pixel_art.py's date/pattern logic
├── daily_log.txt         # Rotating dummy file
├── progress.md           # Rotating dummy file
├── inspiration.txt       # Rotating dummy file
├── pixel_art_log.txt     # Content file for pixel_art.py's commits
├── commit_log.txt        # Records commit history
└── .github/
    └── workflows/
        └── activity.yml  # GitHub Actions workflow
```

---

## 🤝 Contributing

Contributions are welcome! 🎉  
If you have ideas for:
- Better commit logic  
- Cool new features  
- Code cleanup or optimization  

Feel free to fork this repo and open a pull request.

---

## ⚠️ **Disclaimer**

> **This project is for educational and demonstration purposes only.**  
> It is designed to show how GitHub Actions can be used for scheduled automation tasks — not for inflating contributions or misleading viewers.

Automating your GitHub activity can be a **fun and informative** way to learn about CI/CD, bots, scripting, and workflows — but it's important to use this responsibly:

- Be **transparent** in your usage  
- Avoid **spammy or misleading behavior**  
- Present it clearly as a **testbed for learning automation**

---

🧪 Built for learning, not for production.  
💚 Happy green squares!  
📅 Automation starts from: `2025-07-01`

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).  
Feel free to use, modify, and distribute it for learning and personal projects.  
See the full license in the [LICENSE](LICENSE) file.
