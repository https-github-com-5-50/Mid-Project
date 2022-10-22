# 필요 라이브러리 
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import plugins
import json
import time
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from glob import glob
import koreanize_matplotlib
import plotly.express as px


st.set_page_config(
    page_title="5시50분",
    page_icon="🕕",
    layout="wide"
)

@st.cache
def load_data(file_name,en):
    data = pd.read_csv(file_name[0], encoding=en)
    return data

# (공통) 행정동 정보 파일 불러오기-----------------
file_name = glob("data/상*.csv")
region = load_data(file_name,"utf-8")   
region = region.drop_duplicates()
df_2 = region[["상권_코드","행정동_코드","행정동명","시군구명"]]

# main 파일 불러오기-----------------------------
# 매출
file_name = glob("data/매출데이터.zip")
df_1 = load_data(file_name,"utf-8")

# df_1_columns = df_1.columns
# drop_columns = [col for col in df_1_columns if "비율" in col]
# df_1 = df_1.drop(columns=drop_columns, axis=1)
# df_1 = df_1.drop(columns=["주중_매출_금액","주말_매출_금액",'주중_매출_건수',
#        '주말_매출_건수'],axis=1)

# 지도-업종
file_name = glob('data/rawdata_folium_1022_1.csv')
df_map = load_data(file_name,"cp949")


# 상권코드를 기준으로 두 df 합치기--------------------------
# 매출
df = df_1.merge(df_2, on="상권_코드", how="left")

# 금액 단위 만원으로 바꾸기
df_columns = df.columns
price_cols = [col for col in df_columns if "금액" in col]
df[price_cols]=(df[price_cols]/10000).astype(int)

# 생활인구 (이미 전처리 완료된 데이터셋)
file_name = glob("data/mini*.csv")
df_mini = load_data(file_name,"utf-8")

# 거주인구 (이미 전처리 완료된 데이터셋)
file_name = glob("data/df_melt.csv")
df_melt = load_data(file_name,"utf-8")


# sidebar 지정-------------------------------------
with st.sidebar:
    st.markdown("## 💌 창업자를 위한 분석 보고서 💌")
    st.markdown("#### 안녕하세요! 5시 50분입니다.")
    st.markdown("#### 해당 사이트는 창업자들의 상권 분석을 도와주기 위한 목적으로 만들어졌습니다.")
    st.markdown("#### 여러 그래프를 통해 비교해보시고 창업 성공을 기원합니다.🎊")
    st.markdown("**************")
    st.markdown("## **📌page 가이드📌**")
    st.markdown("#### [1] 📊분석 리포트 : 시군구, 행정동, 업종을 선택하면 해당 선택지에 맞는 분석 리포트를 제공합니다.")
    st.markdown("#### [2] 📑관련 뉴스 검색 : 검색 키워드를 통해 오늘 뉴스를 검색할 수 있습니다. 원하는 창업 관련 키워드를 검색해보세요!" )
    st.markdown("**************")
    st.header("🔎검색")
    # 검색 요소 받기
    # 1) 시군구 선택
    sorted_unique_시군구 = sorted(df_map["시군구명"].unique())
    시군구 = st.selectbox("시군구",sorted_unique_시군구)
    # 2) 행정동 선택
    sorted_unique_행정동 = sorted(df_map.loc[df_map["시군구명"]==시군구,"행정동명"].unique())
    행정동 =  st.selectbox("행정동",sorted_unique_행정동)
    # 3) 업종 선택
    sorted_unique_업종 = sorted(df_map.loc[(df_map["시군구명"]==시군구) & (df_map["행정동명"]==행정동) ,"서비스_업종_코드_명"].unique())
    업종 =  st.selectbox("업종",sorted_unique_업종)
    st.markdown("**************")

# 선택한 지역&업종으로 df 추출 ----------------------------
# 매출
df_big = df[(df["시군구명"]==시군구) & (df["서비스_업종_코드_명"]==업종)]
df_small = df[(df["시군구명"]==시군구) & (df["서비스_업종_코드_명"]==업종) & (df["행정동명"]==행정동)]

# 생활인구
df_gu = df_mini[(df_mini["시군구명"]==시군구)]
df_dong = df_mini[(df_mini["시군구명"]==시군구) & (df_mini["행정동명"]==행정동)]

# 거주인구
df_big_melt = df_melt[df_melt["시군구명"]==시군구]
df_small_melt = df_melt[(df_melt["시군구명"]==시군구) & (df_melt["행정동명"]==행정동)]

# 지도-업종
df1 = df_map[(df_map["시군구명"]==시군구) & (df_map["서비스_업종_코드_명"]==업종)]
df2 = df_map[(df_map["시군구명"]==시군구) & (df_map["행정동명"]==행정동) & (df_map["서비스_업종_코드_명"]==업종)]


st.markdown("# ✔ 분석리포트 ✔ ")
st.markdown("+ 지도에서 원하는 부분을 클릭해주세요! 선택하신 업종의 점포 수를 확인할 수 있습니다.")
st.markdown("+ 동그라미가 클수록 해당 지역에 선택하신 업종의 수가 많다는 것을 의미합니다! 😊")

# col1 위치에 folium 지도 넣기---------------------------

m = folium.Map(location=[df2["위도"].mean(), df2["경도"].mean()], zoom_start=14)

geo_data = json.load(open('data/서울_자치구_경계_2017.geojson', encoding='UTF-8'))
folium.Choropleth(geo_data = geo_data, data = df1,
columns = ['시군구명','점포_수'], key_on="feature.properties.SIG_KOR_NM",
fill_color = 'BuPu',  
legend_name = '점포수').add_to(m)

location_data = df1[["위도","경도"]].values[:len(df1)].tolist()
for i in df1.index:
    name = df1.loc[i, "행정동명"]
    category = df1.loc[i, "서비스_업종_코드_명"]
    jumpo = df1.loc[i, "점포_수"]
    popup = folium.Popup(f"<b>{name}</b><br>{category}</b><br>{jumpo}개", max_width=300)
    tt = f"{name} 점포수 확인하기"
    location = [df1.loc[i, "위도"], df1.loc[i, "경도"]]
    if jumpo > 100:
        size_n = 550
    elif jumpo > 50:
        size_n = 450
    elif jumpo > 20:
        size_n = 350
    elif jumpo > 10:
        size_n = 250
    else:
        size_n = 150
    folium.Circle(
            location = location,
            radius= size_n,
            fill='blue',
            popup = popup,
            tooltip = tt 
    ).add_to(m)
        
plugins.MarkerCluster(location_data).add_to(m)


#지도 띄우기
st_data = st_folium(m, width = 900)

st.markdown("*****")
st.markdown("# 📰 상세 분석 리포트")
# tabl - 매출 분석 내용 띄우기--------------------------
with st.expander("💳 매출 분석"):
    st.markdown("### 💳매출 분석 리포트💳")

    # 지역별 분석
    st.markdown("*************")
    st.markdown("#### [1] 시군구 내 비교")
    st.markdown("> ###### 선택하신 시군구 안의 행정동별 분석을 보여드립니다.   행정동별로 비교해볼 수 있습니다.")
    st.markdown("\n")
    if len(df_big.index) ==0:
        st.markdown("## 😥 죄송합니다. ")
        st.markdown("## 💦 해당 시군구에 존재하는 업소의 매출 정보가 없습니다.")
    else:
        st.markdown("* ##### **행정동별 총 매출 금액 그래프**")
        st.markdown(">> ###### 행정동별로 총 매출을 보여줍니다. 단위는 만원입니다.")
        st.markdown(">> ###### 이때 총 매출은 평균 한 점포의 1년 총 매출입니다.")
        fig, axe = plt.subplots(figsize=(15,3))
        axe = sns.barplot(data=df_big, x="행정동명", y="분기당_매출_금액", estimator=sum, ci=None)
        # axe.set_title("행정동별 총매출 (단위:만원)", fontsize=15)
        axe.set_ylabel("총매출",fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)

        st.markdown("\n")
        st.markdown("* ##### **행정동별 점포 수 그래프**")
        st.markdown(">> ###### 선택하신 업종의 점포 수를 행정동별로 보여줍니다.")
        fig, axe = plt.subplots(figsize=(15,3))
        axe = sns.barplot(data=df1, x="행정동명", y="점포_수", estimator=sum, ci=None)
        # axe.set_title("행정동별 총매출 (단위:만원)", fontsize=15)
        axe.set_ylabel("총 점포 수",fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)


    st.markdown("*************")
    st.markdown("#### [2] 행정동 내 비교")
    st.markdown("> ###### 선택하신 행정동 내의 분석을 보여드립니다.")
    st.markdown("> ###### 성별 및 연령대 등으로 나누어진 다양한 매출 정보를 얻을 수 있습니다.")
    st.markdown("\n")
    # 행정동별 분석
    if len(df_small.index) ==0:
        st.markdown("## 😥 죄송합니다. ")
        st.markdown("## 💦 해당 행정동에 존재하는 업소의 매출 정보가 없습니다.")
    else:
        col = df_small.columns
        col1, col2 = st.columns([1,1])
        with col1:
            # 분기별 데이터 시각화
            st.markdown("* ##### **분기별 총 매출 금액 그래프**")
            st.markdown(">> ###### 분기별로 총 매출을 보여줍니다. 단위는 만원입니다.")
            st.markdown(">> ###### 이때 총 매출은 평균 한 점포의 분기별 총매출입니다.")
            fig, axe1 = plt.subplots(figsize=(8,5))
            axe1 = sns.barplot(data=df_small, x="기준_분기_코드", y="분기당_매출_금액",color="blue",ci=None)
            # axe1.set_title("분기별 평균 금액", fontsize=15)
            axe1.set_xlabel("분기", fontsize=10)
            axe1.set_ylabel("총 매출 금액(단위:만원)", fontsize=10)
            axe1.tick_params(labelsize=10)
            st.pyplot(fig)

            # 요일별 데이터 처리 & 시각화
            price = ['월요일_매출_금액', '화요일_매출_금액', '수요일_매출_금액', '목요일_매출_금액',
        '금요일_매출_금액', '토요일_매출_금액', '일요일_매출_금액']
            not_melt = [c for c in col if c not in price]
            df_price_melt = pd.melt(df_small, id_vars=not_melt, var_name="요일", value_name="요일별_매출금액")
            df_price_melt["요일"] = df_price_melt["요일"].str.split("_",expand=True)[0]
            cnt = ['월요일_매출_건수', '화요일_매출_건수', '수요일_매출_건수', '목요일_매출_건수',
            '금요일_매출_건수', '토요일_매출_건수', '일요일_매출_건수']
            not_melt = [c for c in col if c not in cnt]
            df_cnt_melt = pd.melt(df_small, id_vars=not_melt, var_name="요일", value_name="요일별_매출건수")
            df_cnt_melt["요일"] = df_cnt_melt["요일"].str.split("_",expand=True)[0]
            df_concat = df_price_melt.merge(df_cnt_melt[["기준_분기_코드","상권_코드","요일","요일별_매출건수"]],on=["기준_분기_코드","상권_코드","요일"],how="left")

            st.markdown("\n\n\n")
            st.markdown("\n\n\n")
            st.markdown("\n\n\n")
            st.markdown("\n\n\n")
            st.markdown("* ##### **요일별 평균 분기 매출 그래프**")
            st.markdown(">> ###### 요일별로 평균 매출을 보여줍니다. 단위는 만원입니다.")
            st.markdown(">> ###### 이때 평균 매출은 평균 한 분기당 총매출금액입니다.")
            st.markdown(">> ###### 평균 매출건수 또한 평균 한 분기당 총매출건수입니다.")


            fig, axe1 = plt.subplots(figsize=(8,5))
            axe2 = axe1.twinx()
            c1 = sns.barplot(ax=axe1, data=df_concat, x="요일", y="요일별_매출금액",color="blue",ci=None)
            c2 = sns.lineplot(ax=axe2, data=df_concat, x= "요일", y="요일별_매출건수", color="red", ci=None)

            axe2.legend(["평균 매출건수"])

            # axe1.set_title("요일별 평균 금액/건수", fontsize=15)
            axe1.set_xlabel("요일별", fontsize=10)
            axe1.set_ylabel("평균 매출금액(단위:만원)", fontsize=10)
            axe1.tick_params(labelsize=10)

            axe2.tick_params(labelsize=10)
            axe2.set_ylabel('평균 매출건수')
            st.pyplot(fig)

            # 연령대별 데이터 전처리 & 시각화
            age = ['연령대_10_매출_금액', '연령대_20_매출_금액', '연령대_30_매출_금액', 
            '연령대_40_매출_금액', '연령대_50_매출_금액', '연령대_60_이상_매출_금액']
            not_melt = [c for c in col if c not in age]
            df_price_melt = pd.melt(df_small, id_vars=not_melt, var_name="연령대", value_name="연령대별_매출금액")
            df_price_melt["연령대"] = df_price_melt["연령대"].str.split("_",expand=True)[1]
            cnt = ['연령대_10_매출_건수','연령대_20_매출_건수', '연령대_30_매출_건수', 
        '연령대_40_매출_건수', '연령대_50_매출_건수','연령대_60_이상_매출_건수']
            not_melt = [c for c in col if c not in cnt]
            df_cnt_melt = pd.melt(df_small, id_vars=not_melt, var_name="연령대", value_name="연령대별_매출건수")
            df_cnt_melt["연령대"] = df_cnt_melt["연령대"].str.split("_",expand=True)[1]
            df_concat = df_price_melt.merge(df_cnt_melt[["기준_분기_코드","상권_코드","연령대","연령대별_매출건수"]],on=["기준_분기_코드","상권_코드","연령대"],how="left")

            st.markdown("\n\n")
            st.markdown("* ##### **연령대별 평균 분기 매출 그래프**")
            st.markdown(">> ###### 연령대별로 평균 매출을 보여줍니다. 단위는 만원입니다.")
            st.markdown(">> ###### 이때 평균 매출은 평균 한 분기당 총매출금액입니다.")
            st.markdown(">> ###### 평균 매출건수 또한 평균 한 분기당 총매출건수입니다.")



            fig, axe1 = plt.subplots(figsize=(8,5))
            axe2 = axe1.twinx()

            c1 = sns.barplot(ax=axe1, data=df_concat, x="연령대", y="연령대별_매출금액",color="blue",ci=None)
            c2 = sns.lineplot(ax=axe2, data=df_concat, x= "연령대", y="연령대별_매출건수", color="red", ci=None)

            axe2.legend(["평균 매출건수"])

            # axe1.set_title("연령대별 평균 금액/건수", fontsize=15)
            axe1.set_xlabel("연령대별", fontsize=10)
            axe1.set_ylabel("평균 매출금액(단위:만원)",fontsize=10)
            axe1.tick_params(labelsize=10)

            axe2.set_ylabel('평균 매출건수')
            axe2.tick_params(labelsize=10)

            st.pyplot(fig)

        with col2:
            # 성별 데이터 전처리 & 시각화
            sex = ['남성_매출_금액', '여성_매출_금액']
            not_melt = [c for c in col if c not in sex]
            df_price_melt = pd.melt(df_small, id_vars=not_melt, var_name="성별", value_name="성별_매출금액")
            df_price_melt["성별"] = df_price_melt["성별"].str.split("_",expand=True)[0]
            cnt = ['남성_매출_건수', '여성_매출_건수']
            not_melt = [c for c in col if c not in cnt]
            df_cnt_melt = pd.melt(df_small, id_vars=not_melt, var_name="성별", value_name="성별_매출건수")
            df_cnt_melt["성별"] = df_cnt_melt["성별"].str.split("_",expand=True)[0]
            df_concat = df_price_melt.merge(df_cnt_melt[["기준_분기_코드","상권_코드","성별","성별_매출건수"]],on=["기준_분기_코드","상권_코드","성별"],how="left")

            st.markdown("* ##### **성별 평균 분기 매출 그래프**")
            st.markdown(">> ###### 성별로 평균 매출을 보여줍니다. 단위는 만원입니다.")
            st.markdown(">> ###### 이때 평균 매출은 평균 한 분기당 총매출금액입니다.")
            st.markdown(">> ###### 평균 매출건수 또한 평균 한 분기당 총매출건수입니다.")

            fig, axe1 = plt.subplots(figsize=(8,5))
            axe2 = axe1.twinx()
            c1 = sns.barplot(ax=axe1, data=df_concat, x="성별", y="성별_매출금액",color="blue",ci=None)
            c2 = sns.lineplot(ax=axe2, data=df_concat, x= "성별", y="성별_매출건수", color="red", ci=None)
            axe2.legend(["평균 매출건수(월별)"])
            
            # axe1.set_title("성별 평균 금액/건수", fontsize=15)
            axe1.set_xlabel("성별", fontsize=10)
            axe1.set_ylabel("평균 매출금액(월별/단위:만원)", fontsize=10)
            axe1.tick_params(labelsize=10)

            axe2.tick_params(labelsize=10)
            axe2.set_ylabel('평균 매출건수(월별)')
            st.pyplot(fig)

            # 시간대별 데이터 전처리 & 시각화
            time = ['시간대_00~06_매출_금액','시간대_06~11_매출_금액', '시간대_11~14_매출_금액', 
        '시간대_14~17_매출_금액', '시간대_17~21_매출_금액', '시간대_21~24_매출_금액']
            not_melt = [c for c in col if c not in time]
            df_price_melt = pd.melt(df_small, id_vars=not_melt, var_name="시간대", value_name="시간대별_매출금액")
            df_price_melt["시간대"] = df_price_melt["시간대"].str.split("_",expand=True)[1]
            cnt = ['시간대_건수~06_매출_건수','시간대_건수~11_매출_건수','시간대_건수~14_매출_건수',
            '시간대_건수~17_매출_건수','시간대_건수~21_매출_건수', '시간대_건수~24_매출_건수']
            not_melt = [c for c in col if c not in cnt]
            df_cnt_melt = pd.melt(df_small, id_vars=not_melt, var_name="시간대", value_name="시간대별_매출건수")

            def time_change(x):
                end = x.split("~")[1]
                if int(end)==6:
                    result = '00~06'
                elif int(end)==11:
                    result = '06~11'
                elif int(end)==14:
                    result = '11~14'
                elif int(end)==17:
                    result = '14~17'
                elif int(end)==21:
                    result = '17~21'
                else:
                    result = "21~24"
                    
                return result
            df_cnt_melt["시간대"] = df_cnt_melt["시간대"].str.split("_",expand=True)[1].apply(time_change)
            df_concat = df_price_melt.merge(df_cnt_melt[["기준_분기_코드","상권_코드","시간대","시간대별_매출건수"]],on=["기준_분기_코드","상권_코드","시간대"],how="left")

            st.markdown("\n\n")
            st.markdown("* ##### **시간대별 평균 분기 매출 그래프**")
            st.markdown(">> ###### 시간대별로 평균 매출을 보여줍니다. 단위는 만원입니다.")
            st.markdown(">> ###### 이때 평균 매출은 평균 한 분기당 총매출금액입니다.")
            st.markdown(">> ###### 평균 매출건수 또한 평균 한 분기당 총매출건수입니다.")


            fig, axe1 = plt.subplots(figsize=(8,5))
            axe2 = axe1.twinx()

            c1 = sns.barplot(ax=axe1, data=df_concat, x="시간대", y="시간대별_매출금액",color="blue",ci=None)
            c2 = sns.lineplot(ax=axe2, data=df_concat, x= "시간대", y="시간대별_매출건수", color="red", ci=None)

            axe2.legend(["평균 매출건수"])

            # axe1.set_title("시간대별 평균 금액/건수", fontsize=15)
            axe1.set_xlabel("시간대", fontsize=10)
            axe1.set_ylabel("평균 매출금액(단위:만원)", fontsize=10)
            axe1.tick_params(labelsize=10)

            axe2.set_ylabel('평균 매출건수')
            axe2.tick_params(labelsize=10)
            st.pyplot(fig)
        

# tab2 - 생활인구 분석 내용 띄우기--------------------------
# tab2 들어가기 전 생활 인구 데이터 변형
# 구 기준 tidy dataset
df_sex_gu = pd.melt(df_gu, id_vars=["시군구명", '행정동명', '기준_분기_코드', '총_생활인구_수'], value_vars=['남성', '여성'], var_name="성별별", value_name="성별별인구")
df_age_gu = pd.melt(df_gu, id_vars=["시군구명", '행정동명', '기준_분기_코드'], value_vars=['10대', '20대', '30대', '40대', '50대', '60대_이상'],
                      var_name="연령별", value_name="연령별인구")
df_time_gu = pd.melt(df_gu, id_vars=["시군구명", '행정동명', '기준_분기_코드'],
               value_vars=['00~06시', '06~11시', '11~14시', '14~17시', '17~21시', '21~24시'],
               var_name="시간대별", value_name="시간대별인구")
df_week_gu = pd.melt(df_gu, id_vars=["시군구명", '행정동명', '기준_분기_코드'],
                       value_vars=['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'],
                       var_name="요일별", value_name="요일별인구")
# 행 기준 tidy dataset
df_sex_dong = pd.melt(df_dong, id_vars=["시군구명", '행정동명', '기준_분기_코드', '총_생활인구_수'], value_vars=['남성', '여성'], var_name="성별별", value_name="성별별인구")
df_age_dong = pd.melt(df_dong, id_vars=["시군구명", '행정동명', '기준_분기_코드'], value_vars=['10대', '20대', '30대', '40대', '50대', '60대_이상'],
                      var_name="연령별", value_name="연령별인구")
df_time_dong = pd.melt(df_dong, id_vars=["시군구명", '행정동명', '기준_분기_코드'],
               value_vars=['00~06시', '06~11시', '11~14시', '14~17시', '17~21시', '21~24시'],
               var_name="시간대별", value_name="시간대별인구")
df_week_dong = pd.melt(df_dong, id_vars=["시군구명", '행정동명', '기준_분기_코드'],
                       value_vars=['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'],
                       var_name="요일별", value_name="요일별인구")                 

# tab2 들어가서 생활인구 분석 시각화
with st.expander("🏃‍♀️ 생활인구 분석"):
    st.markdown("### 🏃‍♀️생활인구 분석 리포트🏃‍♂️")

    # 지역별 분석
    st.markdown("*************")
    st.markdown("#### [1] 시군구 내 비교")
    st.markdown("> ###### 선택하신 시군구 안의 행정동별 분석을 보여드립니다.   행정동별로 비교해볼 수 있습니다.")
    st.markdown("\n")

    st.markdown("* ##### **행정동별 총 생활인구 그래프**")
    st.markdown(">> ###### 행정동별로 총 생활인구를 보여줍니다.")

    fig, axe = plt.subplots(figsize=(15,3))
    axe = sns.barplot(data=df_sex_gu, x="행정동명", y="총_생활인구_수", estimator=sum, ci=None)
    # axe.set_title("행정동별 총 생활인구 수", fontsize=15)
    axe.set_ylabel("총 생활인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    st.pyplot(fig)

    st.markdown("* ##### **행정동별 & 성별 총 생활인구 그래프**")
    st.markdown(">> ###### 행정동별 & 성별로 나누어 총 생활인구를 보여줍니다.")
    fig, axe = plt.subplots(figsize=(15,3))
    axe = sns.barplot(data=df_sex_gu, x="행정동명", y="성별별인구", hue="성별별", estimator=sum, ci=None)
    # axe.set_title("행정동별&성별 총 생활인구 수", fontsize=15)
    axe.set_ylabel("총 생활인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    axe.legend(title='성별', loc='upper right')
    st.pyplot(fig)

    st.markdown("* ##### **행정동별 & 연령대별 총 생활인구 그래프**")
    st.markdown(">> ###### 행정동별 & 연령대별로 나누어 총 생활인구를 보여줍니다.")
    fig, axe = plt.subplots(figsize=(15,3))
    axe = sns.barplot(data=df_age_gu, x="행정동명", y="연령별인구", hue="연령별", estimator=sum, ci=None)
    # axe.set_title("행정동별&연령대별 총 생활인구 수", fontsize=15)
    axe.set_ylabel("총 생활인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    axe.legend(title='연령별', loc='upper right')
    st.pyplot(fig)

    st.markdown("* ##### **행정동별 & 시간대별 총 생활인구 그래프**")
    st.markdown(">> ###### 행정동별 & 시간대별로 나누어 총 생활인구를 보여줍니다.")
    fig, axe = plt.subplots(figsize=(15,3))
    axe = sns.lineplot(data=df_time_gu, x="행정동명", y="시간대별인구", hue="시간대별", estimator=sum, ci=None)
    # axe.set_title("행정동별&시간대별 총 생활인구 수", fontsize=15)
    axe.set_ylabel("총 생활인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    axe.legend(title='시간대', loc='upper right')
    st.pyplot(fig)

    # 행정동별 분석
    st.markdown("*************")
    st.markdown("#### [2] 행정동 내 비교")
    st.markdown("> ###### 선택하신 행정동 내의 분석을 보여드립니다.")
    st.markdown("> ###### 성별 및 연령대 등으로 나누어진 다양한 생활인구 정보를 얻을 수 있습니다.")
    st.markdown("\n")

    col3, col4 = st.columns([1,1])
    with col3:
        st.markdown("\n\n")
        st.markdown("* ##### **분기별 평균 생활인구 수 그래프**")
        st.markdown(">> ###### 분기별로 평균 생활인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_dong, x="기준_분기_코드", y="총_생활인구_수", ci=None)
        # axe.set_title("분기별 평균 생활인구 수", fontsize=15)
        axe.set_xlabel("분기", fontsize=10)
        axe.set_ylabel("평균 생활인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)

        st.markdown("\n\n")
        st.markdown("* ##### **연령대별 평균 생활인구 수 그래프**")
        st.markdown(">> ###### 연령대별로 평균 생활인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_age_dong, x="연령별", y="연령별인구", ci=None)
        # axe.set_title("연령대별 평균 생활인구 수", fontsize=15)
        axe.set_xlabel("연령대", fontsize=10)
        axe.set_ylabel("평균 생활인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)

        st.markdown("\n\n")
        st.markdown("* ##### **요일별 평균 생활인구 수 그래프**")
        st.markdown(">> ###### 요일별로 평균 생활인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_week_dong, x="요일별", y="요일별인구", ci=None)
        # axe.set_title("요일별 평균 생활인구 수", fontsize=10)
        axe.set_xlabel("요일", fontsize=10)
        axe.set_ylabel("평균 생활인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)



    with col4:
        st.markdown("\n\n")
        st.markdown("* ##### **성별별 평균 생활인구 수 그래프**")
        st.markdown(">> ###### 성별별로 평균 생활인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_sex_dong, x="행정동명", y="성별별인구", hue="성별별", ci=None)
        # axe.set_title("성별 평균 생활인구 수", fontsize=15)
        axe.set_xlabel(" ", fontsize=10)
        axe.set_ylabel("평균 생활인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        axe.legend(title='성별', loc='upper right')
        st.pyplot(fig)

        st.markdown("\n\n")
        st.markdown("* ##### **시간대별 평균 생활인구 수 그래프**")
        st.markdown(">> ###### 시간대별로 평균 생활인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.lineplot(data=df_time_dong, x="시간대별", y="시간대별인구", ci=None)
        # axe.set_title("시간대별 평균 생활인구 수", fontsize=15)
        axe.set_xlabel("시간대", fontsize=10)
        axe.set_ylabel("평균 생활인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)


# tab3 들어가서 거주인구 분석 시각화
with st.expander("🏠 거주인구 분석"):
    st.markdown("### 🏠거주인구 분석 리포트🏠")

    # 지역별 분석
    st.markdown("*************")
    st.markdown("#### [1] 시군구 내 비교")
    st.markdown("> ###### 선택하신 시군구 안의 행정동별 분석을 보여드립니다.   행정동별로 비교해볼 수 있습니다.")
    st.markdown("\n")

    st.markdown("* ##### **행정동별 총 거주인구 그래프**")
    st.markdown(">> ###### 행정동별로 나누어 총 거주인구를 보여줍니다.")
    fig, axe = plt.subplots(figsize=(15,5))
    axe = sns.barplot(data=df_big_melt, x="행정동명", y="연령대별 수", estimator=sum, ci=None)
    # axe.set_title("행정동별 총 거주인구 수", fontsize=15)
    axe.set_ylabel("총 거주인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    st.pyplot(fig)

    st.markdown("* ##### **행정동별 & 성별 총 거주인구 그래프**")
    st.markdown(">> ###### 행정동별 & 성별로 나누어 총 거주인구를 보여줍니다.")
    fig, axe = plt.subplots(figsize=(15,5))
    axe = sns.barplot(data=df_big_melt, x="행정동명", y="연령대별 수", hue ="성별" , ci=None)
    # axe.set_title("행정동별 & 성별 총 거주인구 수", fontsize=15)
    axe.set_ylabel("총 거주인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    st.pyplot(fig)

    st.markdown("* ##### **행정동별 & 연령대별 총 거주인구 그래프**")
    st.markdown(">> ###### 행정동별 & 연령대별로 나누어 총 거주인구를 보여줍니다.")
    fig, axe = plt.subplots(figsize=(15,5))
    axe = sns.barplot(data=df_big_melt, x="행정동명", y="연령대별 수", hue ="성별" , ci=None)
    # axe.set_title("행정동별 & 연령대별 총 거주인구 수", fontsize=15)
    axe.set_ylabel("총 거주인구 수",fontsize=10)
    axe.tick_params(labelsize=10)
    st.pyplot(fig)

    # 행정동별 분석
    st.markdown("*************")
    st.markdown("#### [2] 행정동 내 비교")
    st.markdown("> ###### 선택하신 행정동 내의 분석을 보여드립니다.")
    st.markdown("> ###### 성별 및 연령대 등으로 나누어진 다양한 거주인구 정보를 얻을 수 있습니다.")
    st.markdown("\n")

    col5, col6 = st.columns([1,1])
    with col5:
        st.markdown("\n\n")
        st.markdown("* ##### **분기별 평균 거주인구 수 그래프**")
        st.markdown(">> ###### 분기별로 평균 거주인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_small_melt, x="분기", y="연령대별 수", ci=None)
        # axe.set_title("분기별 평균 거주인구 수", fontsize=10)
        axe.set_xlabel("분기", fontsize=10)
        axe.set_ylabel("평균 거주인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)

        st.markdown("* ##### **성별 평균 거주인구 수 그래프**")
        st.markdown(">> ###### 성별별로 평균 거주인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_small_melt, x="성별", y="연령대별 수", ci=None)
        # axe.set_title("성별 평균 거주인구 수", fontsize=10)
        axe.set_xlabel("성별", fontsize=10)
        axe.set_ylabel("평균 거주인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)

    with col6:
        st.markdown("* ##### **연령대별 평균 거주인구 수 그래프**")
        st.markdown(">> ###### 연령대별로 평균 거주인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_small_melt, x="상주인구 연령대", y="연령대별 수", ci=None)
        # axe.set_title("연령대별 평균 거주인구 수", fontsize=10)
        axe.set_xlabel("연령대별", fontsize=10)
        axe.set_ylabel("평균 거주인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)

        st.markdown("* ##### **연령대별 & 성별 평균 거주인구 수 그래프**")
        st.markdown(">> ###### 연령대별 & 성별로 나누어 평균 거주인구 수를 보여줍니다.")
        fig, axe = plt.subplots(figsize=(8,5))
        axe = sns.barplot(data=df_small_melt, x="상주인구 연령대", y="연령대별 수", hue="성별", ci=None)
        axe.set_xlabel("연령대별", fontsize=10)
        axe.set_ylabel("평균 거주인구 수", fontsize=10)
        axe.tick_params(labelsize=10)
        st.pyplot(fig)    


