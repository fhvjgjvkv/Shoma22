import streamlit as st
import pandas as pd
import json
import re
from groq import Groq

# 1. إعدادات الصفحة والستايل
st.set_page_config(page_title="SHOMA LAB PRO", layout="wide", page_icon="🔬")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button { 
        background: linear-gradient(45deg, #00ffcc, #0055ff); 
        color: white; border-radius: 10px; border: none; font-weight: bold; width: 100%;
    }
    .premium-card {
        background: linear-gradient(135deg, #1e2130 0%, #004444 100%);
        padding: 20px; border-radius: 15px; border: 2px solid #00ffcc; margin-bottom: 20px;
    }
    .tool-card { 
        background: #1e2130; padding: 15px; border-radius: 10px; 
        border-right: 5px solid #00ffcc; margin-bottom: 10px;
    }
    h1, h2, h3 { color: #00ffcc !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 2. تحميل البيانات (الوصفات)
@st.cache_data
def load_recipes():
    try:
        with open('recipes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

all_recipes = load_recipes()

# 3. تهيئة Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 4. نظام الدخول
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔬 SHOMA LAB PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("رمز الدخول:", type="password")
        if st.button("فتح المختبر"):
            if pwd == "247":
                st.session_state.auth = True
                st.rerun()
            else: st.error("الرمز خاطئ")
    st.stop()

# 5. القائمة الجانبية
with st.sidebar:
    st.markdown("<h3>⚖️ حاسبة المختبر</h3>", unsafe_allow_html=True)
    total_w = st.number_input("الوزن المطلوب (غرام):", min_value=1, value=1000)
    st.divider()
    if st.button("🗑️ مسح محادثات الذكاء"):
        st.session_state.chat_chem = []
        st.session_state.chat_gen = []
        st.rerun()
    st.caption("تطوير: شيماء علي عبد الحسين")

# 6. التبويبات (إضافة التبويبين للذكاء)
tabs = st.tabs(["⭐ المميزة", "📚 المستودع", "🧪 خبير الوصفات", "🤖 الذكاء العام", "🎓 الدراسة"])

# --- تبويب الوصفات المميزة ---
with tabs[0]:
    st.markdown("### 🌟 القائمة الذهبية")
    for r in all_recipes[:7]:
        with st.container():
            st.markdown(f"<div class='premium-card'><h4>{r['name']}</h4><p><b>المكونات:</b> {r['ing']}<br><i>{r['method']}</i></p></div>", unsafe_allow_html=True)
            with st.expander("حساب الأوزان"):
                parts = re.findall(r'([^,]+)\s+(\d+)%', r['ing'])
                if parts:
                    df = pd.DataFrame([{"المادة": p[0].strip(), "الوزن (g)": f"{(int(p[1])/100)*total_w:,.2f}"} for p in parts])
                    st.table(df)

# --- تبويب المستودع ---
with tabs[1]:
    search = st.text_input("🔍 بحث في المستودع:")
    for r in all_recipes:
        if search.lower() in r['name'].lower():
            with st.expander(f"🛠️ {r['name']}"):
                st.write(f"**المكونات:** {r['ing']}")
                parts = re.findall(r'([^,]+)\s+(\d+)%', r['ing'])
                if parts:
                    df = pd.DataFrame([{"المادة": p[0].strip(), "الوزن (g)": f"{(int(p[1])/100)*total_w:,.2f}"} for p in parts])
                    st.table(df)

# --- تبويب خبير الوصفات (يفهم تخصصك) ---
with tabs[2]:
    st.info("هذا الخبير مخصص فقط للكيمياء التجميلية وتطوير الوصفات.")
    if "chat_chem" not in st.session_state: st.session_state.chat_chem = []
    
    for m in st.session_state.chat_chem:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    p_chem = st.chat_input("اسألي عن مكون أو طريقة تحضير...")
    if p_chem:
        st.session_state.chat_chem.append({"role": "user", "content": p_chem})
        with st.chat_message("user"): st.markdown(p_chem)
        with st.chat_message("assistant"):
            # تزويد الذكاء بسياق تخصصك
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"أنت خبير كيمياء تجميلية محترف. وظيفتك مساعدة شيماء في تطوير تركيبات العناية بالبشرة والشعر."}] + st.session_state.chat_chem
            )
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_chem.append({"role": "assistant", "content": ans})

# --- تبويب الذكاء العام (لأي شيء آخر) ---
with tabs[3]:
    st.info("يمكنك سؤال هذا الخبير في أي مجال (دراسة، برمجة، معلومات عامة).")
    if "chat_gen" not in st.session_state: st.session_state.chat_gen = []
    
    for m in st.session_state.chat_gen:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    p_gen = st.chat_input("اسألي أي سؤال عام...")
    if p_gen:
        st.session_state.chat_gen.append({"role": "user", "content": p_gen})
        with st.chat_message("user"): st.markdown(p_gen)
        with st.chat_message("assistant"):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"أنت مساعد ذكي شامل وموسوعي."}] + st.session_state.chat_gen
            )
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_gen.append({"role": "assistant", "content": ans})

# --- تبويب الدراسة ---
with tabs[4]:
    st.markdown("### 🎓 أدوات الدراسة")
    tools = [
        {"n": "ChatGPT", "u": "https://chatgpt.com", "d": "مساعد دراسي."},
        {"n": "Perplexity", "u": "https://www.perplexity.ai", "d": "بحث أكاديمي."},
        {"n": "Gamma AI", "u": "https://gamma.app", "d": "للعروض التقديمية."}
    ]
    for t in tools:
        st.markdown(f"<div class='tool-card'><a href='{t['u']}' target='_blank' style='color:#00ffcc; text-decoration:none;'>🔗 {t['n']}</a><br>{t['d']}</div>", unsafe_allow_html=True)

st.caption("SHOMA LAB PRO © 2026")
