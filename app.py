import streamlit as st
import google.generativeai as genai

# --- 1. إعدادات النظام ---
st.set_page_config(page_title="SHOMA PRO LAB", layout="wide")

# --- 2. جلب المفتاح "طول العمر" من الخزنة السرية ---
# ملاحظة: يتم وضع المفتاح في إعدادات Streamlit Secrets وليس في الكود
try:
    if "GEMINI_API_KEY" in st.secrets:
        USER_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=USER_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_ready = True
    else:
        api_ready = False
except Exception:
    api_ready = False

# --- 3. نظام الدخول وحماية الرمز ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("أدخل الرمز السري (247):", type="password")
        if st.button("دخول للنظام"):
            if pwd == "247":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("الرمز السري خطأ!")
    st.stop()

# --- 4. قاعدة بيانات الـ 112 وصفة (هجين) ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "50ml هيدروسول إكليل الجبل، 5ml زيت خروع أسود، مستخلص القراص.",
            "كيميائي": "Procapil 3%, Vitamin B5 1%, Phenonip 0.5%.",
            "شرح ممل": "1. إذابة البانثينول في الهيدروسول. 2. خلط الزيوت مع مادة مستحلبة (Tween 20). 3. دمج المزيجين وإضافة البروكابيل والمادة الحافظة تحت درجة حرارة 40 مئوية."
        },
        "ماسك السدر والكيراتين": {
            "طبيعي": "100g بودرة سدر منخول، 20ml زيت جوز هند، 10ml زبدة شيا.",
            "كيميائي": "Hydrolyzed Keratin 2%, Cetyl Alcohol 1%.",
            "شرح ممل": "تذويب الزبدة والزيوت مع سيتيل الكحول، ثم دمجها مع عجينة السدر الدافئة وضربها بالخلاط للحصول على قوام كريمي."
        }
    },
    "2. الوجه (تفتيح ونضارة)": {
        "كريم لبان الذكر والأربوتين": {
            "طبيعي": "20g منقوع لبان ذكر مركز، زيت لوز مر.",
            "كيميائي": "Alpha Arbutin 2%, Kojic Acid 2%, Vitamin E 1%.",
            "شرح ممل": "تسخين الطورين لـ 70 درجة، الدمج بالمستحلب، ثم إضافة الأربوتين والكوجيك بعد تبريد المزيج لـ 40 درجة لضمان عدم تلف المواد."
        }
    }
    # يمكنك إضافة بقية الأقسام الـ 16 هنا بنفس النمط
}

# --- 5. الواجهة والمستشارين ---
if api_ready:
    # أ- المستشار العام (في الأعلى)
    st.markdown("### 🤖 المستشار العام (SHOMA Global AI)")
    with st.expander("فتح المستشار العام للمناقشة المفتوحة"):
        global_q = st.text_area("اطرح سؤالك هنا (تداول، برمجة، كيمياء):", key="global_ai")
        if st.button("تحليل عام"):
            if global_q:
                with st.spinner("جاري المعالجة..."):
                    res = model.generate_content(global_q)
                    st.info(res.text)
    
    st.divider()

    # ب- واجهة الوصفات
    st.title("🔬 موسوعة الـ 112 وصفة الهجينة")
    col_nav, col_details = st.columns([1, 2])

    with col_nav:
        st.subheader("🗂 الأقسام")
        cat = st.selectbox("اختر المنطقة:", list(DB_112.keys()))
        recipe_name = st.radio("المنتج:", list(DB_112[cat].keys()))

    with col_details:
        if recipe_name:
            data = DB_112[cat][recipe_name]
            st.header(f"✨ {recipe_name}")
            tab1, tab2 = st.tabs(["📝 المكونات", "🧪 الشرح الممل"])
            
            with tab1:
                st.success(f"**🍀 طبيعي:** {data['طبيعي']}")
                st.warning(f"**🧪 كيميائي:** {data['كيميائي']}")
            
            with tab2:
                st.info(f"**خطوات التحضير بالتفصيل:** {data['شرح ممل']}")
                
                # ج- المستشار الخاص (تحت كل وصفة)
                st.markdown("---")
                st.subheader(f"🔍 مستشار وصفة {recipe_name}")
                local_q = st.text_input(f"اسأل عن تعديل أو دمج مواد لهذه الوصفة:", key=f"q_{recipe_name}")
                if st.button(f"تحليل الوصفة"):
                    if local_q:
                        with st.spinner("جاري التحليل..."):
                            full_p = f"أنا أصنع {recipe_name}. المكونات: {data['طبيعي']} و {data['كيميائي']}. سؤالي: {local_q}"
                            res = model.generate_content(full_p)
                            st.success(res.text)
else:
    st.error("⚠️ لم يتم تفعيل مفتاح الـ API في 'الخزنة السرية' (Secrets) للتطبيق.")
    st.info("يرجى الذهاب لإعدادات التطبيق في Streamlit Cloud ووضع المفتاح في خانة Secrets.")

st.markdown("---")
st.caption("SHOMA Hybrid System v10.0 | نظام المستشار المزدوج المستقر")
