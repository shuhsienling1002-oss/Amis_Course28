import streamlit as st
import time
import random
from io import BytesIO

# --- 1. 核心相容性修復 ---
def safe_rerun():
    """自動判斷並執行重整"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except:
            st.stop()

def safe_play_audio(text):
    """語音播放安全模式"""
    try:
        from gtts import gTTS
        # 使用印尼語 (id) 發音
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.caption(f"🔇 (語音生成暫時無法使用)")

# --- 0. 系統配置 ---
st.set_page_config(page_title="Unit 28: O Wayway", page_icon="🌡️", layout="centered")

# --- CSS 美化 (鮮明橙色調) ---
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .source-tag { font-size: 12px; color: #aaa; text-align: right; font-style: italic; }
    
    /* 單字卡 */
    .word-card {
        background: linear-gradient(135deg, #FFF3E0 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 4px solid #FF9800;
    }
    .emoji-icon { font-size: 48px; margin-bottom: 10px; }
    .amis-text { font-size: 22px; font-weight: bold; color: #EF6C00; }
    .chinese-text { font-size: 16px; color: #7f8c8d; }
    
    /* 句子框 */
    .sentence-box {
        background-color: #FFF3E0;
        border-left: 5px solid #FFCC80;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
    }

    /* 按鈕 */
    .stButton>button {
        width: 100%; border-radius: 12px; font-size: 20px; font-weight: 600;
        background-color: #FFE0B2; color: #E65100; border: 2px solid #FF9800; padding: 12px;
    }
    .stButton>button:hover { background-color: #FFB74D; border-color: #F57C00; }
    .stProgress > div > div > div > div { background-color: #FF9800; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料庫 (Unit 28: 14個單字 - 句子提取核心詞) ---
vocab_data = [
    {"amis": "Adada", "chi": "痛 / 生病", "icon": "🤒", "source": "Row 470"},
    {"amis": "Maroray", "chi": "累 / 辛苦", "icon": "😫", "source": "Row 465"},
    {"amis": "Kaeso'", "chi": "好吃 / 美味", "icon": "😋", "source": "Row 353"},
    {"amis": "Takaraw", "chi": "高", "icon": "📏", "source": "Row 19"},
    {"amis": "Fa'edet", "chi": "熱", "icon": "🔥", "source": "Row 1690"},
    {"amis": "Si'enaw", "chi": "冷", "icon": "❄️", "source": "Row 254"},
    {"amis": "'Aloman", "chi": "多 (指人)", "icon": "👥", "source": "Row 323"},
    {"amis": "Adihay", "chi": "多 (指物)", "icon": "🔢", "source": "Row 470"},
    {"amis": "Tada", "chi": "非常 / 真正", "icon": "❗️", "source": "Row 2158"},
    {"amis": "Kakahad", "chi": "寬 / 寬闊", "icon": "↔️", "source": "Row 2158"},
    {"amis": "Fangsis", "chi": "香 / 香味", "icon": "🌸", "source": "Row 998"},
    {"amis": "Kohecal", "chi": "白 / 白色", "icon": "⚪", "source": "Row 221"},
    {"amis": "Miming", "chi": "小", "icon": "🤏", "source": "Row 221"},
    {"amis": "Tiyad", "chi": "肚子", "icon": "🤰", "source": "Row 470"},
]

# --- 句子庫 (7句: 嚴格源自 CSV 並移除連字號) ---
sentences = [
    {"amis": "Adihay ko mikaenan no mako, saka adada ko tiyad no mako.", "chi": "我吃的太多，所以我肚子痛。", "icon": "🤒", "source": "Row 470"},
    {"amis": "Kaeso' kora a titi a kaenen.", "chi": "那塊肉吃起來很美味。", "icon": "😋", "source": "Row 353"},
    {"amis": "Yo wawaho kako 'i, 'aloman ko tamdaw i niyaro'.", "chi": "當我小時候，在部落人很多。", "icon": "👥", "source": "Row 323"},
    {"amis": "Si'enaw ko romi'ad.", "chi": "天氣冷。", "icon": "❄️", "source": "Row 254"},
    {"amis": "Fa'edet ko romi'ad anini.", "chi": "今天天氣熱。", "icon": "🔥", "source": "Row 1690"},
    {"amis": "Tadakakahaday a riyar.", "chi": "非常寬闊的海洋。", "icon": "🌊", "source": "Row 2158"},
    {"amis": "Mimingay a kohecalay koni a fakeloh.", "chi": "這塊石頭又小又白。", "icon": "🪨", "source": "Row 221"},
]

# --- 3. 隨機題庫 (Synced) ---
raw_quiz_pool = [
    {
        "q": "Adihay ko mikaenan no mako, saka...",
        "audio": "Adihay ko mikaenan no mako, saka",
        "options": ["所以我肚子痛", "所以我很飽", "所以我很累"],
        "ans": "所以我肚子痛",
        "hint": "Adada ko tiyad (肚子痛) (Row 470)"
    },
    {
        "q": "Kaeso' kora a titi a kaenen.",
        "audio": "Kaeso' kora a titi a kaenen",
        "options": ["那塊肉很美味", "那塊肉很硬", "那塊肉很貴"],
        "ans": "那塊肉很美味",
        "hint": "Kaeso' (好吃) (Row 353)"
    },
    {
        "q": "單字測驗：Fa'edet",
        "audio": "Fa'edet",
        "options": ["熱", "冷", "涼"],
        "ans": "熱",
        "hint": "Row 1690: Fa'edet ko romi'ad (天氣熱)"
    },
    {
        "q": "單字測驗：'Aloman",
        "audio": "'Aloman",
        "options": ["人多", "物多", "錢多"],
        "ans": "人多",
        "hint": "'Aloman ko tamdaw (人很多) (Row 323)"
    },
    {
        "q": "Tadakakahaday a riyar.",
        "audio": "Tadakakahaday a riyar",
        "options": ["非常寬闊的海洋", "非常深的海", "非常藍的海"],
        "ans": "非常寬闊的海洋",
        "hint": "Kakahad (寬闊) (Row 2158)"
    },
    {
        "q": "單字測驗：Adada",
        "audio": "Adada",
        "options": ["痛/生病", "癢", "酸"],
        "ans": "痛/生病",
        "hint": "Adada ko tiyad (肚子痛)"
    },
    {
        "q": "單字測驗：Kohecal",
        "audio": "Kohecal",
        "options": ["白色", "黑色", "紅色"],
        "ans": "白色",
        "hint": "Row 221: ...kohecalay (白的)"
    },
    {
        "q": "單字測驗：Maroray",
        "audio": "Maroray",
        "options": ["累/辛苦", "快樂", "生氣"],
        "ans": "累/辛苦",
        "hint": "工作很久會 Maroray"
    }
]

# --- 4. 狀態初始化 (洗牌邏輯) ---
if 'init' not in st.session_state:
    st.session_state.score = 0
    st.session_state.current_q_idx = 0
    st.session_state.quiz_id = str(random.randint(1000, 9999))
    
    # 抽題與洗牌
    selected_questions = random.sample(raw_quiz_pool, 3)
    final_questions = []
    for q in selected_questions:
        q_copy = q.copy()
        shuffled_opts = random.sample(q['options'], len(q['options']))
        q_copy['shuffled_options'] = shuffled_opts
        final_questions.append(q_copy)
        
    st.session_state.quiz_questions = final_questions
    st.session_state.init = True

# --- 5. 主介面 ---
st.markdown("<h1 style='text-align: center; color: #EF6C00;'>Unit 28: O Wayway</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>狀態與形容 (Adjectives)</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📚 詞彙與句型", "🎲 隨機挑戰"])

# === Tab 1: 學習模式 ===
with tab1:
    st.subheader("📝 核心單字 (從句子提取)")
    col1, col2 = st.columns(2)
    for i, word in enumerate(vocab_data):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="word-card">
                <div class="emoji-icon">{word['icon']}</div>
                <div class="amis-text">{word['amis']}</div>
                <div class="chinese-text">{word['chi']}</div>
                <div class="source-tag">src: {word['source']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 聽發音", key=f"btn_vocab_{i}"):
                safe_play_audio(word['amis'])

    st.markdown("---")
    st.subheader("🗣️ 實用句型 (Data-Driven)")
    for i, s in enumerate(sentences):
        st.markdown(f"""
        <div class="sentence-box">
            <div style="font-size: 20px; font-weight: bold; color: #EF6C00;">{s['icon']} {s['amis']}</div>
            <div style="font-size: 16px; color: #555; margin-top: 5px;">{s['chi']}</div>
            <div class="source-tag">src: {s['source']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ 播放句型", key=f"btn_sent_{i}"):
            safe_play_audio(s['amis'])

# === Tab 2: 隨機挑戰模式 ===
with tab2:
    st.markdown("### 🎲 隨機評量")
    
    if st.session_state.current_q_idx < len(st.session_state.quiz_questions):
        q_data = st.session_state.quiz_questions[st.session_state.current_q_idx]
        
        st.progress((st.session_state.current_q_idx) / 3)
        st.markdown(f"**Question {st.session_state.current_q_idx + 1} / 3**")
        
        st.markdown(f"### {q_data['q']}")
        if q_data['audio']:
            if st.button("🎧 播放題目音檔", key=f"btn_audio_{st.session_state.current_q_idx}"):
                safe_play_audio(q_data['audio'])
        
        # 使用洗牌後的選項
        unique_key = f"q_{st.session_state.quiz_id}_{st.session_state.current_q_idx}"
        user_choice = st.radio("請選擇正確答案：", q_data['shuffled_options'], key=unique_key)
        
        if st.button("送出答案", key=f"btn_submit_{st.session_state.current_q_idx}"):
            if user_choice == q_data['ans']:
                st.balloons()
                st.success("🎉 答對了！")
                time.sleep(1)
                st.session_state.score += 100
                st.session_state.current_q_idx += 1
                safe_rerun()
            else:
                st.error(f"不對喔！提示：{q_data['hint']}")
                
    else:
        st.progress(1.0)
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background-color: #FFE0B2; border-radius: 20px; margin-top: 20px;'>
            <h1 style='color: #EF6C00;'>🏆 挑戰成功！</h1>
            <h3 style='color: #333;'>本次得分：{st.session_state.score}</h3>
            <p>你已經學會描述各種狀態了！</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再來一局 (重新抽題)", key="btn_restart"):
            st.session_state.score = 0
            st.session_state.current_q_idx = 0
            st.session_state.quiz_id = str(random.randint(1000, 9999))
            
            new_questions = random.sample(raw_quiz_pool, 3)
            final_qs = []
            for q in new_questions:
                q_copy = q.copy()
                shuffled_opts = random.sample(q['options'], len(q['options']))
                q_copy['shuffled_options'] = shuffled_opts
                final_qs.append(q_copy)
            
            st.session_state.quiz_questions = final_qs
            safe_rerun()
