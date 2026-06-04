from flask import Flask, render_template, request, send_from_directory
from demoparser2 import DemoParser
import tempfile
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():

    return render_template("index.html")


@app.route("/parse", methods=["POST"])
def parse_demo():

    file = request.files.get("demo")

    if not file:

        return """
        <div class="error">
            No file selected
        </div>
        """

    if not file.filename.lower().endswith(".dem"):

        return """
        <div class="error">
            Invalid file type
        </div>
        """

    temp_path = None

    try:

        # TEMP FILE
        # Exists only while parsing

        temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".dem"
        )

        temp_path = temp.name

        file.save(temp_path)

        # Parse demo

        parser = DemoParser(temp_path)

        round_end = parser.parse_event(
            "round_end"
        )

        if len(round_end) == 0:

            return """
            <div class="error">
                Failed to parse demo
            </div>
            """

        last_tick = (
            round_end["tick"]
            .to_list()[-1]
        )

        df = parser.parse_ticks(
            [
                "name",
                "steamid",
                "crosshair_code",

                "CCSPlayerPawn.m_flViewmodelFOV",
                "CCSPlayerPawn.m_flViewmodelOffsetX",
                "CCSPlayerPawn.m_flViewmodelOffsetY",
                "CCSPlayerPawn.m_flViewmodelOffsetZ",
                "CCSPlayerPawn.m_bLeftHanded"
            ],
            ticks=[last_tick]
        )

        players = []

        seen = set()

        # Works with pandas

        rows = df.to_dict(
            orient="records"
        )

        for row in rows:

            steamid = str(
                row.get("steamid")
            )

            if not steamid:
                continue

            if steamid in seen:
                continue

            seen.add(steamid)

            players.append({

                "name":
                    row.get("name")
                    or "Unknown",

                "steamid":
                    steamid,

                "crosshair":
                    row.get("crosshair_code")
                    or "No crosshair found",

                "fov":
                    row.get(
                        "CCSPlayerPawn.m_flViewmodelFOV"
                    ),

                "x":
                    row.get(
                        "CCSPlayerPawn.m_flViewmodelOffsetX"
                    ),

                "y":
                    row.get(
                        "CCSPlayerPawn.m_flViewmodelOffsetY"
                    ),

                "z":
                    row.get(
                        "CCSPlayerPawn.m_flViewmodelOffsetZ"
                    ),

                "lefthand":
                    row.get(
                        "CCSPlayerPawn.m_bLeftHanded"
                    )
            })

        return render_template(
            "players.html",
            players=players
        )

    except Exception as e:

        print(e)

        return f"""
        <div class="error">
            Failed to parse demo
        </div>
        """

    finally:

        # DELETE TEMP FILE

        if (
            temp_path and
            os.path.exists(temp_path)
        ):

            try:
                os.remove(temp_path)
            except:
                pass

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

