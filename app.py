
import streamlit as st
import google.generativeai as genai

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# --- 2. التحقق من الخزنة (Secrets) ---
# هذا الجزء سيعلمنا إذا كان التطبيق يرى المفتاح أم لا
if "GEMINI_API_KEY" in st.secrets:
    try:
        key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    except Exception as e:
        st.error(f"❌ الكود موجود ولكن جوجل ترفضه: {e}")
        api_ready = False
else:
    st.error("❌ التطبيق لا يرى أي مفتاح في خانة Secrets!")
    st.info("تأكد أنك كتبت GEMINI_API_KEY = 'كودك' في إعدادات Streamlit.")
    api_ready = False

# --- 3. نظام الدخول ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    pwd = st.text_input("الرمز السري (247):", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 4. واجهة العمل ---
if api_ready:
    st.success("✅ النظام متصل بذكاء جوجل وجاهز للعمل!")
    user_q = st.text_area("اسأل المستشار الآن:")
    if st.button("تحليل"):
        try:
            res = model.generate_content(user_q)
            st.info(res.text)
        except Exception as e:
            st.error(f"حدث خطأ أثناء المحادثة: {e}")
