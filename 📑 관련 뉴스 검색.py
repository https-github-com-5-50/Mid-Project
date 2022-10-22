import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import re
import streamlit as st
import streamlit.components.v1 as components

def Naver_news(keyword):
    
    top_page_url = []
    enctext = urllib.parse.quote(keyword)
    url = 'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query='+enctext
    headers = {'User-Agent': 'Chrome/105.0.0.0 '}
    response = requests.get(url, headers=headers)
    soup = bs(response.text, "html.parser")

    soup = soup.find('div', id='content')
    soup = soup.find('div', id='main_pack')
    soup = soup.find('section', class_='sc_new sp_nnews _prs_nws')

    for href in soup.find("ul", class_="list_news").find_all("div",attrs = {"class":re.compile("api_save_group _keep_wrap")}):
        temp = href.find("a")["data-url"]
        top_page_url.append(temp)
        
    return top_page_url

def Naver_title(keyword):
    
    real_title=[]
    enctext = urllib.parse.quote(keyword)
    url = 'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query='+enctext
    headers = {'User-Agent': 'Chrome/105.0.0.0 '}
    response = requests.get(url, headers=headers)
    soup = bs(response.text, "html.parser")
    items = soup.select('.news_tit')
    for item in items:
        real_title.append(item.text)
        
    return real_title

st.markdown("## 🔎 검색할 키워드를 입력하세요")
keyword = st.text_input('검색할 키워드를 입력하세요',label_visibility="hidden")

try:
    
    if type(keyword) == str:
        with st.spinner('Wait for it...'):
            naver_link = Naver_news(keyword)
            naver_main = Naver_title(keyword)
            num=1
            i = naver_link
            k = naver_main #여기엔 숫자대신 제목이 들어갈 예정
            link_dict = { name:value for name, value in zip(k,i)}
            st.markdown("**************")
            st.markdown("### 🧾보고싶은 뉴스를 선택해주세요!")
            selected = st.selectbox(' ',options = [t for t in k])

            selected_link = link_dict[selected]
            st.markdown("\n")
            st.markdown("\n")
            st.markdown("##### <뉴스 크기 조절>")
            w = st.slider('뉴스의 가로 크기 설정', 700, 1500)
            h = st.slider('뉴스의 세로 크기 설정', 700, 1500)

            st.markdown("\n")
            components.iframe(selected_link, width=w, height=h, scrolling=True)
                
        
        
except AttributeError:
    pass
