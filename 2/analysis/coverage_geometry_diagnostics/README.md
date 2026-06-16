# Coverage Geometry Diagnostics

Small mechanism-diagnostic pilot for closed-world multi-agent false completion.

This is intentionally separate from the main paper and experiment code. It only
uses existing logs and reports missing fields instead of fabricating them.
The archived `liudang1/` tree is treated as read-only historical data; all new
diagnostic scripts, reports, CSVs, and figures are written under this directory.

Run:

```powershell
python analysis\coverage_geometry_diagnostics\run_diagnostics.py
```

Main outputs:

- `analysis/coverage_geometry_diagnostics/docs/geometry_log_audit.md`
- `analysis/coverage_geometry_diagnostics/docs/coverage_geometry_diagnostic_report.md`
- `analysis/coverage_geometry_diagnostics/results/run_level_summary.csv`
- `analysis/coverage_geometry_diagnostics/results/coverage_geometry_metrics.csv`
- `analysis/coverage_geometry_diagnostics/figures/*.png`
