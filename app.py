import streamlit as st
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# جلب المفتاح من الخزنة السرية
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # تحديد الموديل بطريقة متوافقة مع كل النسخ
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    except:
        api_ready = False
else:
    api_ready = False

# نظام الدخول
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("الرمز السري (247):", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# الواجهة الرئيسية
if api_ready:
    st.success("✅ النظام متصل وجاهز للعمل!")
    user_q = st.text_area("اسأل المستشار الآن:")
    if st.button("تحليل ذكي"):
        if user_q:
            try:
                # محاولة طلب المحتوى
                response = model.generate_content(user_q)
                st.info(response.text)
            except Exception as e:
                # خطة بديلة في حال وجود مشكلة في نسخة المكتبة
                try:
                    alt_model = genai.GenerativeModel('gemini-pro')
                    response = alt_model.generate_content(user_q)
                    st.info(response.text)
                except:
                    st.error(f"يرجى عمل Reboot للتطبيق من إعدادات Streamlit: {e}")
