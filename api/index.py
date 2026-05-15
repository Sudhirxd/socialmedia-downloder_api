from flask import Flask, request, jsonify
import requests, re, os, shutil, time
import http.cookiejar
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import instaloader

app = Flask(__name__)

# -------------------- COMMON --------------------
def get_url_param():
    url = request.values.get("video", "").strip()
    if not url:
        return None, jsonify({"status": "error", "message": "Missing 'video' parameter", "dev": "sudhirxd.in"})
    return url, None

# -------------------- FACEBOOK --------------------
def get_fb_video(url):
    headers = {
        'User-Agent': generate_user_agent(),
        'Origin': 'https://fbdown.blog',
        'Referer': 'https://fbdown.blog/',
    }
    try:
        r = requests.post('https://fbdown.blog/get.php', headers=headers, data={'url': url}, timeout=15)
        data = r.json()['data']

        hd = sd = "Not available"
        for m in data.get("medias", []):
            if m.get("quality") == "HD":
                hd = m["url"]
            elif m.get("quality") == "SD":
                sd = m["url"]

        return {
            "status": "success",
            "video": {
                "title": data.get("title"),
                "author": data.get("author"),
                "duration": data.get("duration"),
                "thumbnail": data.get("thumbnail"),
                "hd": hd,
                "sd": sd
            },
            "dev": "sudhirxd.in"
        }
    except Exception as e:
        return {"status": "error", "message": f"Facebook error: {str(e)}", "dev": "sudhirxd.in"}

# -------------------- INSTAGRAM --------------------
def download_insta_reel(url):
    try:
        match = re.search(r'instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        if not match:
            return {"status": "error", "message": "Invalid Instagram URL", "dev": "sudhirxd.in"}

        shortcode = match.group(1)
        L = instaloader.Instaloader()

        src = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')
        tmp = '/tmp/insta.txt'
        if os.path.isfile(src):
            shutil.copy2(src, tmp)

        if os.path.isfile(tmp):
            cj = http.cookiejar.MozillaCookieJar()
            cj.load(tmp, ignore_discard=True, ignore_expires=True)
            L.context._session.cookies.update(cj)

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        return {
            "status": "success",
            "type": "video" if post.is_video else "image",
            "video": post.video_url if post.is_video else None,
            "image": post.url,
            "caption": post.caption,
            "dev": "sudhirxd.in"
        }

    except Exception as e:
        return {"status": "error", "message": f"Instagram error: {str(e)}", "dev": "sudhirxd.in"}

# -------------------- SNAPCHAT --------------------
def download_snapchat(url):
    try:
        headers = {"user-agent": generate_user_agent()}
        r = requests.post("https://www.expertstool.com/converter.php", headers=headers, data={"url": url})
        video = re.findall(r'<source[^>]+src="(https?://[^"]+)"', r.text)
        return {"status": "success", "video": video[0] if video else None, "dev": "sudhirxd.in"}
    except Exception as e:
        return {"status": "error", "message": str(e), "dev": "sudhirxd.in"}

# -------------------- PINTEREST --------------------
def get_pinterest_download_links(url):
    try:
        r = requests.post('https://www.expertstool.com/download-pinterest-video-online/', data={'url': url})
        video = re.findall(r'href="(https://v[^"]+\.mp4)"', r.text)
        return {"status": "success", "video": video[0] if video else None, "dev": "sudhirxd.in"}
    except Exception as e:
        return {"status": "error", "message": str(e), "dev": "sudhirxd.in"}

# -------------------- YOUTUBE (FIXED) --------------------
def get_youtube_video(url):
    try:
        import yt_dlp

        src = os.path.join(os.path.dirname(__file__), '..', 'ytcookies.txt')
        tmp = '/tmp/yt.txt'
        if os.path.isfile(src):
            shutil.copy2(src, tmp)

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "format": "bv*+ba/best",
            "extractor_args": {
                "youtube": {"player_client": ["android", "web"]}
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        if os.path.isfile(tmp):
            ydl_opts["cookiefile"] = tmp

        for i in range(3):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                break
            except:
                time.sleep(3)

        formats = info.get("formats", [])

        video = [f for f in formats if f.get("vcodec") != "none" and f.get("url")]
        audio = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]

        return {
            "status": "success",
            "video": {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "formats": video[-5:],
                "audio": audio[-3:]
            },
            "dev": "sudhirxd.in"
        }

    except Exception as e:
        return {"status": "error", "message": f"YouTube error: {str(e)}", "dev": "sudhirxd.in"}

# -------------------- GENERIC --------------------
def get_generic_video(url):
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({"quiet": True, "format": "best"}) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "status": "success",
            "platform": info.get("extractor_key"),
            "video": {
                "title": info.get("title"),
                "url": info.get("url")
            },
            "dev": "sudhirxd.in"
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "dev": "sudhirxd.in"}

# -------------------- ROUTES --------------------
@app.route('/fb', methods=['GET', 'POST'])
def fb():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_fb_video(url))

@app.route('/insta', methods=['GET', 'POST'])
def insta():
    url, err = get_url_param()
    if err: return err
    return jsonify(download_insta_reel(url))

@app.route('/snap', methods=['GET', 'POST'])
def snap():
    url, err = get_url_param()
    if err: return err
    return jsonify(download_snapchat(url))

@app.route('/pin', methods=['GET', 'POST'])
def pin():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_pinterest_download_links(url))

@app.route('/yt', methods=['GET', 'POST'])
def yt():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_youtube_video(url))

@app.route('/dl', methods=['GET', 'POST'])
def dl():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_generic_video(url))

# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(debug=True)
