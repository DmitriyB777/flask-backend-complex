from ..extensions import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID

class TokenBlockList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(UUID(as_uuid=True), nullable=False, unique=True)
    create_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))