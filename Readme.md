# 🚀 Social Media Downloader API 📥

A powerful and fast Flask-based API to download media from various social media platforms! Ready to be deployed on **Vercel** with a single click. 🌟

---

## 🛠️ Features

* 📸 **Instagram:** Reels, Posts (Photos/Videos), Stories, Highlights & Profiles.
* 👥 **Facebook:** HD & SD Video download links.
* 👻 **Snapchat:** Direct video & image extraction.
* 📌 **Pinterest:** Direct video & high-resolution photo links.
* ⚡ **Fast & Lightweight:** Built with Flask and standard Python requests.
* ☁️ **Vercel Ready:** Preconfigured for hosting as a serverless backend.

---

## 📡 API Endpoints

### 🏠 1. Root / Health Check
Get all available endpoints and developer information.
* **Endpoint:** `/`
* **Method:** `GET`
* **Response Example:**
  ```json
  {
    "Developer": "t.me/Sudhirxd",
    "Endpoints": {
      "Facebook": "/fb?video=URL",
      "Instagram": "/insta?video=URL",
      "Pinterest": "/pin?video=URL",
      "Snapchat": "/snap?video=URL"
    },
    "Github": "www.github.com/sudheer729",
    "Website": "www.sudhirxd.in"
  }
  ```

### 📸 2. Instagram Downloader
Download Reels, posts, stories, highlights, or profile grids.
* **Endpoint:** `/insta`
* **Method:** `GET` or `POST`
* **Parameter:** `video` (The Instagram URL)
* **Response Example:**
  ```json
  {
    "Developer": "t.me/Sudhirxd",
    "Download Link": "https://instagram.fyyc6-1.fna.fbcdn.net/...",
    "Github": "www.github.com/sudheer729",
    "Quality": "720p",
    "Title": "Instagram post description",
    "Website": "www.sudhirxd.in"
  }
  ```
  *(Note: Returns a list of objects if multiple slides, stories, or posts are detected.)*

### 👥 3. Facebook Downloader
* **Endpoint:** `/fb`
* **Method:** `GET` or `POST`
* **Parameter:** `video` (The Facebook URL)

### 👻 4. Snapchat Downloader
* **Endpoint:** `/snap`
* **Method:** `GET` or `POST`
* **Parameter:** `video` (The Snapchat URL)

### 📌 5. Pinterest Downloader
* **Endpoint:** `/pin`
* **Method:** `GET` or `POST`
* **Parameter:** `video` (The Pinterest Pin URL)

---

## 💻 Running Locally

1. **Clone or download** this project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```bash
   python api.py
   ```
4. Access the API local host: `http://127.0.0.1:5150/` 🚀

---

## ☁️ Deploying to Vercel

This repository contains the required [vercel.json](file:///c:/Users/HP/Desktop/yt%20do/downloads/vercel.json) config file.

### Option A: Using Vercel CLI 💻
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Run in the root folder:
   ```bash
   vercel
   ```

### Option B: Link via GitHub 🐙
1. Upload this project to GitHub.
2. Import it on the [Vercel Dashboard](https://vercel.com/dashboard).
3. Click **Deploy**! 🚀

---

## 👨‍💻 Developer Credits

* **Developer:** [@Sudhirxd](https://t.me/Sudhirxd) 💬
* **GitHub:** [sudheer729](https://www.github.com/sudheer729) 🐙
* **Website:** [sudhirxd.in](http://www.sudhirxd.in) 🌐
