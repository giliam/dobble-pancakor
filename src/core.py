import io
import math
import os
import pathlib
from PIL import Image
import random

import flask
import json

from src.db import get_db
from src.script import build_cards, check_validity
from src.place import generate_card

bp = flask.Blueprint("dobble", __name__)

AUTHORIZED_EXT = ["jpg", "jpeg", "png", "gif", "jfif"]

RADIUS = 500
POSITION_IMAGE_RADIUS = 0.55
MIN_SIZE_CARD = 0.5  # In %
MAX_SIZE_CARD = 1.30  # In %


@bp.route("/", methods=["POST", "GET"])
def homepage():
    if flask.request.method == "POST":
        db = get_db()

        nb_elements = int(flask.request.form["n"])
        uploaded_files = flask.request.files.getlist("file[]")

        nb_files = len(list(pathlib.Path("src/static/").glob("*")))

        files = []
        files_sizes = []
        for image in uploaded_files:
            extension = image.filename.split(".")[-1]
            if not extension in AUTHORIZED_EXT:
                continue
            nb_files += 1

            filename = "%d.%s" % (nb_files, extension)
            # image.save("src/static/" + filename)

            image_bytes = io.BytesIO(image.stream.read())
            # save bytes in a buffer

            img = Image.open(image_bytes)
            img.save("src/static/" + filename)
            # produces a PIL Image object

            size = img.size

            # read the size of the Image object
            files.append(filename)
            files_sizes.append(size)

        cards = build_cards(nb_elements - 1)
        nb_errors = check_validity(cards)
        if nb_errors > 0:
            flask.current_app.logger.warning("Errors in card generation.")
        else:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO game (pictures, cards, sizes) VALUES (?, ?, ?)",
                (json.dumps(files), json.dumps(cards), json.dumps(files_sizes)),
            )
            db.commit()
            id_game = cursor.lastrowid
            return flask.redirect(flask.url_for("dobble.display", id_game=id_game))
    return flask.render_template("generator.html", number_symbols=(4, 6, 8, 12, 14))


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


def get_positions(cards, nb_sym_per_card, max_width, files_sizes):
    if nb_sym_per_card <= 0:
        raise ValueError("Should be at least one symbol per card")
    if max_width <= 0:
        raise ValueError("Max Width should be positive")

    max_size_rec = max_width / RADIUS * 0.85
    min_size_rec = 0.01 * max_size_rec

    positions = []
    output_sizes = []

    nb_cards = len(cards)

    print("nb_sym_per_card", nb_sym_per_card)
    print("min_size_rec", min_size_rec)
    print("max_size_rec", max_size_rec)

    for card in cards:
        new_sizes = []
        old_sizes = []
        for picture in card:
            new_sizes.append(
                (picture, files_sizes[picture][1] / files_sizes[picture][0])
            )
        random.shuffle(new_sizes)

        placed_rectangles = generate_card(
            nb_sym_per_card, new_sizes, min_size_rec, max_size_rec
        )
        positions.append(
            {
                id_pic: {
                    "x": rec.pos[0] * RADIUS + RADIUS,
                    "y": rec.pos[1] * RADIUS + RADIUS,
                }
                for id_pic, rec in placed_rectangles.items()
            }
        )
        output_sizes.append(
            {
                id_pic: (rec.size * RADIUS, rec.size * rec.ratio * RADIUS)
                for id_pic, rec in placed_rectangles.items()
            }
        )
    return positions, output_sizes


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
            sizes = json.loads(game["sizes"])
        except json.decoder.JSONDecodeError:
            return flask.redirect(flask.url_for("homepage"))

        nb_sym_per_card = len(cards[0])
        pictures = add_id_to_picture(pictures)
        max_width = get_max_width_cards(nb_sym_per_card)
        positions, sizes = get_positions(cards, nb_sym_per_card, max_width, sizes)

        return flask.render_template(
            "display.html",
            cards=cards,
            pictures=pictures,
            positions=positions,
            radius=RADIUS,
            position_radius=POSITION_IMAGE_RADIUS,
            max_width=max_width,
            sizes=sizes,
        )
    else:
        return flask.redirect(flask.url_for("homepage"))
