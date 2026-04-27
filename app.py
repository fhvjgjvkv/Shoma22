import streamlit as st
import google.generativeai as genai

# --- إعدادات النظام ---
st.set_page_config(page_title="SHOMA Ultimate Hybrid", layout="wide")

# --- قاعدة بيانات الـ 112 وصفة (هجين: طبيعي + كيميائي) ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "50ml هيدروسول إكليل الجبل، 5ml زيت خروع أسود، مستخلص القراص.",
            "كيميائي": "Procapil 3%, Vitamin B5 1%, Phenonip 0.5%.",
            "شرح ممل": "1. إذابة البانثينول في الهيدروسول. 2. خلط الزيوت مع Solubilizer. 3. دمج المزيجين وإضافة البروكابيل والمادة الحافظة."
        },
        "ماسك السدر والكيراتين": {
            "طبيعي": "100g بودرة سدر، 20ml زيت جوز هند، 10ml زبدة شيا.",
            "كيميائي": "Hydrolyzed Keratin 2%, Cetyl Alcohol 1%.",
            "شرح ممل": "تذويب الزبدة والزيوت مع سيتيل الكحول، ثم دمجها مع عجينة السدر الدافئة بالخلاط."
        }
    },
    "2. الوجه (تفتيح ونضارة)": {
        "كريم لبان الذكر والأربوتين": {
            "طبيعي": "20g منقوع لبان ذكر مركز، 10ml زيت لوز مر.",
            "كيميائي": "Alpha Arbutin 2%, Kojic Acid 2%, Vitamin E 1%.",
            "شرح ممل": "تسخين الطورين لـ 70 درجة، الدمج بالمستحلب، ثم إضافة الأربوتين والكوجيك بعد أن تبرد الحرارة لـ 40 درجة."
        }
    }
}

# --- نظام الحماية (كلمة المرور مخفية) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("shoma_logo.png", width=200)
        pwd = st.text_input("أدخل الرمز السري:", type="password")
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 1. المستشار العام (في أعلى الصفحة - خانة مستقلة) ---
st.markdown("### 🤖 المستشار العام (SHOMA Global AI)")
api_key = "YOUR_API_KEY_HERE" # ضع مفتاحك هنا
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

with st.expander("فتح المستشار العام للمناقشة (خارج الوصفات)"):
    global_q = st.text_area("اسأل عن أي شيء (برمجة، تداول، كيمياء عامة):", key="global_ai")
    if st.button("تحليل عام"):
        if global_q:
            res = model.generate_content(global_q)
            st.info(res.text)

st.divider()

# --- الواجهة الرئيسية للوصفات ---
st.title("🔬 موسوعة الـ 112 وصفة الهجينة")

col_nav, col_details = st.columns([1, 2])

with col_nav:
    st.subheader("🗂 الأقسام الـ 16")
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
            st.info(f"**خطوات التحضير:** {data['شرح ممل']}")
            
            # --- 2. المستشار الخاص (تحت كل وصفة) ---
            st.markdown("---")
            st.subheader(f"🔍 مستشار وصفة {recipe_name}")
            local_q = st.text_input(f"اسأل المستشار عن تعديل هذه الوصفة:", key=f"q_{recipe_name}")
            if st.button(f"استشارة خاصة لـ {recipe_name}"):
                full_prompt = f"أنا أعمل على وصفة {recipe_name} المكونة من {data['طبيعي']} و {data['كيميائي']}. سؤالي هو: {local_q}"
                res = model.generate_content(full_prompt)
                st.success(res.text)

st.markdown("---")
st.caption("SHOMA Hybrid System v7.0 | نظام المستشار المزدوج والخصوصية التامة")
