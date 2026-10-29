from pathlib import Path

p = Path('src/main.jsx')
s = p.read_text()

# The Finance components restored by restore-components.py already contain a
# working Dashboard implementation. Older dashboard replacement targets are
# not stable across restored component versions, so this step must be
# non-destructive and never block the Pages build.
if 'function Dash(' not in s or 'function DashFluxo(' not in s:
    print('Dashboard components are not available in this build; skipping optional dashboard enhancement')
else:
    print('Dashboard components already restored; skipping stale dashboard replacement patch')
