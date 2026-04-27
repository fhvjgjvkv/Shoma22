import streamlit as st
import google.generativeai as genai

# --- 1. إعدادات النظام ---
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# --- 2. إدارة مفتاح الـ API (طول العمر) ---
# يحاول الكود القراءة من Secrets أولاً
if "GEMINI_API_KEY" in st.secrets:
    USER_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    USER_API_KEY = "AIzaSyBD_ferBMo7o_3_RvdjAfpph2bJg_B0mMQ" # مفتاحك الأخير

try:
    genai.configure(api_key=USER_API_KEY)
    # استخدام موديل مستقر ومعروف
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_ready = True
except:
    api_ready = False

# --- 3. نظام الحماية ---
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

# --- 4. قاعدة البيانات (هجين) ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "50ml هيدروسول إكليل الجبل، 5ml زيت خروع أسود، مستخلص القراص.",
            "كيميائي": "Procapil 3%, Vitamin B5 1%, Phenonip 0.5%.",
            "شرح ممل": "1. إذابة البانثينول في الهيدروسول. 2. خلط الزيوت مع مادة مستحلبة (Tween 20). 3. دمج المزيجين وإضافة البروكابيل والمادة الحافظة تحت درجة حرارة 40 مئوية."
        }
    }
}

# --- 5. الواجهة والمستشارين ---
if api_ready:
    st.title("🤖 المستشار العام")
    with st.expander("فتح المستشار العام"):
        global_q = st.text_area("سؤالك العام:")
        if st.button("تحليل ذكي"):
            if global_q:
                try:
                    res = model.generate_content(global_q)
                    st.info(res.text)
                except Exception as e:
                    st.error("حدث خطأ في الاتصال، تأكد من سلامة المفتاح.")

    st.divider()
    st.title("🔬 موسوعة الـ 112 وصفة")
    
    cat = st.selectbox("الأقسام:", list(DB_112.keys()))
    recipe_name = st.radio("المنتج:", list(DB_112[cat].keys()))

    if recipe_name:
        data = DB_112[cat][recipe_name]
        st.header(f"✨ {recipe_name}")
        t1, t2 = st.tabs(["📝 المكونات", "🧪 الشرح الممل"])
        with t1:
            st.success(f"طبيعي: {data['طبيعي']}\n\nكيميائي: {data['كيميائي']}")
        with t2:
            st.info(data['شرح ممل'])
            st.markdown("---")
            st.subheader(f"🔍 مستشار وصفة {recipe_name}")
            local_q = st.text_input("اسأل عن تعديل هذه الوصفة:", key=f"q_{recipe_name}")
            if st.button("استشارة خاصة"):
                if local_q:
                    try:
                        res = model.generate_content(f"وصفة {recipe_name}: {local_q}")
                        st.success(res.text)
                    except:
                        st.error("خطأ في معالجة الطلب.")
else:
    st.error("خطأ في إعدادات الـ API")
