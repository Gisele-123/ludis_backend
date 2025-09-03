from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name  = db.Column(db.String(80), nullable=False)
    email      = db.Column(db.String(255), unique=True, index=True, nullable=False)
    phone      = db.Column(db.String(32), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def to_safe_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "is_email_verified": self.is_email_verified,
            "created_at": self.created_at.isoformat(),
        }

class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "created_at": self.created_at.isoformat()}

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, default="two_teams")  
    # Possible values: "two_teams", "personal", "multi_team"
    
    home_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)
    away_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)

    # For personal/multi-team games, you can store participants as JSON
    participants = db.Column(db.JSON, nullable=True)

    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="scheduled")  # scheduled/live/finished
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "home_team_id": self.home_team_id,
            "away_team_id": self.away_team_id,
            "participants": self.participants,
            "date": self.date.isoformat(),
            "status": self.status,
            "home_score": self.home_score,
            "away_score": self.away_score
        }

