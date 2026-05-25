"""CompanyConfirm agent — runs in-process.

Given a user-supplied company name, this agent normalizes it against the
known company registry. If we can resolve it deterministically (e.g. "pwc"
-> "PricewaterhouseCoopers"), we return the canonical form directly. Only
when resolution fails do we fall back to an LLM clarification step.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..tools.companies import Company, known_companies, resolve_company


@dataclass
class CompanyConfirmation:
    raw: str
    company: Company | None
    canonical_name: str | None
    notes: str

    def to_dict(self) -> dict:
        return {
            "raw": self.raw,
            "canonical_name": self.canonical_name,
            "tenant": self.company.tenant if self.company else None,
            "site": self.company.site if self.company else None,
            "notes": self.notes,
        }


def confirm_company(raw_name: str) -> CompanyConfirmation:
    """Resolve a raw user-typed company string to a registered ``Company``."""
    company = resolve_company(raw_name)
    if company:
        return CompanyConfirmation(
            raw=raw_name,
            company=company,
            canonical_name=company.canonical_name,
            notes=f"Resolved '{raw_name}' to '{company.canonical_name}'.",
        )
    options = ", ".join(known_companies())
    return CompanyConfirmation(
        raw=raw_name,
        company=None,
        canonical_name=None,
        notes=(
            f"Could not resolve '{raw_name}'. Supported companies: {options}."
        ),
    )
