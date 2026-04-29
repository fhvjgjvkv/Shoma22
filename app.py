import streamlit as st
import pandas as pd
import re
from groq import Groq
import base64
import json

# 1. إعدادات الهوية والواجهة
st.set_page_config(page_title="SHOMA LAB PRO", layout="wide", page_icon="🔬")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button { 
        background: linear-gradient(45deg, #00ffcc, #0055ff); 
        color: white; border-radius: 10px; border: none; font-weight: bold; width: 100%;
    }
    .stExpander { background-color: #1e2130; border: 1px solid #00ffcc; border-radius: 10px; }
    h1, h2, h3 { color: #00ffcc !important; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
</style>
""", unsafe_allow_html=True)

# 2. تهيئة محرك الذكاء الاصطناعي
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى ضبط مفتاح GROQ_API_KEY في إعدادات Secrets.")
    st.stop()

# 3. إدارة حالة التطبيق (الذاكرة وقاعدة البيانات الحية)
if "auth" not in st.session_state: st.session_state.auth = False
if "chat_recipes" not in st.session_state: st.session_state.chat_recipes = []
if "chat_general" not in st.session_state: st.session_state.chat_general = []

# --- قاعدة البيانات الـ 100 وصفة القابلة للتعديل ---
if "my_recipes" not in st.session_state:
    st.session_state.my_recipes = [
        # الشعر (1-15)
        {"name": "سيروم الروزماري والبروكابيل", "cat": "الشعر", "ing": "ماء 85%, بروكابيل 3%, جلسرين 10%, حافظة 2%", "method": "خلط بارد."},
        {"name": "شامبو البيوتين والبروتين", "cat": "الشعر", "ing": "قاعدة شامبو 90%, بيوتين 5%, كيراتين 5%", "method": "دمج تدريجي."},
        {"name": "ماسك السدر الملكي", "cat": "الشعر", "ing": "سدر 50%, منقوع إكليل جبل 40%, زيت جوجوبا 10%", "method": "علاج تساقط."},
        {"name": "سيروم الكافيين 5%", "cat": "الشعر", "ing": "ماء 90%, كافيين 5%, بانثينول 5%", "method": "تنشيط البصيلات."},
        {"name": "بلسم الكيراتين والحرير", "cat": "الشعر", "ing": "قاعدة بلسم 85%, كيراتين 10%, زيت أرغان 5%", "method": "ترميم."},
        {"name": "بخاخ الفلفل والزنجبيل", "cat": "الشعر", "ing": "ماء 90%, مستخلص فلفل 5%, زنجبيل 5%", "method": "تحفيز الدورة."},
        {"name": "زيت الثوم والجرجير", "cat": "الشعر", "ing": "زيت زيتون 70%, زيت ثوم 20%, فيتامين E 10%", "method": "تطويل."},
        {"name": "ماسك زبدة الشيا والمايونيز", "cat": "الشعر", "ing": "زبدة شيا 40%, مايونيز 50%, عسل 10%", "method": "ترطيب."},
        {"name": "بخاخ جل الصبار العضوي", "cat": "الشعر", "ing": "جل صبار 90%, ماء ورد 10%", "method": "ترطيب يومي."},
        {"name": "سيروم منع النفشة", "cat": "الشعر", "ing": "سيليكون 90%, زيت جوز هند 10%", "method": "تلميع."},
        {"name": "زيت القطران العلاجي", "cat": "الشعر", "ing": "زيت زيتون 90%, قطران 10%", "method": "علاج القشرة."},
        {"name": "ماسك المشاط الأحمر", "cat": "الشعر", "ing": "مشاط 50%, سدر 30%, زيت سمسم 20%", "method": "تطويل وتعطير."},
        {"name": "سيروم الببتيدات المكثف", "cat": "الشعر", "ing": "ماء 90%, ببتيدات 8%, حافظة 2%", "method": "تكثيف."},
        {"name": "تونيك الزعتر الجبلي", "cat": "الشعر", "ing": "ماء 80%, زعتر 10%, إكليل جبل 10%", "method": "تطهير الفروة."},
        {"name": "ماسك الحناء الزيتي", "cat": "الشعر", "ing": "حناء 60%, زيت لوز 30%, ليمون 10%", "method": "تغذية."},

        # التبييض (16-30)
        {"name": "كريم ألفا أربوتين 2%", "cat": "التبييض", "ing": "قاعدة كريم 80%, أربوتين 2%, عرقسوس 10%, نياسيناميد 8%", "method": "تفتيح."},
        {"name": "سيروم فيتامين سي 20%", "cat": "التبييض", "ing": "ماء 70%, فيتامين سي 20%, فيروليك 1%, جلسرين 9%", "method": "نضارة."},
        {"name": "ماسك النيلة المغربية", "cat": "التبييض", "ing": "نيلة 20%, زبادي 70%, نشا 10%", "method": "تفتيح فوري."},
        {"name": "كريم الكوجيك أسيد", "cat": "التبييض", "ing": "قاعدة كريم 90%, كوجيك 5%, ليمون 5%", "method": "علاج تصبغات."},
        {"name": "سيروم الترانيكساميك", "cat": "التبييض", "ing": "ماء 85%, ترانيكساميك 5%, نياسيناميد 10%", "method": "علاج الكلف."},
        {"name": "لوشن عرقسوس الجسم", "cat": "التبييض", "ing": "لوشن 80%, عرقسوس 20%", "method": "تفتيح الجسم."},
        {"name": "كريم الجلوتاثيون", "cat": "التبييض", "ing": "قاعدة 80%, جلوتاثيون 10%, فيتامين سي 10%", "method": "نضارة."},
        {"name": "جل المناطق الحساسة", "cat": "التبييض", "ing": "جل صبار 80%, عرقسوس 10%, بابونج 10%", "method": "آمن."},
        {"name": "ماسك الأرز والبودرة", "cat": "التبييض", "ing": "دقيق أرز 50%, ماء ورد 40%, حليب 10%", "method": "تنعيم."},
        {"name": "تونر الليمون للمسام", "cat": "التبييض", "ing": "ماء ورد 90%, ليمون 10%", "method": "قبض مسام."},
        {"name": "كريم بودرة اللؤلؤ", "cat": "التبييض", "ing": "لؤلؤ 10%, كريم مرطب 90%", "method": "نضارة ملكية."},
        {"name": "سيروم مستخلص التوت", "cat": "التبييض", "ing": "ماء 80%, مستخلص توت 20%", "method": "تفتيح طبيعي."},
        {"name": "لوشن البابايا الإنزيمي", "cat": "التبييض", "ing": "لوشن 80%, بابايا 20%", "method": "تنعيم."},
        {"name": "كريم الكركم واللبن", "cat": "التبييض", "ing": "كركم 10%, لبن 80%, عسل 10%", "method": "بهتان البشرة."},
        {"name": "ماسك القهوة الموحد", "cat": "التبييض", "ing": "قهوة 30%, نشا 30%, ماء ورد 40%", "method": "إزالة الإرهاق."},

        # التقشير (31-45)
        {"name": "مقشر AHA 30% القوي", "cat": "التقشير", "ing": "ماء 60%, جليكوليك 30%, جلسرين 10%", "method": "كيميائي."},
        {"name": "غسول الساليسيليك 2%", "cat": "التقشير", "ing": "منظف 95%, ساليسيليك 2%, شجرة شاي 3%", "method": "حب الشباب."},
        {"name": "مقشر القهوة والسكر", "cat": "التقشير", "ing": "سكر 40%, قهوة 40%, زيت لوز 20%", "method": "سنفرة."},
        {"name": "الطين المغربي المنقي", "cat": "التقشير", "ing": "طين 70%, ماء ورد 30%", "method": "تنظيف مسام."},
        {"name": "مقشر البابايا والأناناس", "cat": "التقشير", "ing": "بابايا 50%, أناناس 50%", "method": "تقشير بارد."},
        {"name": "تونر الجليكوليك 7%", "cat": "التقشير", "ing": "ماء 90%, جليكوليك 7%, ورد 3%", "method": "تجديد سطح البشرة."},
        {"name": "ملح الحليب والزيوت", "cat": "التقشير", "ing": "ملح 70%, حليب 20%, زيت لوز 10%", "method": "تفتيح ركب."},
        {"name": "ماسك الفحم والجيلاتين", "cat": "التقشير", "ing": "فحم 10%, جيلاتين 40%, ماء 50%", "method": "رؤوس سوداء."},
        {"name": "مقشر الشوفان الناعم", "cat": "التقشير", "ing": "شوفان 70%, حليب 30%", "method": "بشرة حساسة."},
        {"name": "سيروم اللاكتيك 10%", "cat": "التقشير", "ing": "ماء 85%, لاكتيك 10%, هيالورونيك 5%", "method": "تقشير وترطيب."},
        {"name": "سكراب اللافندر والملح", "cat": "التقشير", "ing": "ملح بحري 80%, لافندر 20%", "method": "استرخاء."},
        {"name": "الطين البركاني والخل", "cat": "التقشير", "ing": "طين 80%, خل تفاح 20%", "method": "سحب سموم."},
        {"name": "مقشر قشور الجوز", "cat": "التقشير", "ing": "جوز مطحون 20%, كريم 80%", "method": "مناطق خشنة."},
        {"name": "لوشن جلد الدجاجة", "cat": "التقشير", "ing": "لوشن 90%, ساليسيليك 5%, لاكتيك 5%", "method": "علاج Keratosis."},
        {"name": "مقشر الصودا والمنظف", "cat": "التقشير", "ing": "صودا 30%, غسول وجه 70%", "method": "تنظيف أنف."},

        # الجسم والترطيب (46-60)
        {"name": "لوشن اليوريا 10%", "cat": "الجسم", "ing": "قاعدة 85%, يوريا 10%, زيت زيتون 5%", "method": "خشونة شديدة."},
        {"name": "زبدة الشيا والكاكاو", "cat": "الجسم", "ing": "شيا 60%, كاكاو 20%, جوز هند 20%", "method": "ترطيب عميق."},
        {"name": "زيت التان والبرونز", "cat": "الجسم", "ing": "زيت جزر 50%, جوز هند 40%, لون 10%", "method": "تسمير."},
        {"name": "جل النعناع والبانثينول", "cat": "الجسم", "ing": "جل صبار 90%, نعناع 5%, بانثينول 5%", "method": "مبرد حروق."},
        {"name": "كريم الكولاجين والشد", "cat": "الجسم", "ing": "كولاجين 10%, بانثينول 10%, قاعدة 80%", "method": "شد تجاعيد."},
        {"name": "لوشن المسك والزيوت", "cat": "الجسم", "ing": "لوشن 90%, زيت مسك 10%", "method": "تعطير."},
        {"name": "كريم تفتيح المفاصل", "cat": "الجسم", "ing": "يوريا 20%, ساليسيليك 5%, قاعدة 75%", "method": "سواد مستعصي."},
        {"name": "زيت لمعان الجسم Glow", "cat": "الجسم", "ing": "زيت جاف 95%, مايكا 5%", "method": "لمعة ذهبية."},
        {"name": "زبدة الكاكاو للتمدد", "cat": "الجسم", "ing": "كاكاو 80%, فيتامين E 20%", "method": "علاج سترتش ماركس."},
        {"name": "لوشن الحليب والعسل", "cat": "الجسم", "ing": "حليب 10%, عسل 10%, قاعدة 80%", "method": "ترطيب ناعم."},
        {"name": "بخاخ اللافندر للنوم", "cat": "الجسم", "ing": "ماء 80%, زيت لافندر 20%", "method": "تعطير مفارش."},
        {"name": "سيروم كافيين للسيلوليت", "cat": "الجسم", "ing": "كافيين 10%, قرفة 5%, قاعدة 85%", "method": "شد جلد."},
        {"name": "لوشن فيتامين E المركز", "cat": "الجسم", "ing": "لوشن 95%, زيت فيتامين E 5%", "method": "ترميم."},
        {"name": "جل الحلبة لشد الجسم", "cat": "الجسم", "ing": "جل صبار 80%, زيت حلبة 20%", "method": "شد وتحسين مظهر."},
        {"name": "صابون النيلة والودع", "cat": "الجسم", "ing": "قاعدة صابون 90%, نيلة 10%", "method": "تنظيف تفتيح."},

        # العلاجيات (61-75)
        {"name": "مرهم الحروق والندبات", "cat": "علاجيات", "ing": "سمسم 80%, شمع نحل 20%", "method": "ترميم أنسجة."},
        {"name": "كريم الإكزيما", "cat": "علاجيات", "ing": "شيا 50%, بابونج 20%, زنك 30%", "method": "تهدئة."},
        {"name": "جل الفطريات", "cat": "علاجيات", "ing": "شجرة شاي 50%, زيت زيتون 50%", "method": "علاج فطريات."},
        {"name": "كريم الزنك للأطفال", "cat": "علاجيات", "ing": "زنك 40%, فازلين 60%", "method": "التهاب حفاظ."},
        {"name": "محلول المرة الطبيعي", "cat": "علاجيات", "ing": "ماء 90%, مرة 10%", "method": "تعقيم جروح."},
        {"name": "بخاخ المحلول الملحي", "cat": "علاجيات", "ing": "ماء 95%, ملح 5%", "method": "تطهير."},
        {"name": "مرهم الكبريت", "cat": "علاجيات", "ing": "كبريت 10%, فازلين 90%", "method": "تجفيف حبوب."},
        {"name": "جل الصبار والمنثول", "cat": "علاجيات", "ing": "صبار 90%, منثول 10%", "method": "تبريد لدغات."},
        {"name": "كريم كافور للمساج", "cat": "علاجيات", "ing": "منثول 10%, كافور 10%, قاعدة 80%", "method": "آلام مفاصل."},
        {"name": "علاج فطريات الأظافر", "cat": "علاجيات", "ing": "خل تفاح 50%, زيت شاي 50%", "method": "نقع."},
        {"name": "بودرة القدم المعقمة", "cat": "علاجيات", "ing": "تلك 70%, حمض بوريك 20%, نعناع 10%", "method": "روائح."},
        {"name": "مرهم اللانولين للتشقق", "cat": "علاجيات", "ing": "لانولين 50%, فازلين 50%", "method": "ترميم عميق."},
        {"name": "بخاخ الجيوب الأنفية", "cat": "علاجيات", "ing": "ماء 99%, ملح 1%", "method": "غسول أنفي."},
        {"name": "جل القرنفل للثة", "cat": "علاجيات", "ing": "قرنفل 10%, زيت زيتون 90%", "method": "تسكين أسنان."},
        {"name": "ماسك تهدئة الوردية", "cat": "علاجيات", "ing": "خيار 50%, طين أبيض 50%", "method": "تبريد محتقن."},

        # العطور (76-90)
        {"name": "مخمرية العود والمسك", "cat": "العطور", "ing": "فازلين 80%, عود 10%, صندل 10%", "method": "تعطير ثابت."},
        {"name": "عطر الشعر السيليكوني", "cat": "العطور", "ing": "سيليكون 90%, زيت عطري 10%", "method": "لمعان ورائحة."},
        {"name": "المسك الجامد الفاخر", "cat": "العطور", "ing": "شمع 30%, لوز 50%, مسك 20%", "method": "عطر صلب."},
        {"name": "بدي ميست الزهور", "cat": "العطور", "ing": "كحول 70%, ماء 20%, عطر 10%", "method": "بخاخ."},
        {"name": "عطر الزيوت النقي", "cat": "العطور", "ing": "جوجوبا 90%, مسك مركز 10%", "method": "ثبات عالي."},
        {"name": "فازلين اللافندر", "cat": "العطور", "ing": "فازلين 80%, لافندر 20%", "method": "مساج نوم."},
        {"name": "بخور المعمول الملكي", "cat": "العطور", "ing": "دقة عود 50%, زيوت 50%", "method": "تخمير."},
        {"name": "مكعبات المسك", "cat": "العطور", "ing": "برافين 50%, مسك 50%", "method": "تعطير خزانات."},
        {"name": "سبراي ماء الورد", "cat": "العطور", "ing": "ماء ورد 95%, زيت ورد 5%", "method": "انتعاش."},
        {"name": "عطر الأطفال المائي", "cat": "العطور", "ing": "ماء 95%, زيت مائي 5%", "method": "آمن."},
        {"name": "المسك المتسلق المخملي", "cat": "العطور", "ing": "فازلين 80%, ورد طائفي 20%", "method": "مناطق حساسة."},
        {"name": "بودرة الجسم بالياسمين", "cat": "العطور", "ing": "نشا 70%, ياسمين 30%", "method": "جفاف ورائحة."},
        {"name": "زيت المساج الاسترخائي", "cat": "العطور", "ing": "لوز حلو 90%, لافندر 10%", "method": "استرخاء."},
        {"name": "مخمرية بودرة النظافة", "cat": "العطور", "ing": "فازلين 80%, عطر بودرة 20%", "method": "رائحة نظافة."},
        {"name": "زيت الفواحة المركز", "cat": "العطور", "ing": "كحول 80%, زيت عطري 20%", "method": "تعطير جو."},

        # الصابون والقدم (91-100)
        {"name": "صابون النيلة والكركم", "cat": "صابون", "ing": "صابون 90%, نيلة 5%, كركم 5%", "method": "تفتيح الجسم."},
        {"name": "غسول اليد المعقم", "cat": "صابون", "ing": "صابون سائل 95%, شجرة شاي 5%", "method": "تعقيم."},
        {"name": "صابون الفحم والليمون", "cat": "صابون", "ing": "صابون 95%, فحم 5%", "method": "بشرة دهنية."},
        {"name": "شاور جل التوت والكرز", "cat": "صابون", "ing": "قاعدة صابون 90%, توت 10%", "method": "استحمام منعش."},
        {"name": "مقشر اليوريا 40%", "cat": "القدم", "ing": "يوريا 40%, فازلين 40%, ساليسيليك 20%", "method": "تشقق قدم قاسي."},
        {"name": "أملاح نقع القدم", "cat": "القدم", "ing": "ماء 70%, ملح إبسوم 20%, خل 10%", "method": "فطريات."},
        {"name": "كريم توريد كعب القدم", "cat": "القدم", "ing": "فازلين 95%, دم غزال 5%", "method": "لون وردي."},
        {"name": "سبراي إزالة رائحة القدم", "cat": "القدم", "ing": "كحول 80%, منثول 20%", "method": "تعقيم حذاء."},
        {"name": "سكراب ملح القدم", "cat": "القدم", "ing": "ملح 60%, زيت لوز 30%, ليمون 10%", "method": "سنفرة خشنة."},
        {"name": "سيروم الخروع للأظافر", "cat": "القدم", "ing": "خروع 90%, فيتامين E 10%", "method": "تقوية."}
    ]

# 4. نظام الدخول
if not st.session_state.auth:
    st.markdown("<h1>🔬 SHOMA LAB PRO</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل الرمز السري للمختبر (247):", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
        else: st.error("الرمز غير صحيح.")
    st.stop()

# 5. القائمة الجانبية (إضافة وحسابات)
with st.sidebar:
    st.markdown("### ⚖️ حاسبة المختبر")
    total_w = st.number_input("الوزن الإجمالي (غرام):", min_value=1, value=1000)
    
    st.divider()
    st.markdown("### ➕ إضافة وصفة جديدة")
    with st.form("add_recipe", clear_on_submit=True):
        n_name = st.text_input("الاسم:")
        n_cat = st.selectbox("القسم:", ["الشعر", "التبييض", "التقشير", "الجسم", "علاجيات", "العطور", "صابون", "القدم"])
        n_ing = st.text_area("المكونات والنسب:")
        n_meth = st.text_area("الطريقة:")
        if st.form_submit_button("حفظ بالمستودع"):
            if n_name and n_ing:
                st.session_state.my_recipes.append({"name": n_name, "cat": n_cat, "ing": n_ing, "method": n_meth})
                st.rerun()

    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.chat_recipes = []
        st.session_state.chat_general = []
        st.rerun()

# 6. الأقسام
tabs = st.tabs(["📚 المستودع الحي (100+)", "🧪 خبير التركيبات AI", "🤖 الخبير العام AI"])

# --- التبويب الأول: إدارة الـ 100 وصفة ---
with tabs[0]:
    query = st.text_input("🔍 ابحث في الـ 100 وصفة الحية:")
    for i, r in enumerate(st.session_state.my_recipes):
        if query.lower() in r['name'].lower() or query.lower() in r['cat'].lower():
            with st.expander(f"🛠️ تعديل: {r['name']} - [{r['cat']}]"):
                col1, col2 = st.columns(2)
                with col1:
                    u_name = st.text_input("الاسم", value=r['name'], key=f"un_{i}")
                    u_ing = st.text_area("المكونات", value=r['ing'], key=f"ui_{i}")
                    u_meth = st.text_area("الطريقة", value=r['method'], key=f"um_{i}")
                    if st.button("حفظ التغييرات", key=f"sv_{i}"):
                        st.session_state.my_recipes[i] = {"name": u_name, "cat": r['cat'], "ing": u_ing, "method": u_meth}
                        st.success("تم!")
                        st.rerun()
                with col2:
                    st.markdown("**الأوزان المحسوبة:**")
                    parts = u_ing.split(',')
                    c_data = []
                    for p in parts:
                        match = re.search(r'(\d+)%', p)
                        if match:
                            perc = int(match.group(1))
                            w = (perc / 100) * total_w
                            c_data.append({"المادة": p.split(str(perc))[0].strip(), "الوزن (g)": f"{w:,.2f}"})
                    if c_data: st.table(pd.DataFrame(c_data))
                    if st.button("🗑️ حذف نهائي", key=f"dl_{i}"):
                        st.session_state.my_recipes.pop(i)
                        st.rerun()

# --- التبويب الثاني والثالث للذكاء الاصطناعي ---
with tabs[1]:
    for m in st.session_state.chat_recipes:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    r_img = st.file_uploader("📸 صور:", accept_multiple_files=True, key="img_r")
    r_txt = st.chat_input("اسأل خبير التركيبات...")
    if r_txt:
        st.session_state.chat_recipes.append({"role": "user", "content": r_txt})
        with st.chat_message("user"): st.markdown(r_txt)
        with st.chat_message("assistant"):
            db_ctx = json.dumps(st.session_state.my_recipes, ensure_ascii=False)
            sys_p = {"role": "system", "content": f"أنت خبير كيمياء تجميلية. مستودعك الحالي: {db_ctx}. تذكر السياق."}
            msgs = [sys_p] + st.session_state.chat_recipes
            if r_img:
                content = [{"type": "text", "text": r_txt}]
                for im in r_img:
                    enc = base64.b64encode(im.read()).decode('utf-8')
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{enc}"}})
                msgs[-1]["content"] = content
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_recipes.append({"role": "assistant", "content": ans})

with tabs[2]:
    for m in st.session_state.chat_general:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    g_img = st.file_uploader("📸 صور تحاليل/أكواد:", accept_multiple_files=True, key="img_g")
    g_txt = st.chat_input("اسأل في أي مجال...")
    if g_txt:
        st.session_state.chat_general.append({"role": "user", "content": g_txt})
        with st.chat_message("user"): st.markdown(g_txt)
        with st.chat_message("assistant"):
            sys_g = {"role": "system", "content": "أنت خبير شامل (طبيب ومبرمج). مطور من قبل شيماء علي عبد الحسين. تذكر السياق."}
            msgs = [sys_g] + st.session_state.chat_general
            if g_img:
                content = [{"type": "text", "text": g_txt}]
                for im in g_img:
                    enc = base64.b64encode(im.read()).decode('utf-8')
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{enc}"}})
                msgs[-1]["content"] = content
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_general.append({"role": "assistant", "content": ans})

st.markdown("---")
st.caption("SHOMA LAB PRO © 2026 | تطوير: شيماء علي عبد الحسين")
