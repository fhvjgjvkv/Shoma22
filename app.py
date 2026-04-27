import streamlit as st
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="SHOMA PRO LAB")

# المفتاح المباشر اللي دزيته بالصورة
MY_API_KEY = "AIzaSyC8amNz4ybtlws6avJIujei3v1j2S6a5XI"

try:
    genai.configure(api_key=MY_API_KEY)
    # استخدام اسم الموديل بدون كلمة models/ لتجنب تعارض النسخ
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_ready = True
except Exception as e:
    st.error(f"خطأ في الاتصال: {e}")
    api_ready = False

# نظام الدخول البسيط
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("الرمز السري (247):", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# واجهة العمل
if api_ready:
    st.success("✅ النظام متصل بالمفتاح المباشر وجاهز!")
    user_q = st.text_area("اطرح سؤالك هنا:")
    if st.button("تحليل ذكي"):
        if user_q:
            try:
                res = model.generate_content(user_q)
                st.info(res.text)
            except Exception as e:
                # إذا رجع خطأ الـ 404، نستخدم الموديل المستقر القديم
                try:
                    alt_model = genai.GenerativeModel('gemini-pro')
                    res = alt_model.generate_content(user_q)
                    st.info(res.text)
                except:
                    st.error("السيرفر يحتاج إعادة تشغيل (Reboot) بعد تعديل المتطلبات.")
