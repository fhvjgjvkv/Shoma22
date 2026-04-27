import streamlit as st
import google.generativeai as genai
import os

# إعداد الصفحة
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# جلب المفتاح
if "GEMINI_API_KEY" in st.secrets:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # التعديل الجوهري: محاولة استدعاء الموديل بأكثر من طريقة
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
        api_ready = True
    except Exception as e:
        st.error(f"خطأ في الإعدادات: {e}")
        api_ready = False
else:
    st.error("المفتاح مفقود من Secrets!")
    api_ready = False

# نظام الدخول (كلمة السر 247)
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("ادخل الرمز (247):", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# واجهة العمل
if api_ready:
    st.success("✅ النظام جاهز ومحدث")
    q = st.text_input("اسأل المستشار:")
    if st.button("تحليل"):
        if q:
            try:
                # حل نهائي لمشكلة v1beta عبر طلب المحتوى مباشرة
                response = model.generate_content(q)
                st.write(response.text)
            except Exception as e:
                st.error(f"الخلل: {e}")
                st.info("إذا ظهر خطأ 404، اضغط على Reboot App الآن.")
