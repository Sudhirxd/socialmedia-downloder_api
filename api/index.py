from flask import Flask, request, jsonify
import requests
import re
import os
import http.cookiejar
from bs4 import BeautifulSoup
import html as html_lib
from user_agent import generate_user_agent
import instaloader

app = Flask(__name__)


def get_fb_video(url):
    headers = {
        'User-Agent': generate_user_agent(),
        'Origin': 'https://fbdown.blog',
        'Referer': 'https://fbdown.blog/',
    }
    try:
        r = requests.post('https://fbdown.blog/get.php', headers=headers, data={'url': url}, timeout=15)
        data = r.json()['data']
        title = data.get("title", "Unknown Title")
        author = data.get("author", "Unknown Author")
        duration_sec = data.get("duration", 0)
        thumbnail = data.get("thumbnail", "")
        mins = int(duration_sec // 60)
        secs = int(duration_sec % 60)
        duration_str = f"{mins:02d}:{secs:02d}"
        hd = sd = "Not available"
        for m in data.get("medias", []):
            if m.get("quality") == "HD":
                hd = m["url"]
            elif m.get("quality") == "SD" and sd == "Not available":
                sd = m["url"]
        return {
            "status": "success",
            "video": {
                "title": title,
                "author": author,
                "duration": duration_str,
                "thumbnail": thumbnail,
                "hd": hd,
                "sd": sd
            },
            "dev": "sudhirxd.in"
        }
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out", "dev": "sudhirxd.in"}
    except (KeyError, ValueError):
        return {"status": "error", "message": "Unexpected response format", "dev": "sudhirxd.in"}
    except Exception as e:
        return {"status": "error", "message": f"Facebook video not found: {str(e)}", "dev": "sudhirxd.in"}


def download_insta_reel(url):
    try:
        match = re.search(r'instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        if not match:
            return {"status": "error", "message": "Invalid Instagram URL", "dev": "sudhirxd.in"}
        shortcode = match.group(1)

        L = instaloader.Instaloader()

        # Load cookies.txt — copy to /tmp first (Vercel read-only fs)
        src_cookies = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')
        tmp_cookies = '/tmp/insta_cookies.txt'
        if os.path.isfile(src_cookies) and not os.path.isfile(tmp_cookies):
            import shutil
            shutil.copy2(src_cookies, tmp_cookies)
        if os.path.isfile(tmp_cookies):
            cj = http.cookiejar.MozillaCookieJar()
            cj.load(tmp_cookies, ignore_discard=True, ignore_expires=True)
            L.context._session.cookies.update(cj)

        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if not post.is_video:
            return {
                "status": "success",
                "type": "image",
                "image": post.url,
                "caption": post.caption or "",
                "dev": "sudhirxd.in"
            }
        return {
            "status": "success",
            "type": "video",
            "video": post.video_url,
            "thumbnail": post.url,
            "caption": post.caption or "",
            "views": post.video_view_count,
            "dev": "sudhirxd.in"
        }
    except instaloader.exceptions.InstaloaderException as e:
        return {"status": "error", "message": f"Reel not found or private: {str(e)}", "dev": "sudhirxd.in"}
    except Exception as e:
        return {"status": "error", "message": f"Instagram request failed: {str(e)}", "dev": "sudhirxd.in"}


def _clean_link(link):
    if not link:
        return None
    link = link.replace("\\u0026", "&").replace("&quot;", "").strip()
    return link.split(",mediaPreviewUrl:")[0].rstrip("&")


def download_snapchat(url):
    headers = {
        "authority": "www.expertstool.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.expertstool.com",
        "referer": "https://www.expertstool.com/snapchat-video-downloader/",
        "user-agent": generate_user_agent()
    }
    try:
        response = requests.post("https://www.expertstool.com/converter.php", headers=headers, data={"url": url}, timeout=20)
        html = response.text
        video_links = [_clean_link(v) for v in re.findall(r'<source[^>]+src="(https?://[^"]+)"', html) if _clean_link(v)]
        image_links = list(set([
            _clean_link(i[1]) for i in re.findall(r'(poster|src)="(https?://[^"]+)"', html)
            if _clean_link(i[1]) and '.mp4' not in i[1].lower()
        ]))
        if video_links or image_links:
            return {
                "status": "success",
                "video": video_links[0] if video_links else None,
                "image": image_links[0] if image_links else None,
                "dev": "sudhirxd.in"
            }
        return {"status": "error", "message": "Invalid Snapchat URL", "dev": "sudhirxd.in"}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out", "dev": "sudhirxd.in"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch Snapchat data: {str(e)}", "dev": "sudhirxd.in"}


def get_pinterest_download_links(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'origin': 'https://www.expertstool.com',
        'referer': 'https://www.expertstool.com/download-pinterest-video-online/',
        'user-agent': generate_user_agent(),
    }
    try:
        response = requests.post('https://www.expertstool.com/download-pinterest-video-online/', headers=headers, data={'url': url}, timeout=20)
        html = response.text
        if "API Not Work" in html or "Invalid" in html:
            return {"status": "error", "message": "Invalid Pinterest URL", "dev": "sudhirxd.in"}
        soup = BeautifulSoup(html, 'html.parser')
        for btn in soup.find_all('a', class_=re.compile(r'btn.*primary')):
            href = btn.get('href', '')
            if href.startswith('https://v') and '.mp4' in href:
                return {"status": "success", "video": href, "dev": "sudhirxd.in"}
        for img in soup.find_all('a', href=re.compile(r'pinimg\.com.*originals')):
            return {"status": "success", "photo": img['href'], "dev": "sudhirxd.in"}
        return {"status": "error", "message": "No media found", "dev": "sudhirxd.in"}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out", "dev": "sudhirxd.in"}
    except Exception as e:
        return {"status": "error", "message": f"Pinterest request failed: {str(e)}", "dev": "sudhirxd.in"}


def get_url_param():
    url = request.values.get("video", "").strip()
    if not url:
        return None, jsonify({"status": "error", "message": "Missing 'video' parameter", "dev": "sudhirxd.in"})
    return url, None


@app.route('/fb', methods=['GET', 'POST'])
@app.route('/api/fb', methods=['GET', 'POST'])
def fb():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_fb_video(url))


@app.route('/insta', methods=['GET', 'POST'])
@app.route('/api/insta', methods=['GET', 'POST'])
def insta():
    url, err = get_url_param()
    if err: return err
    return jsonify(download_insta_reel(url))


@app.route('/snap', methods=['GET', 'POST'])
@app.route('/api/snap', methods=['GET', 'POST'])
def snap():
    url, err = get_url_param()
    if err: return err
    return jsonify(download_snapchat(url))


@app.route('/pin', methods=['GET', 'POST'])
@app.route('/api/pin', methods=['GET', 'POST'])
def pin():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_pinterest_download_links(url))


def get_youtube_video(url):
    try:
        import yt_dlp
        # Copy cookies to /tmp (only writable dir on Vercel)
        src_cookies = os.path.join(os.path.dirname(__file__), '..', 'ytcookies.txt')
        tmp_cookies = '/tmp/ytcookies.txt'
        if os.path.isfile(src_cookies) and not os.path.isfile(tmp_cookies):
            import shutil
            shutil.copy2(src_cookies, tmp_cookies)

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
            'noplaylist': True,
            'no_cache_dir': True,
            'cachedir': False,
        }
        if os.path.isfile(tmp_cookies):
            ydl_opts['cookiefile'] = tmp_cookies
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            author = info.get('uploader', 'Unknown Author')
            duration_sec = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
            mins = int(duration_sec // 60)
            secs = int(duration_sec % 60)
            duration_str = f"{mins:02d}:{secs:02d}"

            # Get best video+audio, 720p, 360p separately
            formats = info.get('formats', [])

            # Sort formats by quality
            video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('url')]
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url')]

            def best_by_height(h):
                # exact match first, then closest
                exact = [f for f in video_formats if f.get('height') == h]
                if exact:
                    return exact[-1]['url']
                below = [f for f in video_formats if (f.get('height') or 0) <= h]
                if below:
                    return sorted(below, key=lambda f: f.get('height') or 0)[-1]['url']
                return video_formats[-1]['url'] if video_formats else 'Not available'

            hd = best_by_height(720)
            sd = best_by_height(360)
            audio = audio_formats[-1]['url'] if audio_formats else 'Not available'

            return {
                "status": "success",
                "video": {
                    "title": title,
                    "author": author,
                    "duration": duration_str,
                    "thumbnail": thumbnail,
                    "hd": hd,
                    "sd": sd,
                    "audio": audio
                },
                "dev": "sudhirxd.in"
            }
    except Exception as e:
        return {"status": "error", "message": f"YouTube fetch failed: {str(e)}", "dev": "sudhirxd.in"}




def get_generic_video(url):
    try:
        import yt_dlp, shutil
        src_cookies = os.path.join(os.path.dirname(__file__), '..', 'ytcookies.txt')
        tmp_cookies = '/tmp/ytcookies.txt'
        if os.path.isfile(src_cookies) and not os.path.isfile(tmp_cookies):
            shutil.copy2(src_cookies, tmp_cookies)

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
            'noplaylist': True,
            'no_cache_dir': True,
            'cachedir': False,
        }
        if os.path.isfile(tmp_cookies):
            ydl_opts['cookiefile'] = tmp_cookies

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            author = info.get('uploader') or info.get('channel') or info.get('creator', 'Unknown Author')
            duration_sec = info.get('duration', 0) or 0
            thumbnail = info.get('thumbnail', '')
            mins = int(duration_sec // 60)
            secs = int(duration_sec % 60)
            duration_str = f"{mins:02d}:{secs:02d}"
            formats = info.get('formats', [])

            # Sort formats by quality
            video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('url')]
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url')]

            def best_by_height(h):
                # exact match first, then closest
                exact = [f for f in video_formats if f.get('height') == h]
                if exact:
                    return exact[-1]['url']
                below = [f for f in video_formats if (f.get('height') or 0) <= h]
                if below:
                    return sorted(below, key=lambda f: f.get('height') or 0)[-1]['url']
                return video_formats[-1]['url'] if video_formats else 'Not available'

            hd = best_by_height(720)
            sd = best_by_height(360)
            audio = audio_formats[-1]['url'] if audio_formats else 'Not available'

            return {
                "status": "success",
                "platform": info.get('extractor_key', 'Unknown'),
                "video": {
                    "title": title,
                    "author": author,
                    "duration": duration_str,
                    "thumbnail": thumbnail,
                    "hd": hd,
                    "sd": sd,
                    "audio": audio
                },
                "dev": "sudhirxd.in"
            }
    except Exception as e:
        return {"status": "error", "message": f"Download failed: {str(e)}", "dev": "sudhirxd.in"}

@app.route('/yt', methods=['GET', 'POST'])
@app.route('/api/yt', methods=['GET', 'POST'])
def yt():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_youtube_video(url))


@app.route('/dl', methods=['GET', 'POST'])
@app.route('/api/dl', methods=['GET', 'POST'])
def dl():
    url, err = get_url_param()
    if err: return err
    return jsonify(get_generic_video(url))
