import streamlit as st
import sqlite3
import datetime

# --- 1. 데이터베이스 세팅 (사진/영상 저장을 위한 필드 추가) ---
conn = sqlite3.connect('z_platform.db', check_same_thread=False)
c = conn.cursor()

# users: 회원정보, posts: 글내용 + 미디어데이터 + 미디어타입
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS posts (author TEXT, content TEXT, media BLOB, media_type TEXT, timestamp TEXT)')
conn.commit()

# --- 2. 앱 스타일링 (Z/Twitter 느낌의 다크 모드 UI) ---
st.set_page_config(page_title="Z - What's happening", page_icon="𝕏", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #1d9bf0; color: white; font-weight: bold; border: none; }
    .stTextArea>div>div>textarea { background-color: #16181c; color: white; border: 1px solid #333; border-radius: 15px; }
    .post-container { border-bottom: 1px solid #333; padding: 15px 0; }
    .author-name { font-weight: bold; color: #ffffff; font-size: 1.1em; }
    .timestamp { color: #71767b; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 세션 상태 관리 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# --- 4. 로직 함수 ---
def add_user(username, password):
    c.execute('INSERT INTO users VALUES (?,?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    return c.fetchone()

# --- 5. 사이드바 (로그인/가입) ---
with st.sidebar:
    st.title("𝕏 메뉴")
    if st.session_state.logged_in:
        st.write(f"**@{st.session_state.current_user}** 님")
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        choice = st.radio("접속", ["로그인", "회원가입"])
        u = st.text_input("아이디")
        p = st.text_input("비밀번호", type="password")
        if choice == "회원가입":
            if st.button("가입"):
                add_user(u, p)
                st.success("가입 완료!")
        else:
            if st.button("로그인"):
                if login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else:
                    st.error("정보 불일치")

# --- 6. 메인 화면 (게시글 작성) ---
st.title("𝕏")

if st.session_state.logged_in:
    with st.container():
        content = st.text_area("", placeholder="무슨 일이 일어나고 있나요?", height=100)
        # 사진 및 동영상 업로드 기능
        media_file = st.file_uploader("사진 또는 동영상 첨부", type=['png', 'jpg', 'jpeg', 'mp4', 'mov'])
        
        if st.button("게시하기"):
            if content or media_file:
                media_data = media_file.read() if media_file else None
                m_type = media_file.type if media_file else None
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                
                c.execute('INSERT INTO posts VALUES (?,?,?,?,?)', 
                          (st.session_state.current_user, content, media_data, m_type, now))
                conn.commit()
                st.rerun()
else:
    st.warning("로그인 후 이용 가능합니다.")

st.divider()

# --- 7. 타임라인 (Z 스타일 피드) ---
c.execute('SELECT * FROM posts ORDER BY timestamp DESC')
posts = c.fetchall()

for post in posts:
    author, text, media, m_type, ts = post
    with st.container():
        st.markdown(f"<div class='post-container'><span class='author-name'>{author}</span> <span class='timestamp'>· {ts}</span></div>", unsafe_allow_html=True)
        if text:
            st.write(text)
        
        # 미디어 출력 (사진 또는 영상)
        if media:
            if 'image' in m_type:
                st.image(media, use_container_width=True)
            elif 'video' in m_type:
                st.video(media)
        st.write("")