# Arkin Sales Portal — Deployment Guide

Goal: get a **public URL** you can share with your boss, with **username + password** login.

---

## What changed in this version

1. **Product scoping is now strict**: Every RM, ABM, RBM, and ZH belongs to exactly one product (STLAP or Wheels). They see only their product's data. Only **CXO** and **Central Team** see both products.
2. **Real login**: username + password form replaces the demo dropdown. Same demo password `arkin@2026` for all accounts.
3. **Hierarchy is now product-split**:
   - 8 ZHs (4 STLAP + 4 Wheels)
   - 30 RBMs (15 STLAP + 15 Wheels)
   - 200 ABMs (100 STLAP + 100 Wheels)
   - 600 RMs (300 STLAP + 300 Wheels)

---

## EASIEST DEPLOY — Streamlit Community Cloud (Free)

**End result**: A public link like `https://arkin-portal.streamlit.app` that anyone with the password can access. Free, takes 15 minutes, no servers to manage.

### One-time setup

**Step 1 — Make a GitHub account** (if you don't have one)
Go to https://github.com → Sign up. Free.

**Step 2 — Create a new repository**
1. On GitHub, click the **+** at the top right → **New repository**
2. Name it: `arkin-portal`
3. Set it to **Private** (your data shouldn't be on a public repo)
4. Click **Create repository**

**Step 3 — Upload your files to GitHub**
On the repository page, click **uploading an existing file** (the link in the middle of the screen).

Drag and drop these files from your Mac:
- `arkin_app.py`
- `requirements.txt`
- The `arkin/` folder (containing `arkin_dummy_data.xlsx`)

For the folder, you may need to drag the individual file inside. To keep folder structure: just create the folder via GitHub web UI:
1. Click **Create new file**
2. In the filename box, type: `arkin/arkin_dummy_data.xlsx` — but since GitHub web UI doesn't allow uploading binaries this way, use this trick instead:

**Easier approach using terminal**:
```bash
cd /Users/shekhar/Desktop/arkin/arkin_portal
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/arkin-portal.git
git push -u origin main
```
(Replace `YOUR_USERNAME` with your actual GitHub username. You'll be asked to log in — use a Personal Access Token from GitHub settings as the password.)

**Step 4 — Sign up for Streamlit Community Cloud**
1. Go to https://share.streamlit.io
2. Click **Sign in with GitHub**
3. Authorize Streamlit to access your repos

**Step 5 — Deploy your app**
1. On Streamlit Cloud, click **New app**
2. Pick your repo: `YOUR_USERNAME/arkin-portal`
3. Branch: `main`
4. Main file path: `arkin_app.py`
5. Click **Deploy**

Wait 2-3 minutes. Streamlit builds your app and gives you a URL like:
```
https://YOUR_USERNAME-arkin-portal-arkin-app-XXXXXX.streamlit.app
```

(You can rename it from the Settings panel after deploy to something cleaner, like `arkin-portal.streamlit.app`.)

**Step 6 — Send to your boss**

```
Hi [Boss],

Demo link: https://YOUR_APP_URL.streamlit.app

Try these accounts (password for all: arkin@2026):

• Sales Manager (STLAP):   rm.3001
• Sales Manager (Wheels):  rm.4001
• Team Leader (ABM):       abm.2001
• Regional Business Mgr:   rbm.201
• Zonal Head:              zh.131
• CXO (sees both):         cxo
• Admin:                   admin

Each persona shows a different view of the data.

Best,
Shekhar
```

---

## ALTERNATIVE — Render.com (also free, slightly more flexible)

If Streamlit Cloud's free tier isn't enough (it sleeps after 7 days inactivity), Render gives you 750 free hours/month.

1. Sign up at https://render.com (GitHub login)
2. **New +** → **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `streamlit run arkin_app.py --server.port=$PORT --server.address=0.0.0.0`
5. Deploy. You get a URL like `https://arkin-portal.onrender.com`

---

## How the new login works

When you (or your boss) open the URL:
1. A login form appears
2. Type any valid username (e.g. `rm.3001`) + password `arkin@2026`
3. The app authenticates and lands on the persona dashboard

**Username format**: `<level>.<id>` (e.g. `rm.3001`, `abm.2001`, `rbm.201`, `zh.131`). Special accounts: `cxo`, `central`, `admin` (no number).

**Password**: `arkin@2026` for every account in the demo. To change it, edit the `DEMO_PASSWORD` constant in `arkin_app.py` and redeploy.

For production with multiple real passwords, the `pw_hash` field per user in `build_user_directory()` is ready — you'd swap the constant hash with per-user hashes from a user table or AD.

---

## What your boss will see by role

| Login | Lands on |
|---|---|
| `rm.3001` | Personal RM dashboard — only their own STLAP data, AI nudges, funnel, portfolio |
| `rm.4001` | Same but for a Wheels RM |
| `abm.2001` | Team view (3 RMs) — STLAP only, leaderboards, escalations, nudge button |
| `rbm.201` | Regional view (20 RMs) — STLAP, profitability, RoA recommendations |
| `zh.131` | Zonal view — STLAP, region-wise breakdown, top/bottom ABMs |
| `cxo` | Everything across both products with a STLAP/Wheels/Both toggle |
| `admin` | Upload data, manage notifications, see user directory |

---

## Quick local test before deploying

```bash
cd /Users/shekhar/Desktop/arkin/arkin_portal
streamlit run arkin_app.py
```

Open `http://localhost:8501`. You should see the login form. Try `cxo` / `arkin@2026` to see the full view.

---

## Troubleshooting

**"This app is in the workspace's free tier"** → Streamlit free tier is fine for demos. Boss won't see this.

**App sleeps after inactivity (Streamlit Cloud)** → First load might take 30 seconds while it wakes. Or upgrade to paid tier (~$20/mo), or use Render which doesn't sleep.

**Want a custom domain like `arkin.yourcompany.com`?** → Both Streamlit and Render support custom domains on paid plans. Tell me and I can guide.

**Want to keep the data private to your company?** → Don't deploy to public cloud. Use the Docker/intranet path from the earlier README on a company-internal VM.
