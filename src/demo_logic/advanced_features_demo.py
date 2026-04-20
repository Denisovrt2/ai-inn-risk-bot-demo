from __future__ import annotations

from typing import Any, Dict


def is_empty_value(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def normalize_numeric(value: Any) -> Any:
    if value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        raw = value.strip().replace(" ", "").replace(",", ".")
        if not raw:
            return None
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except Exception:
            return value
    return value


def safe_max(current: Any, candidate: Any) -> Any:
    current = normalize_numeric(current)
    candidate = normalize_numeric(candidate)

    if is_empty_value(current):
        return candidate
    if is_empty_value(candidate):
        return current

    if isinstance(current, (int, float)) and isinstance(candidate, (int, float)):
        return max(current, candidate)

    return current


def reconcile_with_base_features(
    advanced_output: Dict[str, Any],
    result_data: Dict[str, Any],
) -> Dict[str, Any]:
    base = (result_data.get("features") or {}) if isinstance(result_data, dict) else {}
    if not isinstance(base, dict) or not base:
        return advanced_output

    out = dict(advanced_output)

    passthrough_keys = [
        "total_cases",
        "defendant_cases",
        "plaintiff_cases",
        "defendant_ratio",
        "plaintiff_ratio",
        "bankruptcy_procedures_count",
        "has_bankruptcy",
        "tax_arrears_total",
        "employees_latest",
        "mass_director_flag",
        "pre_distress_signal",
    ]

    for key in passthrough_keys:
        base_value = base.get(key)
        current_value = out.get(key)

        if is_empty_value(base_value):
            continue

        if key not in out or is_empty_value(current_value):
            out[key] = base_value

    out["total_cases"] = safe_max(out.get("total_cases"), base.get("total_cases"))
    out["defendant_cases"] = safe_max(out.get("defendant_cases"), base.get("defendant_cases"))
    out["plaintiff_cases"] = safe_max(out.get("plaintiff_cases"), base.get("plaintiff_cases"))
    out["bankruptcy_procedures_count"] = safe_max(
        out.get("bankruptcy_procedures_count"),
        base.get("bankruptcy_procedures_count"),
    )
    out["tax_arrears_total"] = safe_max(out.get("tax_arrears_total"), base.get("tax_arrears_total"))
    out["employees_latest"] = safe_max(out.get("employees_latest"), base.get("employees_latest"))

    out["product_meaning"] = (
        "Advanced layer агрегирует критичные risk-signals и устраняет конфликты "
        "между базовыми признаками и расширенной интерпретацией."
    )

    return out


if __name__ == "__main__":
    demo_result_data = {
        "features": {
            "total_cases": 14,
            "defendant_cases": 9,
            "plaintiff_cases": 5,
            "defendant_ratio": 0.64,
            "bankruptcy_procedures_count": 1,
            "has_bankruptcy": True,
            "tax_arrears_total": 250000,
            "employees_latest": 18,
            "mass_director_flag": True,
            "pre_distress_signal": True,
        }
    }

    demo_output = reconcile_with_base_features(
        {"layer": "advanced_features", "source_mode": "public_demo"},
        demo_result_data,
    )
    print(demo_output)