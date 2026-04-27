import streamlit as st
import google.generativeai as genai

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# --- 2. الربط الآمن مع Secrets (طول العمر) ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # الحل لخطأ 404/NotFound: نستخدم الموديل بمساره المباشر
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    except Exception:
        api_ready = False
else:
    api_ready = False

# --- 3. نظام الحماية ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    pwd = st.text_input("الرمز السري (247):", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 4. قاعدة بيانات الوصفات ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "50ml هيدروسول إكليل الجبل، 5ml زيت خروع أسود.",
            "كيميائي": "Procapil 3%, Vitamin B5 1%.",
            "شرح": "إذابة البانثينول في الهيدروسول، ثم دمج الزيوت بمستحلب عند حرارة 40."
        }
    }
}

# --- 5. واجهة العمل ---
if api_ready:
    st.success("✅ النظام متصل بذكاء جوجل!")
    
    # المستشار العام
    with st.expander("🤖 المستشار العام (المناقشة المفتوحة)"):
        user_q = st.text_area("اطرح سؤالك هنا:")
        if st.button("تحليل"):
            if user_q:
                # حل مشكلة الـ NotFound عبر محاولة بديلة (Fallback)
                try:
                    res = model.generate_content(user_q)
                    st.info(res.text)
                except:
                    # إذا فشل الموديل الأول، نجرب النسخة المستقرة الثانية
                    alt_model = genai.GenerativeModel('gemini-pro')
                    res = alt_model.generate_content(user_q)
                    st.info(res.text)

    st.divider()

    # موسوعة الوصفات
    st.title("🔬 موسوعة الـ 112 وصفة")
    cat = st.selectbox("الأقسام:", list(DB_112.keys()))
    recipe = st.radio("المنتج:", list(DB_112[cat].keys()))

    if recipe:
        data = DB_112[cat][recipe]
        st.header(f"✨ {recipe}")
        t1, t2 = st.tabs(["📝 المكونات", "🧪 الشرح الممل"])
        with t1:
            st.write(f"**🍀 طبيعي:** {data['طبيعي']}")
            st.write(f"**🧪 كيميائي:** {data['كيميائي']}")
        with t2:
            st.info(data['شرح'])
