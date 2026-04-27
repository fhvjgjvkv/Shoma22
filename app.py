import streamlit as st
import google.generativeai as genai

# --- إعدادات النظام الاحترافي ---
st.set_page_config(page_title="SHOMA Ultimate Hybrid", layout="wide")

# --- قاعدة بيانات الـ 112 وصفة (هجين: طبيعي + كيميائي) ---
DB_112 = {
    "1. الشعر (إنبات وترميم)": {
        "سيروم الروزماري والبروكابيل": {
            "طبيعي": "هيدروسول إكليل الجبل (50ml)، زيت خروع أسود (5ml)، مستخلص القراص.",
            "كيميائي": "Procapil 3%, Vitamin B5 (Panthenol) 1%, Phenonip 0.5%.",
            "شرح ممل للتحضير": "أولاً: نذيب البانثينول في هيدروسول الروزماري. ثانياً: نخلط الزيوت مع مادة (Solubilizer) لضمان عدم انفصال الزيت عن الماء. ثالثاً: ندمج المزيجين ونضيف البروكابيل والمادة الحافظة ونرج العبوة جيداً. يُحفظ في مكان بارد."
        },
        "ماسك السدر والكيراتين": {
            "طبيعي": "بودرة سدر منخول (100g)، زيت جوز هند (20ml)، زبدة شيا (10ml).",
            "كيميائي": "Hydrolyzed Keratin 2%, Cetyl Alcohol 1%.",
            "شرح ممل للتحضير": "نذيب الزبدة والزيوت مع الـ Cetyl Alcohol في حمام مائي (طور زيتي). نخلط السدر بماء دافئ (طور مائي). ندمج الطورين بالخلاط الكهربائي حتى يتحول لقوام كريمي، ثم نضيف الكيراتين بعد أن يبرد الخليط."
        }
    },
    "2. الوجه (تفتيح ونضارة)": {
        "كريم لبان الذكر والأربوتين": {
            "طبيعي": "منقوع لبان ذكر مركز (20g)، زيت لوز مر (10ml).",
            "كيميائي": "Alpha Arbutin 2%, Kojic Acid 2%, Vitamin E 1%.",
            "شرح ممل للتحضير": "نسخن الزيوت والماء لدرجة 70 مئوية. نستخدم مستحلب لدمجهم. ننتظر حتى تنخفض الحرارة لـ 40 درجة (مهم جداً) ثم نضيف الأربوتين والكوجيك أسيد وفيتامين E لضمان عدم تلف المواد الفعالة بالحرارة."
        }
    }
    # ملاحظة: يمكنك إضافة بقية الـ 16 قسم هنا بنفس الترتيب
}

# --- نظام الحماية (كلمة المرور مخفية) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center;'>🔐 نظام SHOMA المطور</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("shoma_logo.png", width=200)
        # كلمة المرور تظهر كنجوم الآن
        pwd = st.text_input("أدخل الرمز السري:", type="password")
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- خانة المستشار المنفصلة (Sidebar) ---
with st.sidebar:
    st.header("🤖 مستشار المختبر")
    st.write("اكتب سؤالك عن دمج المواد الطبيعية والكيميائية:")
    
    # حقل مفتاح الـ API
    api_key = st.text_input("API KEY (للمستشار):", type="password")
    
    user_q = st.text_area("سؤالك العلمي:", height=150)
    if st.button("استشر SHOMA"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"أنت خبير مختبرات تجميلية، اشرح بالتفصيل: {user_q}")
                st.info(res.text)
            except: st.error("تأكد من صحة الـ API Key")
        else: st.warning("يرجى إدخال مفتاح API أولاً")

# --- الواجهة الرئيسية للوصفات ---
st.title("🔬 موسوعة الـ 112 وصفة (هجين)")
st.divider()

col_nav, col_details = st.columns([1, 2])

with col_nav:
    st.subheader("🗂 الأقسام الـ 16")
    cat = st.selectbox("اختر المنطقة:", list(DB_112.keys()))
    recipe_name = st.radio("المنتج:", list(DB_112[cat].keys()))

with col_details:
    if recipe_name:
        data = DB_112[cat][recipe_name]
        st.header(f"✨ {recipe_name}")
        
        tab1, tab2 = st.tabs(["📝 المكونات الهجينة", "🧪 الشرح الممل للتحضير"])
        
        with tab1:
            st.success(f"**🍀 المكونات الطبيعية:** \n\n {data['طبيعي']}")
            st.warning(f"**🧪 المكونات الكيميائية:** \n\n {data['كيميائي']}")
        
        with tab2:
            st.info(f"**الخطوات بالتفصيل:** \n\n {data['شرح ممل للتحضير']}")

st.markdown("---")
st.caption("SHOMA Hybrid System v6.0 | تم إخفاء الرمز وتفعيل المستشار")
