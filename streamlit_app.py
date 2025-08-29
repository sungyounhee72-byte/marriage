#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Marriage Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 10px;
    text-align: center;
    padding: 15px 0;
    margin-bottom: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
""", unsafe_allow_html=True)

#######################
# Load marriage data
df_reshaped = pd.read_csv("marriage.csv", encoding="cp949")

#######################
# Sidebar
with st.sidebar:
    st.title("💍 2024년 서울시 결혼 신고 데이터 대시보드")

    # 추가 필터 (직업, 연령대)
    with st.expander("추가 필터"):
        husband_jobs = sorted(df_reshaped["남편직업분류코드"].unique())
        wife_jobs = sorted(df_reshaped["아내직업분류코드"].unique())

        selected_husband_job = st.multiselect("남편 직업 코드", husband_jobs)
        selected_wife_job = st.multiselect("아내 직업 코드", wife_jobs)

        husband_age = sorted(df_reshaped["남편연령5세단위코드"].unique())
        wife_age = sorted(df_reshaped["아내연령5세단위코드"].unique())

        selected_husband_age = st.multiselect("남편 연령대 코드", husband_age)
        selected_wife_age = st.multiselect("아내 연령대 코드", wife_age)

    # 색상 테마 선택
    color_theme = st.selectbox("색상 테마 선택", ["Blues", "Reds", "Greens"])
    apply_filter = st.button("필터 적용하기")

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap="medium")

# ===============================
# Column 1: Summary Metrics
# ===============================
with col[0]:
    st.markdown("### 📌 주요 지표 요약")

    total_marriages = len(df_reshaped)
    avg_husband_age = df_reshaped["남편연령5세단위코드"].mean()
    avg_wife_age = df_reshaped["아내연령5세단위코드"].mean()
    husband_first_marriage_ratio = (df_reshaped["남편결혼종류코드"] == 1).mean() * 100
    wife_first_marriage_ratio = (df_reshaped["아내결혼종류코드"] == 1).mean() * 100

    st.metric("총 결혼 건수", f"{total_marriages:,} 건")
    st.metric("남편 평균 연령대 코드", f"{avg_husband_age:.1f}")
    st.metric("아내 평균 연령대 코드", f"{avg_wife_age:.1f}")
    st.metric("남편 초혼 비율", f"{husband_first_marriage_ratio:.1f}%")
    st.metric("아내 초혼 비율", f"{wife_first_marriage_ratio:.1f}%")

# ===============================
# Column 2: 월별 + 연령대별 분석
# ===============================
with col[1]:
    st.markdown("### 📅 월별 결혼 현황")

    monthly_counts = df_reshaped.groupby("신고월").size().reset_index(name="결혼건수")

    fig_month = px.line(
        monthly_counts,
        x="신고월",
        y="결혼건수",
        markers=True,
        title="월별 결혼 건수"
    )
    st.plotly_chart(fig_month, use_container_width=True)

    st.markdown("### 👥 연령대별 결혼 현황 (히트맵)")

    age_counts = (
        df_reshaped.groupby(["남편연령5세단위코드", "아내연령5세단위코드"])
        .size()
        .reset_index(name="결혼건수")
    )

    fig_age = px.density_heatmap(
        age_counts,
        x="남편연령5세단위코드",
        y="아내연령5세단위코드",
        z="결혼건수",
        color_continuous_scale=color_theme,
        title="남편 vs 아내 연령대별 결혼 현황"
    )
    st.plotly_chart(fig_age, use_container_width=True)

# ===============================
# Column 3: Ranking + Details
# ===============================
with col[2]:
    st.markdown("### 🏆 세부 분석")

    st.markdown("#### 💼 직업별 결혼 분포 (남편 기준)")
    job_dist = (
        df_reshaped.groupby("남편직업분류코드")
        .size()
        .reset_index(name="결혼건수")
        .sort_values("결혼건수", ascending=False)
        .head(10)
    )
    fig_job = px.bar(
        job_dist,
        x="남편직업분류코드",
        y="결혼건수",
        color="결혼건수",
        color_continuous_scale=color_theme,
        title="남편 직업별 결혼 건수 TOP 10"
    )
    st.plotly_chart(fig_job, use_container_width=True)

    st.markdown("#### 💍 초혼 · 재혼 비율 (남편 기준)")
    marriage_type = (
        df_reshaped["남편결혼종류코드"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "결혼종류코드", "남편결혼종류코드": "건수"})
    )
    marriage_type.columns = ["결혼종류코드", "건수"]

    fig_pie = px.pie(
        marriage_type,
        names="결혼종류코드",
        values="건수",
        title="남편 결혼 종류 분포"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### ℹ️ About")
    st.info(
        """
        데이터 출처: 행정안전부 · 통계청  
        - `결혼종류코드`: 1=초혼, 2=재혼  
        - `연령5세단위코드`: 1=15~19세, 2=20~24세 …  
        - `직업분류코드`: 통계청 직업분류 기준  
        """
    )
