
DOMAIN_CONTEXTS = {
    "telecom": """
- Missing business rules, regulatory conditions, or billing logic (e.g., BRM, CRM, Mediation, OCS)
- Weak differentiation between **prepaid and postpaid** logic
- Missing data export, reporting, or **auditing/logging mechanisms**
- Privacy/security compliance issues (e.g., MSISDN masking, lawful intercept)
- Incomplete validation of telecom regulatory mandates such as DND enforcement, consent capture, or emergency service compliance.
""",
    
    "fintech": """
- Gaps in transaction integrity, rollback, or idempotency mechanisms
- Missing fraud detection, AML/KYC compliance logic
- Absence of retry logic for payment gateway/API failures
- No handling of race conditions or concurrent transaction risks
- Missing regulatory reporting (e.g., RBI, SEBI, PCI-DSS)
- Inadequate security enforcement (e.g., encryption at rest/in transit, token masking)
- Missing financial audit trails, reconciliation logic, or ledger posting accuracy
- Lack of SLA-based error/failure handling (e.g., payment timeouts, chargebacks)
"""
}
