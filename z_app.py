import streamlit as st
import sqlite3
import datetime

# 1. 최고 관리자(원장님) 아이디 설정 (이 아이디로 가입하셔야 수정 권한이 생깁니다!)
ADMIN_ID = "wiser7" 

# 2. 데이터베이스 세팅 
conn = sqlite3.connect('z_platform.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS posts (author TEXT, content TEXT, media BLOB, media_type TEXT, timestamp TEXT)')
conn.commit()

# 3. Z-MAN 스타일 디자인 입히기
st.set_page_config(page_title="Z-MAN", page_icon="🦸‍♂️", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #000000; color: #E7E9EA; }
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #2F3336; }
    .stTextArea textarea { background-color: transparent !important; border: 1px solid #2F3336 !important; color: #E7E9EA !important; font-size: 1.1rem !important; }
    div.stButton > button { background-color: #1D9BF0 !important; color: white !important; border-radius: 9999px !important; font-weight: bold !important; border: none !important; }
    .post-card { border-bottom: 1px solid #2F3336; padding: 1.5rem 0.5rem; }
    .author-name { font-weight: bold; color: #E7E9EA; font-size: 1.1em; margin-right: 5px; }
    .username { color: #71767B; font-size: 0.9em; }
    img, video { border-radius: 15px; border: 1px solid #2F3336; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 4. 세션 상태 관리 (로그인 & 수정 상태 기억)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'editing_post_id' not in st.session_state:
    st.session_state.editing_post_id = None # 현재 수정 중인 글의 고유번호

# 5. 상단 타이틀
st.markdown("## **Z-MAN** 🦸‍♂️")

# 6. 사이드바 (로그인/가입)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Z-MAN</h2>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        menu = st.radio("Menu", ["Login", "Sign Up"])
        u = st.text_input("ID")
        p = st.text_input("PW", type="password")
        if st.button("GO"):
            if menu == "Sign Up":
                # 중복 확인
                c.execute('SELECT * FROM users WHERE username=?', (u,))
                if c.fetchone():
                    st.warning("이미 존재하는 아이디입니다.")
                else:
                    c.execute('INSERT INTO users VALUES (?,?)', (u, p))
                    conn.commit()
                    st.success("가입 완료! 로그인해주세요.")
            else:
                c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p))
                if c.fetchone():
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else:
                    st.error("정보 불일치")
    else:
        st.write(f"**@{st.session_state.current_user}** 님 환영합니다.")
        if st.session_state.current_user == ADMIN_ID:
            st.success("👑 최고 관리자 모드 활성화")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.editing_post_id = None
            st.rerun()

# 7. 메인 피드 (글쓰기 영역)
if st.session_state.logged_in:
    with st.container():
        content = st.text_area("", placeholder="새로운 소식이나 사진 영상들 남겨주세요!", label_visibility="collapsed")
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
else:
    st.info("왼쪽 메뉴에서 로그인 후 글을 작성할 수 있습니다.")

st.divider()

# 8. 타임라인 리스트 (관리자 수정 기능 포함)
# SQLite의 고유번호인 'rowid'를 불러와서 각 글을 식별합니다.
c.execute('SELECT rowid, author, content, media, media_type, timestamp FROM posts ORDER BY timestamp DESC')
posts = c.fetchall()

for post in posts:
    pid, author, text, media, m_type, ts = post
    
    with st.container():
        # X 스타일 헤더 및 관리자 전용 수정 버튼 영역
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown(f"<span class='author-name'>{author}</span> <span class='username'>@{author} · {ts}</span>", unsafe_allow_html=True)
        
        # 관리자(admin)에게만 [수정] 버튼이 보임
        with col2:
            if st.session_state.logged_in and st.session_state.current_user == ADMIN_ID:
                if st.button("✏️ 수정", key=f"edit_btn_{pid}"):
                    st.session_state.editing_post_id = pid
                    st.rerun()

        # 수정 모드일 때 보여질 화면
        if st.session_state.editing_post_id == pid:
            st.warning("글 수정 모드입니다.")
            new_text = st.text_area("내용 수정", value=text, key=f"edit_area_{pid}")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button("저장", key=f"save_{pid}"):
                    c.execute('UPDATE posts SET content=? WHERE rowid=?', (new_text, pid))
                    conn.commit()
                    st.session_state.editing_post_id = None
                    st.rerun()
            with sub_col2:
                if st.button("취소", key=f"cancel_{pid}"):
                    st.session_state.editing_post_id = None
                    st.rerun()
                    
        # 일반 모드일 때 보여질 화면
        else:
            if text:
                st.write(text)
            if media:
                if 'image' in m_type:
                    st.image(media)
                elif 'video' in m_type:
                    st.video(media)
                    
        st.markdown("<hr style='border:1px solid #2F3336; margin: 10px 0;'>", unsafe_allow_html=True)
