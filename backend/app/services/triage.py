"""Triage engine — classifies questions and determines routing."""

from enum import Enum


class TriageAction(str, Enum):
    ANSWER = "answer"         # Emma can resolve it from KB
    ESCALATE_HR = "escalate_hr"  # Needs human HR review
    ESCALATE_MANAGER = "escalate_manager"  # Store manager handles it


class TriageCategory(str, Enum):
    BENEFITS = "benefits"
    LEAVE = "leave"
    PAYROLL = "payroll"
    POLICY = "policy"
    COMPLIANCE = "compliance"
    OTHER = "other"


# Rule-based mapping: keywords → category + action
TRIAGE_RULES = [
    # Benefits-related
    ("insurance", TriageCategory.BENEFITS, TriageAction.ANSWER),
    ("benefit", TriageCategory.BENEFITS, TriageAction.ANSWER),
    ("enrollment", TriageCategory.BENEFITS, TriageAction.ANSWER),
    ("medical", TriageCategory.BENEFITS, TriageAction.ANSWER),
    ("dental", TriageCategory.BENEFITS, TriageAction.ANSWER),
    ("vision", TriageCategory.BENEFITS, TriageAction.ANSWER),

    # Leave-related
    ("pto", TriageCategory.LEAVE, TriageAction.ANSWER),
    ("vacation", TriageCategory.LEAVE, TriageAction.ANSWER),
    ("time off", TriageCategory.LEAVE, TriageAction.ANSWER),
    ("sick leave", TriageCategory.LEAVE, TriageAction.ANSWER),
    ("sick", TriageCategory.LEAVE, TriageAction.ANSWER),
    ("illness", TriageCategory.LEAVE, TriageAction.ANSWER),
    ("leave", TriageCategory.LEAVE, TriageAction.ANSWER),

    # Payroll-related
    ("pay", TriageCategory.PAYROLL, TriageAction.ANSWER),
    ("salary", TriageCategory.PAYROLL, TriageAction.ANSWER),
    ("wage", TriageCategory.PAYROLL, TriageAction.ANSWER),
    ("overtime", TriageCategory.PAYROLL, TriageAction.ESCALATE_HR),
    ("paycheck", TriageCategory.PAYROLL, TriageAction.ESCALATE_HR),
    ("direct deposit", TriageCategory.PAYROLL, TriageAction.ANSWER),
    ("hourly", TriageCategory.PAYROLL, TriageAction.ANSWER),

    # Compliance-related (always escalate)
    ("harassment", TriageCategory.COMPLIANCE, TriageAction.ESCALATE_HR),
    ("discrimination", TriageCategory.COMPLIANCE, TriageAction.ESCALATE_HR),
    ("compliance", TriageCategory.COMPLIANCE, TriageAction.ESCALATE_HR),
    ("legal", TriageCategory.COMPLIANCE, TriageAction.ESCALATE_HR),

    # Policy-related
    ("dress code", TriageCategory.POLICY, TriageAction.ANSWER),
    ("uniform", TriageCategory.POLICY, TriageAction.ANSWER),
    ("policy", TriageCategory.POLICY, TriageAction.ANSWER),
    ("procedure", TriageCategory.POLICY, TriageAction.ANSWER),
]


def classify_question(text: str) -> tuple[TriageCategory, TriageAction, list[str]]:
    """Classify a question by scanning for triage keywords.

    Returns (category, action, matched_keywords)."""
    text_lower = text.lower()
    matched = []
    last_match = None

    # Priority order matters — check more specific patterns first
    priority_order = [
        "time off", "sick leave", "payroll", "direct deposit",
        "dress code", "health insurance", "workplace harassment",
        "pto", "vacation", "harassment", "discrimination",
        "insurance", "benefit", "salary", "wage", "overtime",
    ]

    for keyword in priority_order:
        if keyword in text_lower:
            matched.append(keyword)

    for kw, category, action in TRIAGE_RULES:
        if kw in text_lower and kw not in matched:
            matched.append(kw)

    # Return the best match (first rule that applies from our priority-ordered scan)
    for keyword in matched:
        for kw, category, action in TRIAGE_RULES:
            if kw == keyword or keyword in kw or kw in keyword:
                return category, action, matched

    return TriageCategory.OTHER, TriageAction.ANSWER, matched
