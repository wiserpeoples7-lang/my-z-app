import streamlit as st
import sqlite3
import datetime
from PIL import Image

# 1. 데이터베이스 세팅
conn = sqlite3.connect('z_platform.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS posts (author TEXT, content TEXT, media BLOB, media_type TEXT, timestamp TEXT)')
conn.commit()

# 2. 세련된 X 스타일 디자인 입히기 (CSS)
st.set_page_config(page_title="Z-Academy", page_icon="🜔", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
        color: #E7E9EA;
    }
    
    /* 사이드바 다크톤 */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #2F3336;
    }

    /* 포스트 작성 박스 */
    .stTextArea textarea {
        background-color: transparent !important;
        border: none !important;
        color: #E7E9EA !important;
        font-size: 1.2rem !important;
    }
    
    /* 게시하기 버튼 (X 특유의 파란색) */
    div.stButton > button {
        background-color: #1D9BF0 !important;
        color: white !important;
        border-radius: 9999px !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        border: none !important;
        float: right;
    }

    /* 피드 컨테이너 스타일 */
    .post-card {
        border-bottom: 1px solid #2F3336;
        padding: 1.5rem 0.5rem;
    }
    
    .author-name {
        font-weight: bold;
        color: #E7E9EA;
        margin-right: 5px;
    }
    
    .username {
        color: #71767B;
        font-size: 0.9em;
    }

    /* 이미지 테두리 둥글게 */
    img {
        border-radius: 15px;
        border: 1px solid #2F3336;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 로그인 세션 관리
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# 4. 상단 네비게이션 느낌의 타이틀
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown("### **Home**")

# 5. 사이드바 로그인 로직
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🜔</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        menu = st.radio("Menu", ["Login", "Sign Up"])
        u = st.text_input("ID")
        p = st.text_input("PW", type="password")
        if st.button("GO"):
            if menu == "Sign Up":
                c.execute('INSERT INTO users VALUES (?,?)', (u, p))
                conn.commit()
                st.success("가입 완료!")
            else:
                c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p))
                if c.fetchone():
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
    else:
        st.write(f"**@{st.session_state.current_user}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# 6. 메인 피드 (글쓰기 영역)
if st.session_state.logged_in:
    with st.container():
        st.markdown(f"**@{st.session_state.current_user}**님이 작성 중")
        content = st.text_area("", placeholder="What's happening?", label_visibility="collapsed")
        media_file = st.file_uploader("", type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")
        
        if st.button("Post"):
            if content or media_file:
                m_data = media_file.read() if media_file else None
                m_type = media_file.type if media_file else None
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute('INSERT INTO posts VALUES (?,?,?,?,?)', 
                          (st.session_state.current_user, content, m_data, m_type, now))
                conn.commit()
                st.rerun()

st.divider()

# 7. 타임라인 리스트
c.execute('SELECT * FROM posts ORDER BY timestamp DESC')
posts = c.fetchall()

for post in posts:
    author, text, media, m_type, ts = post
    with st.container():
        # X 스타일 헤더 (이름 @아이디 · 시간)
        st.markdown(f"""
            <div class='post-card'>
                <span class='author-name'>{author}</span>
                <span class='username'>@{author} · {ts}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if text:
            st.write(text)
        
        if media:
            if 'image' in m_type:
                st.image(media)
            elif 'video' in m_type:
                st.video(media)
        st.write("")
