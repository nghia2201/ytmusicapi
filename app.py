from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "ytmusic api is running",
        "routes": [
            "/",
            "/health",
            "/api/play?q=<song_name>"
        ]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/play", methods=["GET"])
def play_song():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Missing query parameter q"}), 400

    search_query = f"ytsearch1:{query}"

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "extract_flat": False,
        "skip_download": True,
        "default_search": "ytsearch",
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

            if not info or "entries" not in info or not info["entries"]:
                return jsonify({"error": "No song found"}), 404

            entry = info["entries"][0]

            title = entry.get("title", "Unknown")
            video_id = entry.get("id", "")
            stream_url = entry.get("url", "")

            if not stream_url:
                return jsonify({"error": "No stream URL found"}), 500

            return jsonify({
                "status": "success",
                "title": title,
                "videoId": video_id,
                "streamUrl": stream_url
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
