import streamlit as st
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# محاولة جلب المفتاح من الخزنة السرية (Secrets)
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    except:
        api_ready = False
else:
    api_ready = False

# نظام الدخول
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("الرمز السري (247):", type="password")
        if st.button("دخول"):
            if pwd == "247":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("الرمز خطأ")
    st.stop()

# واجهة التطبيق
if api_ready:
    st.title("🤖 المستشار الخبير")
    user_q = st.text_area("اسأل المستشار عن أي شيء:")
    if st.button("تحليل"):
        if user_q:
            try:
                with st.spinner("جاري التحليل..."):
                    res = model.generate_content(user_q)
                    st.success(res.text)
            except Exception as e:
                st.error("المفتاح الذي وضعته في Secrets تم تعطيله. استبدله بمفتاح جديد.")
else:
    st.error("⚠️ النظام متوقف! المفتاح غير موجود في الخزنة السرية (Secrets).")
    st.info("يجب وضع المفتاح في إعدادات Streamlit Cloud وليس في الكود.")
