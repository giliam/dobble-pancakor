import math
import os
import pathlib

import flask
import json

from src.db import get_db
from src.script import build_cards, check_validity

bp = flask.Blueprint("dobble", __name__)

AUTHORIZED_EXT = ["jpg", "jpeg", "png", "gif", "jfif"]

RADIUS = 500
POSITION_IMAGE_RADIUS = 0.55


@bp.route("/", methods=["POST", "GET"])
def homepage():
    if flask.request.method == "POST":
        db = get_db()

        nb_elements = int(flask.request.form["n"])
        uploaded_files = flask.request.files.getlist("file[]")

        nb_files = len(list(pathlib.Path("src/static/").glob("*")))

        files = []
        for image in uploaded_files:
            extension = image.filename.split(".")[-1]
            if not extension in AUTHORIZED_EXT:
                continue
            nb_files += 1
            filename = "%d.%s" % (nb_files, extension)
            image.save("src/static/" + filename)
            files.append(filename)

        cards = build_cards(nb_elements - 1)
        nb_errors = check_validity(cards)
        if nb_errors > 0:
            flask.current_app.logger.warning("Errors in card generation.")
        else:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO game (pictures, cards) VALUES (?, ?)",
                (json.dumps(files), json.dumps(cards)),
            )
            db.commit()
            id_game = cursor.lastrowid
            return flask.redirect(flask.url_for("dooble.display", id_game=id_game))
    return flask.render_template("generator.html", number_symbols=(4, 6, 8, 12, 14))


def get_positions_cards(nb_sym_per_card):
    if nb_sym_per_card <= 0:
        raise ValueError("Should be at least one symbol per card")
    positions = []
    for i in range(nb_sym_per_card):
        positions.append(
            {
                "x": RADIUS
                * POSITION_IMAGE_RADIUS
                * math.cos(i * math.pi * 2.0 / nb_sym_per_card)
                + RADIUS,
                "y": RADIUS
                * POSITION_IMAGE_RADIUS
                * math.sin(i * math.pi * 2.0 / nb_sym_per_card)
                + RADIUS,
            }
        )
    return positions


def get_max_width_cards(nb_sym_per_card):
    if nb_sym_per_card <= 0:
        raise ValueError("Should be at least one symbol per card")
    x0 = POSITION_IMAGE_RADIUS * RADIUS
    print("x0", x0)
    # the idea here is that we draw the inner circle gathering all the centers
    # from the pictures. This circle has a radius of x0. It cuts all pictures
    # in their center and in another point x1. The length between x1 and x0 is
    # the maximal radius of circles. To compute this length, we just have to study
    # the isocele triangle between the center of the main circle, x0 and x1.
    theta = math.pi * 2.0 / nb_sym_per_card
    print("theta", theta)

    # We cut this triangle in two
    max_radius = min(x0 * math.sin(theta / 4.0) * 2.0, RADIUS - x0)
    print("max_radius", max_radius)
    max_width = math.sqrt(2.0) * max_radius
    print("max_width", max_width)
    return max_width


def add_id_to_picture(pictures):
    return [{"id": i, "pic": pic} for i, pic in enumerate(pictures)]


@bp.route("/display/<int:id_game>", methods=["GET"])
def display(id_game):
    db = get_db()
    game = db.execute("SELECT * FROM game WHERE id = ?", (id_game,)).fetchone()
    if game is not None:
        try:
            cards = json.loads(game["cards"])
            pictures = json.loads(game["pictures"])
        except json.decoder.JSONDecodeError:
            return flask.redirect(flask.url_for("homepage"))
        nb_sym_per_card = len(cards[0])
        positions = get_positions_cards(nb_sym_per_card)
        pictures = add_id_to_picture(pictures)
        return flask.render_template(
            "display.html",
            cards=cards,
            pictures=pictures,
            positions=positions,
            radius=RADIUS,
            position_radius=POSITION_IMAGE_RADIUS,
            max_width=get_max_width_cards(nb_sym_per_card),
        )
    else:
        return flask.redirect(flask.url_for("homepage"))
