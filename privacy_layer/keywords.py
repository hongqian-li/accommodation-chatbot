# GDPR Article 9 Sensitive Keywords
# Organised by special category of personal data.
# Used for Stage 1 fast keyword scan in the privacy classifier.

SENSITIVE_KEYWORDS = {

    # --- GDPR Art. 9(1): Data concerning health ---
    "health": [
        "medical", "medicine", "medication", "diagnosis", "diagnosed",
        "disability", "disabled", "handicap", "wheelchair", "chronic",
        "illness", "ill", "sick", "disease", "disorder", "condition",
        "mental health", "mental illness", "depression", "anxiety",
        "therapy", "therapist", "psychologist", "psychiatrist", "psychiatric",
        "cancer", "diabetes", "epilepsy", "allergy", "allergic",
        "surgery", "operation", "hospital", "clinic", "treatment",
        "prescription", "doctor", "patient", "rehab", "rehabilitation",
        "overdose", "addiction", "substance abuse",
    ],

    # --- GDPR Art. 9(1): Family and personal situation ---
    # (Linked to health/social data that often reveals sensitive context)
    "family_situation": [
        "spouse", "husband", "wife", "partner", "pregnant", "pregnancy",
        "maternity", "paternity", "child", "children", "infant", "baby",
        "single parent", "divorce", "divorced", "separated", "widowed",
        "widow", "widower", "guardian", "custody", "family member",
        "dependent", "caregiver", "carer", "foster",
    ],

    # --- GDPR Art. 9(1): Financial hardship ---
    # (Intersects with social protection data and can reveal ethnic/social origin)
    "financial_hardship": [
        "debt", "debts", "indebted", "bankruptcy", "bankrupt", "insolvent",
        "insolvency", "unemployed", "unemployment", "jobless", "evicted",
        "eviction", "homeless", "homelessness", "foreclosure", "repossession",
        "benefit", "welfare", "social assistance", "food bank",
        "financial difficulty", "financial hardship", "can't afford", "cannot afford",
        "low income", "poverty", "broke", "overdue", "bailiff",
    ],

    # --- GDPR Art. 9(1): Racial or ethnic origin ---
    "racial_ethnic_origin": [
        "race", "racial", "ethnicity", "ethnic", "nationality", "national origin",
        "minority", "indigenous", "roma", "traveller", "migrant",
    ],

    # --- GDPR Art. 9(1): Religious or philosophical beliefs ---
    "religion_beliefs": [
        "religion", "religious", "faith", "belief", "beliefs", "church",
        "mosque", "synagogue", "temple", "pray", "prayer", "muslim",
        "christian", "jewish", "hindu", "buddhist", "atheist", "agnostic",
        "halal", "kosher", "sabbath", "ramadan",
    ],

    # --- GDPR Art. 9(1): Political opinions ---
    "political_opinions": [
        "political", "politics", "party membership", "political party",
        "activist", "protest", "demonstration", "union", "trade union",
        "strike", "vote", "voting", "election", "ballot",
    ],

    # --- GDPR Art. 9(1): Sexual orientation and sex life ---
    "sexual_orientation": [
        "sexual orientation", "sexuality", "gay", "lesbian", "bisexual",
        "transgender", "trans", "non-binary", "queer", "lgbtq",
        "same-sex", "homosexual", "heterosexual",
    ],

    # --- GDPR Art. 9(1): Genetic and biometric data ---
    "genetic_biometric": [
        "genetic", "genetics", "dna", "genome", "biometric",
        "fingerprint", "facial recognition", "iris scan",
    ],

    # --- Legal issues (linked to criminal convictions — GDPR Art. 10) ---
    "legal_issues": [
        "court", "courts", "criminal", "crime", "offence", "offense",
        "convicted", "conviction", "sentence", "prison", "jail", "arrest",
        "arrested", "police", "asylum", "asylum seeker", "refugee",
        "deportation", "deported", "undocumented", "illegal stay",
        "restraining order", "probation", "parole",
    ],
}

# Flat list of all keywords for fast scanning
ALL_KEYWORDS: list[str] = [
    kw for keywords in SENSITIVE_KEYWORDS.values() for kw in keywords
]


def get_matched_keywords(text: str) -> list[str]:
    """Return all sensitive keywords found in the given text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in ALL_KEYWORDS if kw in text_lower]


def get_matched_categories(text: str) -> list[str]:
    """Return the GDPR Art. 9 categories triggered by the given text."""
    text_lower = text.lower()
    return [
        category
        for category, keywords in SENSITIVE_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]
