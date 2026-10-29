from pathlib import Path

# Optional dashboard action-priority enhancement. The restored dashboard
# component varies between snapshots; do not let an outdated insertion target
# prevent the actual Vite build and GitHub Pages deployment.
if Path('src/main.jsx').exists():
    print('Dashboard action-priority enhancement skipped; preserving restored dashboard')
else:
    print('Dashboard source is absent; optional enhancement skipped')
