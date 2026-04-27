import streamlit as st
import google.generativeai as genai

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SHOMA PRO LAB 112", layout="wide")

# --- 2. جلب المفتاح من الخزنة (Secrets) لضمان عدم الحظر ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # الحل لخطأ 404: نستخدم الاسم المباشر للموديل المستقر
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    except Exception as e:
        st.error(f"❌ مشكلة في الاتصال: {e}")
        api_ready = False
else:
    st.error("❌ المفتاح غير موجود في Secrets!")
    api_ready = False

# --- 3. نظام الدخول بالرمز السري ---
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

# --- 4. قاعدة بيانات الوصفات (الهجينة) ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "50ml هيدروسول إكليل الجبل، 5ml زيت خروع أسود.",
            "كيميائي": "Procapil 3%, Vitamin B5 1%.",
            "شرح": "1. إذابة البانثينول في الهيدروسول. 2. خلط الزيوت بمستحلب. 3. دمج المزيجين عند حرارة 40 درجة."
        },
        "ماسك السدر والكيراتين": {
            "طبيعي": "100g بودرة سدر منخول، زيت جوز هند.",
            "كيميائي": "Hydrolyzed Keratin 2%.",
            "شرح": "عجن السدر بالماء الدافئ ثم إضافة الكيراتين والزيوت وضربها بالخلاط."
        }
    },
    "2. الوجه (تفتيح ونضارة)": {
        "كريم لبان الذكر والأربوتين": {
            "طبيعي": "منقوع لبان ذكر مركز، زيت لوز مر.",
            "كيميائي": "Alpha Arbutin 2%, Kojic Acid 2%.",
            "شرح": "تسخين الطورين لـ 70 درجة، الدمج، وإضافة المواد الفعالة بعد التبريد لـ 40 درجة."
        }
    }
}

# --- 5. واجهة العمل والمستشارين ---
if api_ready:
    st.success("✅ النظام متصل وجاهز للعمل!")
    
    # أ- المستشار العام
    with st.expander("🤖 المستشار العام (SHOMA Global AI)"):
        user_q = st.text_area("اطرح سؤالك هنا (تداول، برمجة، كيمياء):")
        if st.button("تحليل ذكي"):
            if user_q:
                try:
                    res = model.generate_content(user_q)
                    st.info(res.text)
                except Exception:
                    # محاولة بديلة في حال وجود مشكلة في النسخة
                    res = genai.GenerativeModel('gemini-pro').generate_content(user_q)
                    st.info(res.text)

    st.divider()

    # ب- عرض الوصفات
    st.title("🔬 موسوعة الـ 112 وصفة")
    col_nav, col_details = st.columns([1, 2])

    with col_nav:
        st.subheader("🗂 الأقسام")
        cat = st.selectbox("اختر المنطقة:", list(DB_112.keys()))
        recipe_name = st.radio("المنتج:", list(DB_112[cat].keys()))

    with col_details:
        if recipe_name:
            data = DB_112[cat][recipe_name]
            st.header(f"✨ {recipe_name}")
            t1, t2 = st.tabs(["📝 المكونات", "🧪 الشرح الممل"])
            with t1:
                st.write(f"**🍀 طبيعي:** {data['طبيعي']}")
                st.write(f"**🧪 كيميائي:** {data['كيميائي']}")
            with t2:
                st.info(data['شرح'])
                
                # ج- المستشار الخاص بالوصفة
                st.markdown("---")
                st.subheader(f"🔍 مستشار وصفة {recipe_name}")
                local_q = st.text_input("اسأل عن تعديل هذه الوصفة:", key=f"q_{recipe_name}")
                if st.button("تحليل الوصفة"):
                    if local_q:
                        prompt = f"أنا أصنع وصفة {recipe_name}. مكوناتها هي: {data['طبيعي']} و {data['كيميائي']}. سؤالي هو: {local_q}"
                        res = model.generate_content(prompt)
                        st.success(res.text)
