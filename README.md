# 🚀 YouTube Rising Channel Finder

A specialized tool designed to discover "hidden gem" YouTube channels that have a small subscriber base but achieve exceptionally high view counts. This tool helps identify rising trends and high-potential niches by filtering out the noise of established large channels.

## ✨ Key Features

- **Rising Star Detection**: Specifically identifies channels with low subscriber counts but high viral potential.
- **Card-based Visual UI**: Browse search results with high-quality thumbnails and intuitive engagement metrics.
- **Deep Metrics**: View not just views and subscribers, but also **Likes** and **Comment counts** for each video.
- **Smart Filtering**:
    - **Upload Date**: Filter by last 1 day, 3 days, 7 days, 30 days, 90 days, or 1 year.
    - **Subscriber Cap**: Set maximum subscriber limits (e.g., under 50k) to find small growing channels.
    - **View Floor**: Set minimum view thresholds to ensure the content is trending.
    - **Duration & Region**: Filter by video length (Short/Medium/Long) and target specific countries or languages.
- **Automated Ranking**: Results are automatically sorted by the **View-to-Subscriber Ratio**, highlighting the most "explosive" content first.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Xxxng/youtube-rising-channel-finder.git
   cd youtube-rising-channel-finder
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a YouTube Data API Key:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a project and enable the **YouTube Data API v3**.
   - Create credentials (API Key).

## 🚀 How to Use

1. **Run the application:**
   ```bash
   streamlit run app.py
   ```
2. **Configure Settings (Sidebar):**
   - Enter your **YouTube API Key**.
   - Enter a **Keyword** (e.g., "Camping", "Tech Review", "Vlog").
   - Select the **Upload Date**, **Max Subscribers**, and **Min Views**.
3. **Analyze Results:**
   - Review the video thumbnails and engagement metrics (Views, Subs, Likes, Comments).
   - Click the **"Watch Video"** button to jump directly to YouTube.

## 📦 Requirements

- Python 3.8+
- Streamlit
- Google API Python Client
- Pandas

---
© 2026 YouTube Rising Channel Finder. All data is provided in real-time via the YouTube Data API v3.
