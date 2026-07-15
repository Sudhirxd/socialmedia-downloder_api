from flask import Flask, request, jsonify
import requests
import re
import random
from bs4 import BeautifulSoup
import html as html_lib
from user_agent import generate_user_agent

app = Flask(__name__)

def get_fb_video(url):
    headers = {
        'User-Agent': generate_user_agent(),
        'Origin': 'https://fbdown.blog',
        'Referer': 'https://fbdown.blog/',
    }
    try:
        r = requests.post('https://fbdown.blog/get.php', headers=headers, data={'url': url}, timeout=15)
        raw = r.text.replace('\\/', '/')
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
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        }
    except:
        return {
            "status": "error",
            "message": "Facebook video not found",
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        }

def download_insta_reel(url):
    try:
        session = requests.Session()
        ua = generate_user_agent()
        headers_get = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        page_url = 'https://snapdownloader.com/tools/instagram-reels-downloader/download'
        r_get = session.get(page_url, headers=headers_get, timeout=20)
        if r_get.status_code != 200:
            return {"status": "error", "message": f"Initial page fetch failed: {r_get.status_code}"}
            
        soup = BeautifulSoup(r_get.text, 'html.parser')
        csrf_meta = soup.find('meta', attrs={'name': 'csrf-token'})
        if not csrf_meta:
            return {"status": "error", "message": "CSRF token not found"}
        csrf_token = csrf_meta.get('content')
        
        api_url_meta = soup.find('meta', attrs={'name': 'api-fetch-url'})
        api_url = api_url_meta.get('content') if api_url_meta else 'https://grabgram.io/api/fetch/instagram'
        
        # Dynamically detect tool type
        url_lower = url.lower()
        if 'stories/highlights' in url_lower or '/highlights/' in url_lower:
            tool = 'highlights'
        elif '/stories/' in url_lower:
            tool = 'stories'
        elif '/reel/' in url_lower or '/tv/' in url_lower:
            tool = 'reels'
        elif '/p/' in url_lower:
            tool = 'video'
        else:
            match = re.search(r'instagram\.com/([a-zA-Z0-9_\.]+)', url)
            if match:
                username = match.group(1)
                if username not in ['p', 'reel', 'stories', 'tv', 'developer', 'about', 'explore']:
                    tool = 'profile'
                else:
                    tool = 'reels'
            else:
                tool = 'reels'
        
        headers_post = {
            'User-Agent': ua,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://grabgram.io',
            'Referer': 'https://grabgram.io/en/instagram-reels-downloader',
        }
        
        payload = {
            'url': url.strip(),
            'tool': tool
        }
        
        r_post = session.post(api_url, headers=headers_post, json=payload, timeout=20)
        if r_post.status_code != 200:
            try:
                err_msg = r_post.json().get('error', 'API request failed')
                return {"status": "error", "message": err_msg}
            except:
                return {"status": "error", "message": f"API request failed with code {r_post.status_code}"}
            
        res_json = r_post.json()
        if not res_json.get('ok'):
            return {"status": "error", "message": res_json.get('error', 'Failed to fetch media')}
            
        data = res_json.get('data', {})
        items = data.get('items', [])
        if not items:
            return {"status": "error", "message": "No media found in API response"}
            
        caption = data.get('caption')
        user_info = data.get('user', {})
        username = user_info.get('username', 'Unknown')
        full_name = user_info.get('full_name', 'Unknown')
        
        results = []
        for idx, item in enumerate(items):
            kind = item.get('kind', 'media')
            downloads = item.get('downloads', [])
            if not downloads:
                continue
            
            # Select the first download (usually highest quality)
            best_dl = downloads[0]
            download_url = best_dl.get('url')
            quality = best_dl.get('label') or best_dl.get('ext') or "Original"
            
            title = caption
            if not title:
                title = f"Instagram {kind} #{idx+1} by {username} ({full_name})"
            
            results.append({
                "Developer": "t.me/Sudhirxd",
                "Download Link": download_url,
                "Github": "www.github.com/sudheer729",
                "Quality": quality,
                "Title": title,
                "Website": "www.sudhirxd.in"
            })
            
        if not results:
            return {"status": "error", "message": "No download links found"}
            
        if len(results) == 1:
            return results[0]
            
        return results
    except Exception as e:
        return {"status": "error", "message": f"Instagram request failed: {str(e)}"}

def download_snapchat(url):
    headers = {
        "authority": "www.expertstool.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.expertstool.com",
        "referer": "https://www.expertstool.com/snapchat-video-downloader/",
        "user-agent": generate_user_agent()
    }
    data = {"url": url}
    try:
        response = requests.post("https://www.expertstool.com/converter.php", headers=headers, data=data, timeout=20)
        html = response.text
        def clean_link(link):
            if not link: return None
            link = link.replace("\\u0026", "&").replace("&quot;", "").strip()
            return link.split(",mediaPreviewUrl:")[0].rstrip("&")
        video_links = re.findall(r'<source[^>]+src="(https?://[^"]+)"', html)
        video_links = [clean_link(v) for v in video_links if clean_link(v)]
        img_links = re.findall(r'(poster|src)="(https?://[^"]+)"', html)
        image_links = list(set([clean_link(i[1]) for i in img_links if clean_link(i[1])]))
        return {
            "status": "success",
            "video": video_links[0] if video_links else None,
            "image": image_links[0] if image_links else None,
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        } if video_links or image_links else {
            "status": "error",
            "message": "Invalid Snapchat URL",
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        }
    except:
        return {
            "status": "error",
            "message": "Failed to fetch Snapchat data",
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        }

def get_pinterest_download_links(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'origin': 'https://www.expertstool.com',
        'referer': 'https://www.expertstool.com/pinterest-video-download/',
        'user-agent': generate_user_agent(),
    }
    data = {'url': url}
    try:
        response = requests.post('https://www.expertstool.com/pinterest-video-download/', headers=headers, data=data, timeout=20)
        html = response.text
        if "API Not Work" in html or "Invalid" in html:
            return {
                "status": "error",
                "message": "Invalid Pinterest URL",
                "Developer": "t.me/Sudhirxd",
                "Github": "www.github.com/sudheer729",
                "Website": "www.sudhirxd.in"
            }
        soup = BeautifulSoup(html, 'html.parser')
        for btn in soup.find_all('a', class_=re.compile(r'btn.*primary')):
            href = btn.get('href', '')
            if href.startswith('https://v') and '.mp4' in href:
                return {
                    "status": "success",
                    "video": href,
                    "Developer": "t.me/Sudhirxd",
                    "Github": "www.github.com/sudheer729",
                    "Website": "www.sudhirxd.in"
                }
        for img in soup.find_all('a', href=re.compile(r'pinimg\.com.*originals')):
            return {
                "status": "success",
                "photo": img['href'],
                "Developer": "t.me/Sudhirxd",
                "Github": "www.github.com/sudheer729",
                "Website": "www.sudhirxd.in"
            }
        return {
            "status": "error",
            "message": "No media found",
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        }
    except:
        return {
            "status": "error",
            "message": "Pinterest request failed",
            "Developer": "t.me/Sudhirxd",
            "Github": "www.github.com/sudheer729",
            "Website": "www.sudhirxd.in"
        }

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "Developer": "t.me/Sudhirxd",
        "Endpoints": {
            "Facebook": "/fb?video=URL",
            "Instagram": "/insta?video=URL",
            "Pinterest": "/pin?video=URL",
            "Snapchat": "/snap?video=URL"
        },
        "Github": "www.github.com/sudheer729",
        "Website": "www.sudhirxd.in"
    })

@app.route('/fb', methods=['GET', 'POST'])
def fb(): return jsonify(get_fb_video(request.values.get("video", "").strip()))

@app.route('/insta', methods=['GET', 'POST'])
def insta(): return jsonify(download_insta_reel(request.values.get("video", "").strip()))

@app.route('/snap', methods=['GET', 'POST'])
def snap(): return jsonify(download_snapchat(request.values.get("video", "").strip()))

@app.route('/pin', methods=['GET', 'POST'])
def pin(): return jsonify(get_pinterest_download_links(request.values.get("video", "").strip()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5150)
