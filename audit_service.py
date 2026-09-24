import uuid
from datetime import datetime
from typing import List, Optional
from models import AuditLogEntry, ConfidenceLevel

# In-memory append-only audit trail
AUDIT_LEDGER: List[AuditLogEntry] = []

def record_audit_event(
    event_type: str,
    task_title: str,
    target_employee_id: Optional[str] = None,
    ai_confidence: Optional[ConfidenceLevel] = None,
    details: Optional[dict] = None,
    manager_decision: Optional[str] = None
) -> AuditLogEntry:
    """Appends an immutable audit event to the system ledger."""
    entry = AuditLogEntry(
        log_id=f"AUDIT-{str(uuid.uuid4())[:8].upper()}",
        timestamp=datetime.now(),
        event_type=event_type,
        task_title=task_title,
        target_employee_id=target_employee_id,
        ai_confidence=ai_confidence,
        details=details or {},
        manager_decision=manager_decision
    )
    AUDIT_LEDGER.append(entry)
    return entry

def get_audit_logs() -> List[AuditLogEntry]:
    """Retrieves all logged system events in reverse chronological order."""
    return sorted(AUDIT_LEDGER, key=lambda x: x.timestamp, reverse=True)
    