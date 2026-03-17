import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import ast
import json

# 페이지 설정
st.set_page_config(
    page_title="Nemostore 판교 상가 프리미엄 대시보드",
    page_icon="🏢",
    layout="wide"
)

# 컬럼명 매핑 (영문 -> 한글)
COL_MAP = {
    'title': '매물명',
    'businessMiddleCodeName': '업종',
    'deposit': '보증금(만원)',
    'monthlyRent': '월세(만원)',
    'premium': '권리금(만원)',
    'size': '면적(㎡)',
    'floor': '층',
    'nearSubwayStation': '주변역',
    'viewCount': '조회수',
    'walk_min': '도보시간(분)'
}

# 스타일 설정
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .main-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .property-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 0;
        overflow: hidden;
        background-color: white;
        transition: transform 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .card-img-container {
        height: 180px;
        overflow: hidden;
        border-bottom: 1px solid #eee;
    }
    .card-img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .card-content {
        padding: 15px;
        flex-grow: 1;
    }
    .price-tag {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # 배포 환경을 고려한 상대 경로 설정
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_path, "..", "data", "nemostore.db")
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM products"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # 데이터 전처리
    df['walk_min'] = df['nearSubwayStation'].str.extract(r'도보 (\d+)분')[0].astype(float)
    
    # 사진 URL 파싱 (문자열 형태의 리스트 처리)
    def parse_urls(url_str):
        try:
            return ast.literal_eval(url_str) if url_str else []
        except:
            return []
            
    df['smallPhotoUrls'] = df['smallPhotoUrls'].apply(parse_urls)
    df['originPhotoUrls'] = df['originPhotoUrls'].apply(parse_urls)
    
    # 지도 시각화를 위한 가상 좌표 (판교역 중심)
    # 실제 데이터에 좌표가 없으므로 삼평동/백현동 일대 가상 좌표 생성
    import numpy as np
    df['lat'] = 37.3948 + np.random.uniform(-0.005, 0.005, len(df))
    df['lon'] = 127.1112 + np.random.uniform(-0.005, 0.005, len(df))
    
    return df

def show_detail_page(property_id, df):
    item = df[df['id'] == property_id].iloc[0]
    
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.selected_item = None
        st.rerun()
        
    st.title(f"🏠 {item['title']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 이미지 갤러리
        photos = item['originPhotoUrls']
        if photos:
            st.image(photos[0], use_container_width=True, caption="매물 대표 이미지")
            if len(photos) > 1:
                cols = st.columns(min(len(photos)-1, 4))
                for idx, photo in enumerate(photos[1:5]):
                    cols[idx].image(photo, use_container_width=True)
        else:
            st.info("등록된 이미지가 없습니다.")
            
        st.markdown("### 📝 매물 설명")
        # 실제 데이터에 코멘트가 있다면 노출 (previewPhotoUrl이 아닌 실제 content가 필요하나 현재는 컬럼 기반)
        st.write("판교역 초역세권에 위치한 우수한 가시성을 가진 상가입니다. 주변 대기업 직장인 수요가 밀집되어 있어 매출이 안정적입니다.")

    with col2:
        st.markdown("### 💰 임대 조건")
        metrics_container = st.container(border=True)
        with metrics_container:
            st.write(f"**보증금:** {item['deposit']:,} 만원")
            st.write(f"**월세:** {item['monthlyRent']:,} 만원")
            st.write(f"**권리금:** {item['premium']:,} 만원")
            st.write(f"**전용면적:** {item['size']} ㎡")
            st.write(f"**업종:** {item['businessMiddleCodeName']}")
            st.write(f"**층:** {item['floor']} 층")
            st.write(f"**주변역:** {item['nearSubwayStation']}")

        # 벤치마킹 (상대적 가치 평가)
        st.markdown("### ⚖️ 가치 평가 (시장 분석)")
        avg_rent = df[df['businessMiddleCodeName'] == item['businessMiddleCodeName']]['monthlyRent'].mean()
        rent_diff = ((item['monthlyRent'] - avg_rent) / avg_rent) * 100 if avg_rent > 0 else 0
        
        diff_color = "red" if rent_diff > 0 else "green"
        diff_text = f"동일 업종 평균 대비 **{abs(rent_diff):.1f}% {'비쌈' if rent_diff > 0 else '저렴'}**"
        
        st.markdown(f"""
            <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid {diff_color};">
                <p style="margin-bottom: 5px;">현재 매물 경쟁력</p>
                <p style="font-size: 1.1em;">{diff_text}</p>
            </div>
        """, unsafe_allow_html=True)

def main():
    if 'selected_item' not in st.session_state:
        st.session_state.selected_item = None

    df = load_data()

    if st.session_state.selected_item:
        show_detail_page(st.session_state.selected_item, df)
        return

    st.title("🏢 Nemostore 판교 상가 프리미엄 대시보드")
    
    # 사이드바: 필터 구성
    st.sidebar.header("🔍 검색 및 필터")
    
    search_query = st.sidebar.text_input("매물명, 업종, 위치 검색", "")
    
    st.sidebar.subheader("💰 가격 조건 (만원)")
    dep_range = st.sidebar.slider("보증금", 0, 200000, (0, 200000), step=1000)
    rent_range = st.sidebar.slider("월세", 0, 15000, (0, 15000), step=100)
    prem_range = st.sidebar.slider("권리금", 0, 150000, (0, 150000), step=1000)

    st.sidebar.subheader("📐 면적 조건 (㎡)")
    size_range = st.sidebar.slider("전용면적", 0.0, 200.0, (0.0, 200.0), step=5.0)

    # 필터링
    filtered_df = df[
        (df['deposit'].between(dep_range[0], dep_range[1])) &
        (df['monthlyRent'].between(rent_range[0], rent_range[1])) &
        (df['premium'].between(prem_range[0], prem_range[1])) &
        (df['size'].between(size_range[0], size_range[1]))
    ]
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['businessMiddleCodeName'].str.contains(search_query, case=False, na=False) |
            filtered_df['nearSubwayStation'].str.contains(search_query, case=False, na=False)
        ]

    # Tabs 구성
    tab1, tab2, tab3 = st.tabs(["🖼️ 이미지 갤러리", "🗺️ 지도 위치", "📊 시장 분석"])

    with tab1:
        st.subheader(f"총 {len(filtered_df)}개의 매물이 검색되었습니다.")
        
        # 3열 갤러리 구성
        rows = (len(filtered_df) + 2) // 3
        for r in range(rows):
            cols = st.columns(3)
            for c in range(3):
                idx = r * 3 + c
                if idx < len(filtered_df):
                    item = filtered_df.iloc[idx]
                    with cols[c]:
                        with st.container():
                            st.markdown(f"""
                                <div class="property-card">
                                    <div class="card-img-container">
                                        <img src="{item['smallPhotoUrls'][0] if item['smallPhotoUrls'] else 'https://via.placeholder.com/300?text=No+Image'}">
                                    </div>
                                    <div class="card-content">
                                        <p style="font-size: 0.8em; color: gray; margin-bottom: 5px;">{item['businessMiddleCodeName']} | {item['floor']}층</p>
                                        <p style="font-weight: bold; margin-bottom: 5px; height: 3em; overflow: hidden;">{item['title']}</p>
                                        <p class="price-tag">{item['deposit']:,} / {item['monthlyRent']:,} 만원</p>
                                        <p style="font-size: 0.9em;">권리금 {item['premium']:,} 만원</p>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            if st.button("상세보기", key=f"btn_{item['id']}"):
                                st.session_state.selected_item = item['id']
                                st.rerun()

    with tab2:
        st.subheader("📍 매물 위치 분석")
        if not filtered_df.empty:
            fig = px.scatter_mapbox(
                filtered_df,
                lat="lat",
                lon="lon",
                hover_name="title",
                hover_data=["deposit", "monthlyRent", "businessMiddleCodeName"],
                color="businessMiddleCodeName",
                size="monthlyRent",
                zoom=14,
                mapbox_style="carto-positron",
                height=600,
                labels={'businessMiddleCodeName': '업종', 'monthlyRent': '월세'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("표시할 수 있는 매물이 없습니다.")

    with tab3:
        st.subheader("📈 층별 및 업종별 분석")
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("#### 층별 평균 월세 분석")
            floor_rent = filtered_df.groupby('floor')['monthlyRent'].mean().reset_index()
            fig_floor = px.bar(floor_rent, x='floor', y='monthlyRent', color='floor', 
                             labels={'floor': '층', 'monthlyRent': '평균 월세(만원)'},
                             template='plotly_white')
            st.plotly_chart(fig_floor, use_container_width=True)
            
        with c2:
            st.write("#### 층별 평균 보증금 분석")
            floor_dep = filtered_df.groupby('floor')['deposit'].mean().reset_index()
            fig_dep = px.line(floor_dep, x='floor', y='deposit', markers=True,
                             labels={'floor': '층', 'deposit': '평균 보증금(만원)'},
                             template='plotly_white')
            st.plotly_chart(fig_dep, use_container_width=True)

    # 데이터 테이블 섹션 (사용자 친화적 컬럼명)
    st.markdown("---")
    st.subheader("📋 전체 매물 상세 리스트")
    table_df = filtered_df[['title', 'businessMiddleCodeName', 'deposit', 'monthlyRent', 'premium', 'size', 'floor', 'nearSubwayStation', 'viewCount', 'walk_min']]
    table_df = table_df.rename(columns=COL_MAP)
    st.dataframe(table_df, use_container_width=True)

if __name__ == "__main__":
    main()
