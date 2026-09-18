import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    df = pd.read_csv(DATA_URL)

    # 장르가 여러 개이면 첫 번째 장르만 사용
    df["장르"] = (
        df["genre"]
        .fillna("장르 미상")
        .astype(str)
        .str.split("|")
        .str[0]
    )

    # 제작 국가가 여러 개이면 첫 번째 국가만 사용
    df["대표국가"] = (
        df["nation"]
        .fillna("국가 미상")
        .astype(str)
        .str.split("|")
        .str[0]
    )

    # 숫자 열을 숫자형으로 변환
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# ─────────────────────────────────────
# 그래프 1. 장르별 영화 편수 도넛
# ─────────────────────────────────────
st.header("1. 장르별 영화 편수 (도넛)")

genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45
)

fig1.update_traces(
    hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>"
)

st.plotly_chart(fig1, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note1"
)

st.divider()


# ─────────────────────────────────────
# 그래프 2. 장르 안의 영화 (트리맵)
# ─────────────────────────────────────
st.header("2. 장르 안의 영화 (트리맵)")

treemap_df = (
    df.groupby(["장르", "movieNm"], as_index=False)["total_audi"]
    .sum()
)

# Plotly의 계층 이름 충돌을 피하기 위해 직접 계층을 만듭니다.
labels = []
parents = []
values = []

for genre, group in treemap_df.groupby("장르", sort=True):

    genre_total = group["total_audi"].sum()

    labels.append(str(genre))
    parents.append("")
    values.append(genre_total)

    for _, row in group.iterrows():
        movie = str(row["movieNm"])

        labels.append(movie + " (영화)")
        parents.append(str(genre))
        values.append(row["total_audi"])

fig2 = go.Figure(
    go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate=(
            "%{label}<br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        )
    )
)

st.plotly_chart(fig2, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note2"
)

st.divider()


# ─────────────────────────────────────
# 그래프 3. 총 관객의 분포 (히스토그램)
# ─────────────────────────────────────
st.header("3. 총 관객의 분포 (히스토그램)")

hist_df = df.dropna(subset=["total_audi"])

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=40
)

st.plotly_chart(fig3, width="stretch")

under_1m = (hist_df["total_audi"] < 1_000_000).sum()

if not hist_df.empty:
    best = hist_df.loc[hist_df["total_audi"].idxmax()]

    st.write(
        f"{len(df)}편 가운데 {under_1m}편이 100만 명 미만입니다. "
        f"가장 많이 본 영화는 {best['movieNm']} "
        f"({best['total_audi']:,.0f}명)입니다."
    )

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note3"
)

st.divider()


# ─────────────────────────────────────
# 그래프 4. 개봉일 스크린 수와 총 관객 (산점도)
# ─────────────────────────────────────
st.header("4. 개봉일 스크린 수와 총 관객 (산점도)")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi", "장르"]
)

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm"
)

st.plotly_chart(fig4, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note4"
)

st.divider()


# ─────────────────────────────────────
# 그래프 5. 장르별 총 관객 (박스플롯)
# ─────────────────────────────────────
st.header("5. 장르별 총 관객 (박스플롯)")

big = df["장르"].value_counts()
big = big[big >= 10].index

box_df = df[
    df["장르"].isin(big)
].dropna(subset=["장르", "total_audi"])

fig5 = px.box(
    box_df,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm"
)

st.plotly_chart(fig5, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note5"
)

st.divider()


# ─────────────────────────────────────
# 그래프 6. 첫 주 관객을 점 크기로 (버블)
# ─────────────────────────────────────
st.header("6. 첫 주 관객을 점 크기로 (버블)")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "장르"
    ]
).copy()

bubble_df["first_week_audi"] = bubble_df["first_week_audi"].clip(lower=0)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    size="first_week_audi",
    size_max=40,
    hover_name="movieNm"
)

st.plotly_chart(fig6, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note6"
)

st.divider()


# ─────────────────────────────────────
# 그래프 7. 국가에서 장르로 (선버스트)
# ─────────────────────────────────────
st.header("7. 국가에서 장르로 (선버스트)")

counted = (
    df.groupby(
        ["대표국가", "장르"],
        as_index=False
    )
    .agg(편수=("movieNm", "count"))
)

fig7 = px.sunburst(
    counted,
    path=["대표국가", "장르"],
    values="편수"
)

st.plotly_chart(fig7, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note7"
)

st.divider()


# ─────────────────────────────────────
# 그래프 8. 나만의 질문
# ─────────────────────────────────────
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가?")

# 질문에 필요한 두 열만 사용하고 결측값 제거
question_df = df.dropna(
    subset=["days_in_top10", "total_audi", "movieNm"]
).copy()

fig8 = px.scatter(
    question_df,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm"
)

fig8.update_layout(
    xaxis_title="10위권에 머문 날수",
    yaxis_title="총 관객"
)

fig8.update_traces(
    hovertemplate=(
        "영화: %{hovertext}<br>"
        "10위권에 머문 날수: %{x}일<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

st.plotly_chart(fig8, width="stretch")

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note8"
)
