import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(page_title="YouTube 상승세 채널 발굴기", layout="wide")

# --- 사이드바: 설정 및 필터 ---
st.sidebar.title("🔍 검색 설정")

api_key = st.sidebar.text_input("YouTube API Key를 입력하세요", type="password")
keyword = st.sidebar.text_input("검색 키워드", placeholder="예: 브이로그, 캠핑, 테크")

# 영상 길이 설정
duration_options = {
    "전체": "any",
    "짧음 (4분 미만)": "short",
    "중간 (4~20분)": "medium",
    "김 (20분 이상)": "long"
}
duration_label = st.sidebar.selectbox("영상 길이", list(duration_options.keys()))
duration_value = duration_options[duration_label]

# 국가 및 언어 설정
region_options = {"대한민국": "KR", "미국": "US", "일본": "JP", "전체": None}
region_label = st.sidebar.selectbox("국가 선택", list(region_options.keys()))
region_value = region_options[region_label]

lang_options = {"한국어": "ko", "영어": "en", "일본어": "ja", "전체": None}
lang_label = st.sidebar.selectbox("언어 선택", list(lang_options.keys()))
lang_value = lang_options[lang_label]

# 기간 설정
date_options = {
    "최근 1일": 1,
    "최근 3일": 3,
    "최근 7일": 7,
    "최근 30일": 30,
    "최근 90일": 90,
    "최근 1년": 365
}
date_label = st.sidebar.selectbox("업로드 날짜", list(date_options.keys()), index=3) # 기본값 최근 30일
days_back = date_options[date_label]
published_after = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"

st.sidebar.divider()
st.sidebar.title("📈 상승세 필터")

# 최대 구독자 수 드랍다운
subs_options = {
    "1만 명 이하": 10000,
    "5만 명 이하": 50000,
    "10만 명 이하": 100000,
    "20만 명 이하": 200000,
    "50만 명 이하": 500000,
    "100만 명 이하": 1000000
}
subs_label = st.sidebar.selectbox("최대 구독자 수", list(subs_options.keys()), index=1) # 기본값 5만
max_subs = subs_options[subs_label]

# 최소 조회수 드랍다운
views_options = {
    "1만 회 이상": 10000,
    "3만 회 이상": 30000,
    "5만 회 이상": 50000,
    "10만 회 이상": 100000,
    "30만 회 이상": 300000,
    "50만 회 이상": 500000,
    "100만 회 이상": 1000000
}
views_label = st.sidebar.selectbox("최소 조회수", list(views_options.keys()), index=2) # 기본값 5만
min_views = views_options[views_label]

# --- 메인 화면 ---
st.title("🚀 YouTube 상승세 채널 발굴 프로그램")
st.write("구독자 수는 적지만 조회수가 폭발적으로 높은 알짜 채널을 찾아보세요.")

if st.button("검색 시작"):
    if not api_key:
        st.error("API Key를 입력해주세요.")
    elif not keyword:
        st.error("검색 키워드를 입력해주세요.")
    else:
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
            
            with st.spinner("YouTube 데이터를 가져오는 중..."):
                # 1. 영상 검색 (search.list)
                search_params = {
                    "q": keyword,
                    "part": "snippet",
                    "type": "video",
                    "maxResults": 50,
                    "videoDuration": duration_value,
                    "publishedAfter": published_after,
                    "order": "viewCount" # 조회수 높은 순으로 1차 시도 (API 제약상 완벽하진 않음)
                }
                if region_value: search_params["regionCode"] = region_value
                if lang_value: search_params["relevanceLanguage"] = lang_value
                
                search_response = youtube.search().list(**search_params).execute()
                
                items = search_response.get("items", [])
                if not items:
                    st.warning("검색 결과가 없습니다.")
                else:
                    video_ids = [item["id"]["videoId"] for item in items]
                    channel_ids = [item["snippet"]["channelId"] for item in items]
                    
                    # 2. 영상 상세 정보 가져오기 (videos.list) - 정확한 조회수 확인
                    video_response = youtube.videos().list(
                        part="statistics,snippet",
                        id=",".join(video_ids)
                    ).execute()
                    
                    video_data = {}
                    for v in video_response.get("items", []):
                        video_data[v["id"]] = {
                            "title": v["snippet"]["title"],
                            "thumbnail": v["snippet"]["thumbnails"]["medium"]["url"],
                            "viewCount": int(v["statistics"].get("viewCount", 0)),
                            "likeCount": int(v["statistics"].get("likeCount", 0)),
                            "commentCount": int(v["statistics"].get("commentCount", 0)),
                            "channelId": v["snippet"]["channelId"],
                            "channelTitle": v["snippet"]["channelTitle"],
                            "publishedAt": v["snippet"]["publishedAt"]
                        }
                    
                    # 3. 채널 정보 가져오기 (channels.list) - 구독자 수 확인
                    # 중복 채널 ID 제거
                    unique_channel_ids = list(set(channel_ids))
                    channel_response = youtube.channels().list(
                        part="statistics",
                        id=",".join(unique_channel_ids)
                    ).execute()
                    
                    channel_subs = {}
                    for c in channel_response.get("items", []):
                        channel_subs[c["id"]] = int(c["statistics"].get("subscriberCount", 0))
                    
                    # 4. 데이터 병합 및 필터링
                    results = []
                    for vid, info in video_data.items():
                        subs = channel_subs.get(info["channelId"], 0)
                        views = info["viewCount"]
                        
                        # 상승세 조건 체크
                        if subs <= max_subs and views >= min_views:
                            ratio = round(views / subs, 2) if subs > 0 else views
                            
                            results.append({
                                "id": vid,
                                "channelTitle": info["channelTitle"],
                                "title": info["title"],
                                "thumbnail": info["thumbnail"],
                                "subs": subs,
                                "views": views,
                                "likes": info["likeCount"],
                                "comments": info["commentCount"],
                                "ratio": ratio,
                                "date": info["publishedAt"][:10],
                                "url": f"https://www.youtube.com/watch?v={vid}"
                            })
                    
                    if not results:
                        st.info("조건에 맞는 상승세 채널을 찾지 못했습니다. 필터를 조절해보세요.")
                    else:
                        # 배수 기준으로 내림차순 정렬
                        results = sorted(results, key=lambda x: x["ratio"], reverse=True)
                        
                        st.success(f"총 {len(results)}개의 상승세 영상을 찾았습니다!")
                        
                        # 카드 형태 UI 출력
                        for res in results:
                            with st.container():
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    st.image(res["thumbnail"], use_container_width=True)
                                
                                with col2:
                                    st.subheader(res["title"])
                                    st.write(f"📺 **채널**: {res['channelTitle']} | 📅 **업로드**: {res['date']}")
                                    
                                    m1, m2, m3, m4 = st.columns(4)
                                    m1.metric("조회수", f"{res['views']:,}")
                                    m2.metric("구독자", f"{res['subs']:,}")
                                    m3.metric("좋아요", f"{res['likes']:,}")
                                    m4.metric("댓글", f"{res['comments']:,}")
                                    
                                    st.info(f"🔥 구독자 대비 조회수 **{res['ratio']}배** 폭발 중!")
                                    
                                    st.link_button("📺 영상 보러가기", res["url"], use_container_width=True)
                                
                                st.divider()
                        
        except HttpError as e:
            st.error(f"YouTube API 오류가 발생했습니다: {e}")
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")

st.divider()
st.caption("© 2026 YouTube Rising Channel Finder. 모든 데이터는 YouTube Data API v3를 통해 실시간으로 제공됩니다.")
