# Security Guide (Umutekano)

## Encryption

```python
from ububiko.umutekano import EncryptionEngine, FieldEncryption

engine = EncryptionEngine()
encrypted = engine.encrypt("sensitive data")
decrypted = engine.decrypt(encrypted)
hashed = engine.hash("password")
```

## Field-Level Encryption

```python
field_enc = FieldEncryption(engine)
field_enc.encrypt_field("User", "ssn")
field_enc.encrypt_field("User", "credit_card")

value = field_enc.encrypt_value("User", "ssn", "123-45-6789")
plain = field_enc.decrypt_value("User", "ssn", value)
```

## RBAC

```python
from ububiko.umutekano import RoleBasedAccessControl

rbac = RoleBasedAccessControl()
rbac.create_role("admin", ["read", "write", "delete"])
rbac.create_role("viewer", ["read"])
rbac.assign_role("user1", "admin")

rbac.assert_permission("user1", "delete")  # OK
rbac.has_permission("viewer1", "write")     # False
```

## Audit Logging

```python
from ububiko.umutekano import AuditLogger

logger = AuditLogger(storage=adapter)
logger.log("admin", "DELETE", "users", resource_id="42")

entries = logger.get_by_user("admin")
```

## Data Masking

```python
from ububiko.umutekano import DataMasker

masked_email = DataMasker.mask_email("user@example.com")      # use***@example.com
masked_phone = DataMasker.mask_phone("+250-788-123-456")       # ***********3456
masked_cc = DataMasker.mask_credit_card("4111-1111-1111-1111") # ****-****-****-1111
```

## Compliance

```python
from ububiko.umutekano import ComplianceChecker

gdpr = ComplianceChecker.gdpr_rules()
results = gdpr.check({"has_consent": True, "fields": ["name", "email"], "retention_days": 90})
```
