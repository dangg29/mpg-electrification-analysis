# Dashboard

A responsive static application for exploring vehicle configurations. Files are `index.html`, `styles.css`, `app.js`, and generated `data.json`. No npm build step, external chart CDN, backend, or account is required at runtime.

## Local use

From the repository root:

```bash
python -m http.server 8501 --bind 127.0.0.1 --directory dashboard
```

Open http://127.0.0.1:8501. Do not open the HTML via `file://`, because browsers may block its JSON request.

The default window is 1984–2026, excluding the newest observed model year. Filter by both year endpoints, manufacturer, segment, and powertrain. All four charts, summary metrics, and efficiency tables respond to those filters. Saved model metrics and scenarios are deliberately independent of filter changes.

CSV download exports additive aggregate groups, not vehicle-level rows. Summing `n` gives the number of selected configurations. Divide summed `mpg_sum` by summed `mpg_n` to reconstruct the mean; do not average pre-aggregated means without weights.

## Regenerate

```bash
python scripts/modeling.py
python scripts/build_dashboard.py
```

These commands require the feature Parquet dataset. `python scripts/run_all.py` rebuilds the entire project.

## Static deployment

Any host that serves these four files over HTTPS can host the dashboard. The repository contains a `vercel.json` configuration with output directory `dashboard` and no build command, plus `.vercelignore` to exclude the raw workbook, notebooks, reports, environment, and other local work from a CLI upload.

For a Vercel deployment, import the repository with the Other framework preset, no build command, and `dashboard` as the output directory; alternatively run the Vercel CLI from the repository root. Review the current hosting plan and account terms before enabling paid options. This application needs only static hosting and makes no paid API calls.

**Deployment status:** production deployment is READY at [https://mpg-electrification-analysis.vercel.app](https://mpg-electrification-analysis.vercel.app), verified September 24, 2026. The five browser filter/download cases also passed on the hosted site.

The deployment uploaded only `index.html`, `styles.css`, `app.js`, and `data.json` (381,198 bytes). Local Vercel metadata and credentials were excluded. The private GitHub repository was not connected automatically to Vercel, so future Git pushes do **not** currently redeploy the site. GitHub Actions reproduces and tests the analysis independently.

To redeploy with the same narrow upload scope, from Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force .work/vercel-dashboard | Out-Null
Copy-Item dashboard/index.html,dashboard/styles.css,dashboard/app.js,dashboard/data.json .work/vercel-dashboard
npx.cmd --yes vercel@60.0.0 login
npx.cmd --yes vercel@60.0.0 link --yes --project mpg-electrification-analysis --scope dangdeptrai29s-projects --cwd .work/vercel-dashboard
npx.cmd --yes vercel@60.0.0 deploy --dry --json --cwd .work/vercel-dashboard
npx.cmd --yes vercel@60.0.0 deploy --prod --yes --cwd .work/vercel-dashboard
```

Login is needed only when signed out. Confirm the dry run contains the four expected assets before deployment. Use your own scope if publishing a fork. The ignored `.work/` directory may contain local authentication files; never commit it.


## Browser checks

The browser regression script compares five scenarios with independently computed snapshot values and validates the downloaded CSV counts. With `agent-browser` installed and the local server running:

```powershell
npx.cmd agent-browser open http://127.0.0.1:8501
Get-Content -Raw tests/dashboard.browser.js | npx.cmd agent-browser eval --stdin
```

```bash
npx agent-browser open http://127.0.0.1:8501
npx agent-browser eval --stdin < tests/dashboard.browser.js
```

See [verification evidence](../reports/verification.md). The analytical tests separately check aggregate weights against the underlying Parquet records.
