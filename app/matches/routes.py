from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Team, Match
from datetime import datetime
from ..auth.utils import admin_required

matches_bp = Blueprint("matches", __name__)

@matches_bp.post("/teams")
@admin_required
def create_team():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"message": "Team name required"}), 400

    if Team.query.filter_by(name=name).first():
        return jsonify({"message": "Team already exists"}), 409

    team = Team(name=name)
    db.session.add(team)
    db.session.commit()
    return jsonify({"team": team.to_dict()}), 201
    pass

@matches_bp.post("/matches")
@admin_required
def create_match():
    data = request.json
    match_type = data.get("type", "two_teams")
    sport_type = data.get("sport_type")  # required now
    date = data.get("date")

    if not sport_type:
        return jsonify({"message": "sport_type is required"}), 400

    if match_type not in ["two_teams", "personal", "multi_team"]:
        return jsonify({"message": "Invalid match type"}), 400

    if match_type == "two_teams":
        home_team_id = data.get("home_team_id")
        away_team_id = data.get("away_team_id")
        if not home_team_id or not away_team_id:
            return jsonify({"message": "Two-team match must have home_team_id and away_team_id"}), 400
        match = Match(
            type="two_teams",
            sport_type=sport_type,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            date=date
        )
    else:
        participants = data.get("participants")
        if not participants or not isinstance(participants, list):
            return jsonify({"message": "Personal or multi_team match must have participants list"}), 400
        match = Match(
            type=match_type,
            sport_type=sport_type,
            participants=participants,
            date=date
        )

    db.session.add(match)
    db.session.commit()
    return jsonify(match.to_dict()), 201

@matches_bp.patch("/matches/<int:match_id>/score")
@admin_required
def update_score(match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"message": "Match not found"}), 404

    data = request.json

    if match.type == "two_teams":
        match.home_score = data.get("home_score", match.home_score)
        match.away_score = data.get("away_score", match.away_score)
    else:
        # Personal or multi-team scores stored in JSON: {"player1": 10, "player2": 8}
        scores = data.get("scores")
        if not scores or not isinstance(scores, dict):
            return jsonify({"message": "Scores must be provided as a JSON object"}), 400
        match.home_score = None
        match.away_score = None
        match.participants = [{"name": p, "score": s} for p, s in scores.items()]

    match.status = data.get("status", match.status)
    db.session.commit()
    return jsonify(match.to_dict()), 200

@matches_bp.get("/teams")
def list_teams():
    teams = Team.query.order_by(Team.name).all()
    return jsonify([t.to_dict() for t in teams]), 200

@matches_bp.get("/teams/<int:team_id>")
def get_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"message": "Team not found"}), 404
    return jsonify(team.to_dict()), 200

@matches_bp.get("/matches")
def list_matches():
    matches = Match.query.order_by(Match.date.desc()).all()
    return jsonify([m.to_dict() for m in matches]), 200

@matches_bp.get("/matches/<int:match_id>")
def get_match(match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({"message": "Match not found"}), 404
    return jsonify(match.to_dict()), 200

@matches_bp.get("/matches/status/<status>")
def get_matches_by_status(status):
    status = status.lower()
    if status not in ["scheduled", "live", "finished"]:
        return jsonify({"message": "Invalid status"}), 400
    matches = Match.query.filter_by(status=status).order_by(Match.date.asc()).all()
    return jsonify([m.to_dict() for m in matches]), 200

@matches_bp.get("/matches/team/<int:team_id>")
def get_matches_by_team(team_id):
    matches = Match.query.filter(
        (Match.home_team_id==team_id) | (Match.away_team_id==team_id)
    ).order_by(Match.date.desc()).all()
    return jsonify([m.to_dict() for m in matches]), 200
