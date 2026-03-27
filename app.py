from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import urllib.parse

app = Flask(__name__)

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
