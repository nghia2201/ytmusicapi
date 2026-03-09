from flask import Flask, request, jsonify
from ytmusicapi import YTMusic
import yt_dlp

app = Flask(__name__)

# Khởi tạo thư viện YouTube Music
ytmusic = YTMusic()

@app.route('/api/play', methods=['GET'])
def get_music_stream():
    # Nhận từ khóa từ ESP32 (Ví dụ: q=nhac+lofi+chill)
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Vui lòng cung cấp từ khóa 'q'"}), 400

    try:
        # BƯỚC 1: TÌM KIẾM TRÊN YOUTUBE MUSIC
        # Lọc kết quả chỉ lấy bài hát (songs)
        search_results = ytmusic.search(query, filter="songs")
        
        if not search_results:
            return jsonify({"error": "Không tìm thấy bài hát"}), 404
            
        # Lấy bài hát đầu tiên trong danh sách kết quả
        top_song = search_results[0]
        video_id = top_song.get('videoId')
        song_title = top_song.get('title')
        
        if not video_id:
             return jsonify({"error": "Bài hát không có VideoID"}), 404

        # BƯỚC 2: GIẢI MÃ LẤY LINK LUỒNG ÂM THANH (STREAM URL)
        # Sử dụng yt-dlp để lấy link audio chất lượng tốt nhất
        ydl_opts = {
            'format': 'bestaudio/best', # Chỉ lấy âm thanh để nhẹ mạng cho ESP32
            'quiet': True,              # Không in log lằng nhằng
            'noplaylist': True          # Chỉ lấy 1 bài, không lấy cả playlist
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(video_url, download=False)
            
            # Lấy ra cái URL gốc tàng hình của Google (Link này có thể vứt thẳng vào audio.connecttohost() của ESP32)
            stream_url = info['url'] 
            
        # BƯỚC 3: TRẢ KẾT QUẢ VỀ CHO ESP32 DƯỚI DẠNG JSON
        return jsonify({
            "status": "success",
            "title": song_title,
            "videoId": video_id,
            "streamUrl": stream_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Chạy server ở cổng 5000
    app.run(host='0.0.0.0', port=5000)