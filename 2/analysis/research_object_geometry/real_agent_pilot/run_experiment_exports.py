from __future__ import annotations

from build_controller_decision_table import build_table
from build_oracle_appendix_export import build_oracle_appendix_export
from build_sensitivity_exports import build_sensitivity_exports
from build_source_route_ablation import build_source_route_ablation
from run_unified_pipeline import export_all


def main() -> None:
    export_all()
    build_table()
    build_source_route_ablation()
    build_sensitivity_exports()
    build_oracle_appendix_export()


if __name__ == "__main__":
    main()
