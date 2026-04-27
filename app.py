import streamlit as st
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# --- محاولة الاتصال بالذكاء الاصطناعي من الخزنة ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    except:
        api_ready = False
else:
    api_ready = False

# --- نظام الدخول بالرمز السري ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("الرمز السري (247):", type="password")
        if st.button("دخول للنظام"):
            if pwd == "247":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("الرمز خطأ!")
    st.stop()

# --- واجهة البوت الشامل ---
if api_ready:
    st.title("🤖 مستشار SHOMA (يعمل طول العمر)")
    
    # 1. المستشار العام
    with st.expander("فتح المستشار العام للمناقشة"):
        user_q = st.text_area("اسأل عن التداول، البرمجة، أو الكيمياء:")
        if st.button("تحليل ذكي"):
            if user_q:
                with st.spinner("جاري التحليل..."):
                    res = model.generate_content(user_q)
                    st.success(res.text)
    
    st.divider()

    # 2. موسوعة الوصفات
    st.title("🔬 موسوعة الـ 112 وصفة")
    st.info("النظام الآن مربوط بالخزنة السرية وجاهز للعمل.")
else:
    st.error("⚠️ المفتاح غير موجود في Secrets!")
    st.info("اتبع الخطوة الثانية لوضع المفتاح في الخزنة.")
