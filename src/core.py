import flask
import pathlib
import json

from src.db import get_db
from src.script import build_cards, check_validity

bp = flask.Blueprint("dobble", __name__)


@bp.route("/", methods=["POST", "GET"])
def homepage():
    if flask.request.method == "POST":
        db = get_db()

        nb_elements = int(flask.request.form["n"])
        uploaded_files = flask.request.files.getlist("file[]")

        nb_files = len(list(pathlib.Path("upload/").glob("*")))

        files = []
        for image in uploaded_files:
            nb_files += 1
            filename = "%d.%s" % (nb_files, image.filename.split(".")[-1])
            image.save("upload/" + filename)
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


@bp.route("/display/<int:id_game>", methods=["GET"])
def display(id_game):
    db = get_db()
    game = db.execute("SELECT * FROM game WHERE id = ?", (id_game,)).fetchone()
    if game is not None:
        return flask.render_template(
            "display.html", cards=game["cards"], pictures=game["pictures"]
        )
    else:
        return flask.redirect(flask.url_for("homepage"))
