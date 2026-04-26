import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعدادات الهوية الملكية (SHOMA SYSTEM)
st.set_page_config(page_title="SHOMA SYSTEM", layout="wide")

# إعداد مفتاح الـ API الخاص بك
GEMINI_KEY = "AIzaSyDG0uYFLO3nQ4SkPNgOYQOwTrRe6K3mAs4"
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #050505; color: #D4AF37; font-family: 'Cairo', sans-serif; direction: rtl; }
    .stTabs [aria-selected="true"] { background-color: #D4AF37 !important; color: black !important; font-weight: bold; }
    .recipe-card { border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; background-color: #0f0f0f; margin-bottom: 25px; border-right: 8px solid #D4AF37; }
    .header-text { text-align: center; color: #D4AF37; font-size: 1.8em; font-weight: bold; margin-top: 10px; }
    .stButton>button { background-color: #D4AF37; color: black; border-radius: 10px; font-weight: bold; width: 100%; }
    .calc-box { background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px dashed #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 2. الشعار والهوية الرسمية
col_img1, col_img2, col_img3 = st.columns([1,1,1])
with col_img2:
    try:
        logo = Image.open("shoma_logo.png")
        st.image(logo, use_column_width=True)
    except:
        st.info("ارفع ملف shoma_logo.png لتظهر صورتك هنا")
st.markdown("<p class='header-text'>من تطوير SHOMA</p>", unsafe_allow_html=True)

# 3. نظام الأمان (247)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.sidebar.text_input("أدخل الرمز السري للوصول:", type="password")
    if st.sidebar.button("فتح نظام SHOMA"):
        if pwd == "247": st.session_state.auth = True; st.rerun()
    st.stop()

# 4. الواجهة الرئيسية
tabs = st.tabs(["🩺 التشخيص والوصفات", "🧪 حاسبة التعادل", "📸 تحليل الرؤية", "📚 الموسوعة", "💬 المستشار البصري"])

# --- التبويب 1: التشخيص ---
with tabs[0]:
    st.subheader("📋 نموذج التشخيص الإلزامي")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("العمر:", min_value=0)
        skin = st.selectbox("نوع البشرة:", ["لم يتم الاختيار", "دهنية", "جافة", "مختلطة", "حساسة"])
    with c2:
        goal = st.text_input("الهدف الدقيق:")
        allergy = st.text_input("حساسية أو ملاحظات:")

    if age > 0 and skin != "لم يتم الاختيار" and len(goal) > 3:
        if st.button("توليد الوصفة المخصصة"):
            res = model.generate_content(f"أنت خبير SHOMA. صمم وصفة لـ {goal} تناسب عمر {age} وبشرة {skin}. اذكر الطريقة المملة والنتائج.")
            st.markdown(f"<div class='recipe-card'>{res.text}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ أكمل البيانات لفتح قسم الوصفات.")

# --- التبويب 2: حاسبة التعادل ---
with tabs[1]:
    st.subheader("⚖️ حاسبة تعادل الـ pH")
    acid_qty = st.number_input("كمية السلفونيك (بالجرام):", min_value=0.0)
    if st.button("احسب الصودا الكاوية"):
        soda = acid_qty * 0.145
        st.markdown(f"<div class='calc-box'>تحتاج تقريباً <b>{soda:.2f} جرام</b> صودا قشور لتعادل {acid_qty} جرام سلفونيك.</div>", unsafe_allow_html=True)

# --- التبويب 3: تحليل الرؤية ---
with tabs[2]:
    st.subheader("📸 رادار SHOMA للواقعية")
    img_now = st.file_uploader("الصورة الحالية", type=['jpg','png','jpeg'], key="v1")
    img_goal = st.file_uploader("صورة الهدف", type=['jpg','png','jpeg'], key="v2")
    if st.button("بدء تحليل الصور"):
        if img_now and img_goal:
            res = model.generate_content(["بصفتك خبير SHOMA، هل الهدف واقعي؟ قارن الصورتين وأعط خطة عمل.", Image.open(img_now), Image.open(img_goal)])
            st.write(res.text)

# --- التبويب 5: المستشار البصري (محدث لاستقبال صور) ---
with tabs[4]:
    st.subheader("💬 مستشار SHOMA الذكي")
    if "chat" not in st.session_state: st.session_state.chat = []
    
    chat_img = st.file_uploader("ارفع صورة للمستشار (اختياري):", type=['jpg','png','jpeg'])
    p = st.chat_input("اسأل SHOMA عن أي شيء...")
    
    if p:
        st.session_state.chat.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
            if chat_img: st.image(chat_img, width=250)
            
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..."):
                if chat_img:
                    res = model.generate_content([f"أنت مستشار مختبر SHOMA، حلل وأجب: {p}", Image.open(chat_img)])
                else:
                    res = model.generate_content(f"أنت مستشار مختبر SHOMA، أجب بموضوعية ودقة: {p}")
                st.markdown(res.text)
                st.session_state.chat.append({"role": "assistant", "content": res.text})
