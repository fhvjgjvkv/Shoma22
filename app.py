import streamlit as st
import google.generativeai as genai

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# --- 2. جلب المفتاح وتحديد الموديل (تعديل الأمان) ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # الحل لخطأ 404: تجربة استدعاء الموديل بأكثر من صيغة لضمان التوافق
        try:
            model = genai.GenerativeModel('gemini-pro') # هذا الموديل هو الأكثر استقراراً للنسخ القديمة
        except:
            model = genai.GenerativeModel('models/gemini-pro')
        api_ready = True
    except Exception as e:
        st.error(f"❌ مشكلة في الإعدادات: {e}")
        api_ready = False
else:
    st.error("❌ المفتاح غير موجود في Secrets!")
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

# --- 4. قاعدة بيانات الوصفات ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "50ml هيدروسول إكليل الجبل، 5ml زيت خروع أسود.",
            "كيميائي": "Procapil 3%, Vitamin B5 1%.",
            "شرح": "إذابة البانثينول في الهيدروسول، ثم دمج الزيوت بمستحلب عند حرارة 40 درجة."
        }
    }
}

# --- 5. واجهة العمل والمستشارين ---
if api_ready:
    st.success("✅ النظام متصل بذكاء جوجل!")
    
    # أ- المستشار العام (في الأعلى)
    with st.expander("🤖 المستشار العام (SHOMA Global AI)"):
        user_q = st.text_area("اطرح سؤالك هنا:")
        if st.button("تحليل ذكي"):
            if user_q:
                try:
                    res = model.generate_content(user_q)
                    st.info(res.text)
                except Exception as e:
                    st.error(f"حدث خطأ في الاستجابة: {e}")

    st.divider()

    # ب- موسوعة الوصفات (هنا تظهر الأقسام والوصفات)
    st.title("🔬 موسوعة الـ 112 وصفة")
    cat = st.selectbox("اختر المنطقة:", list(DB_112.keys()))
    recipe_name = st.radio("المنتج:", list(DB_112[cat].keys()))

    if recipe_name:
        data = DB_112[cat][recipe_name]
        st.header(f"✨ {recipe_name}")
        t1, t2 = st.tabs(["📝 المكونات", "🧪 الشرح الممل"])
        with t1:
            st.write(f"**🍀 طبيعي:** {data['طبيعي']}")
            st.write(f"**🧪 كيميائي:** {data['كيميائي']}")
        with t2:
            st.info(data['شرح'])
