import json
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import current_user

import db
from utils import database


bp = Blueprint("home", __name__)


@bp.route("/", methods=["GET"])
def home():
    """
    Render home page

    """
    try:
        with open(current_app.config["THEME_DIR"], "r") as f:
            data = json.load(f)
            formatted_font = data["font_family"].replace(" ", "+")
            return render_template("index.html", icon=data["icon"], formated_font=formatted_font,
                                   font_family=data["font_family"], name_font_family=data["name_font_family"])
    except FileNotFoundError as e:
        return jsonify({"ERROR": e})


@bp.route("/theme", methods=["GET"])
def theme():
    """
    Returns theme JSON object

    Returns (JSON): theme JSON object
    """
    try:
        with open(current_app.config["THEME_DIR"], "r") as f:
            data = json.load(f)
        return jsonify({"theme": data})
    except FileNotFoundError as e:
        return jsonify({"ERROR": e})


@bp.route("/top_k", methods=["GET"])
def top_k():
    """
    Returns the top k latest entries in the database

    Returns (JSON): a list of top k entries

    """
    db_conn = db.get_db()
    k = request.args.get("k")
    top_ks = database.get_top_k_entries(db_conn, int(k))
    db_conn.close()
    return jsonify({"top_k": top_ks})


@bp.route("/public_repos", methods=["GET"])
def public_repos():
    """
    List all public repos from github

    Returns (JSON): a list of repos and updated timestamp

    """
    db_conn = db.get_db()
    if request.method == "GET":
        repos, updated = database.get_public_repos(db_conn)
        db_conn.close()
        return jsonify({"repos": repos, "updated": updated})


@bp.route("/blogs", methods=["GET", "POST"])
def blogs():
    """
    GET or POST blogs

    Returns (JSON): GET  -> a list of all blogs
                    POST -> INFO message

    """
    db_conn = db.get_db()
    if request.method == "GET":
        all_blogs, updated = database.get_articles(db_conn)
        db_conn.close()
        return jsonify({"blogs": all_blogs, "updated": updated})
    if current_user.is_authenticated:
        title = request.json["title"]
        description = request.json["description"]
        url = request.json["url"]
        image_url = request.json["image_url"]
        time_stamp = request.json["time_stamp"] + " 00:00:00"
        database.add_entry("blogs", db_conn, title, description, url, image_url, time_stamp)
        db_conn.close()
        return jsonify({"INFO": "Blog added"})
    return jsonify({"ERROR": "Unauthenticated"})


@bp.route("/publications", methods=["GET", "POST"])
def publications():
    """
    GET or POST publications

    Returns (JSON): GET  -> a list of all publications
                    POST -> INFO message

    """
    db_conn = db.get_db()
    if request.method == "GET":
        all_blogs = database.get_entries("publications", db_conn)
        db_conn.close()
        return jsonify({"publications": all_blogs})
    if current_user.is_authenticated:
        title = request.json["title"]
        description = request.json["description"]
        url = request.json["url"]
        image_url = request.json["image_url"]
        time_stamp = request.json["time_stamp"] + " 00:00:00"
        database.add_entry("publications", db_conn, title, description, url, image_url, time_stamp)
        db_conn.close()
        return jsonify({"INFO": "Publication added"})
    return jsonify({"ERROR": "Unauthenticated"})
