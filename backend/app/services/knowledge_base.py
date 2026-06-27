"""Mock HR knowledge base — serves as Emma's internal policy reference."""

from dataclasses import dataclass, field


@dataclass
class KBEntry:
    """Single knowledge base entry (HR policy/procedure)."""
    id: int
    category: str          # benefits / leave / payroll / policy / compliance / other
    title: str
    content: str
    tags: list[str] = field(default_factory=list)

    def matches(self, query: str) -> bool:
        """Simple relevance check for MVP (case-insensitive tag/keyword matching)."""
        combined = f"{self.title} {' '.join(self.tags)}".lower()
        return any(word in combined for word in query.lower().split())


# ── Mock KB content — realistic HR data, not dummy text ─────────────────────

MOCK_KB: list[KBEntry] = [
    KBEntry(
        id=1, category="leave", title="PTO Policy",
        content=(
            "Full-time employees accrue PTO at 4 hours per pay period (biweekly). "
            "New hires receive a prorated amount based on their start date. "
            "Unused PTO carries over up to 80 hours. "
            "PTO requests should be submitted at least 2 weeks in advance for planned time off."
        ),
        tags=["pto", "time off", "vacation", "accrual"],
    ),
    KBEntry(
        id=2, category="leave", title="Sick Leave Policy",
        content=(
            "All employees receive 40 hours of sick leave per year. "
            "Sick leave can be used for personal illness, medical appointments, "
            "or caring for a family member with a health condition. "
            "No advance notice required for unexpected illness — call the store manager first."
        ),
        tags=["sick", "illness", "medical", "family"],
    ),
    KBEntry(
        id=3, category="payroll", title="Pay Schedule",
        content=(
            "Employees are paid biweekly every other Friday. "
            "Direct deposit is the standard pay method. "
            "Paper checks can be requested through the HR portal and take 5 business days to process. "
            "Overtime must be pre-approved by your store manager."
        ),
        tags=["pay", "salary", "direct deposit", "overtime"],
    ),
    KBEntry(
        id=4, category="benefits", title="Health Insurance Enrollment",
        content=(
            "Eligible employees can enroll in medical, dental, and vision plans. "
            "Open enrollment occurs annually in November. "
            "New hires have 30 days from their start date to enroll. "
            "Company covers 60% of individual medical premiums; dependents are additional."
        ),
        tags=["insurance", "medical", "dental", "vision", "enrollment"],
    ),
    KBEntry(
        id=5, category="policy", title="Dress Code — Store Staff",
        content=(
            "Store staff must wear company-branded uniforms: black pants, branded polo shirt, "
            "non-slip shoes. No open-toed shoes or sandals. "
            "Name badges must be worn at all times on the sales floor. "
            "Hats are allowed if they are company-branded."
        ),
        tags=["dress code", "uniform", "branded", "badge"],
    ),
    KBEntry(
        id=6, category="compliance", title="Workplace Harassment Policy",
        content=(
            "Emma.ai's parent company maintains a zero-tolerance harassment policy. "
            "Any form of harassment based on race, gender, religion, age, disability, or "
            "sexual orientation is prohibited. Employees who experience or witness harassment "
            "should report to their store manager, an HR representative, or use the anonymous hotline."
        ),
        tags=["harassment", "compliance", "zero tolerance", "reporting"],
    ),
    KBEntry(
        id=7, category="payroll", title="Wage and Hour — Non-Exempt Staff",
        content=(
            "Non-exempt employees are paid hourly with overtime at 1.5x after 40 hours per week. "
            "Employees must clock in/out for every shift. Meal breaks of 30 minutes are unpaid "
            "and required after 5 consecutive hours on duty. Rest breaks of 10 minutes are paid "
            "and provided for every 4 hours worked."
        ),
        tags=["wage", "hourly", "overtime", "break", "clock"],
    ),
    KBEntry(
        id=8, category="other", title="Employee Discount Program",
        content=(
            "All active employees receive a 15% discount on eligible in-store purchases. "
            "Discount applies Monday through Thursday only. Not valid on alcohol, cigarettes, "
            "gift cards, or promotional items. Cannot be combined with other offers."
        ),
        tags=["discount", "perk", "purchase", "employee benefit"],
    ),
]


def search_kb(query: str, category: str | None = None) -> list[KBEntry]:
    """Search the mock knowledge base. Returns top 5 most relevant entries."""
    results = [entry for entry in MOCK_KB if entry.matches(query)]
    if category:
        results = [r for r in results if r.category == category]
    return results[:5]
