import streamlit as st
import pandas as pd
import re
from groq import Groq
import base64
import json

# 1. الإعدادات العامة للبرنامج والهوية
st.set_page_config(page_title="SHOMA LAB PRO", layout="wide", page_icon="🔬")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button { 
        background: linear-gradient(45deg, #00ffcc, #0055ff); 
        color: white; border-radius: 10px; border: none; font-weight: bold;
    }
    .stExpander { background-color: #1e2130; border: 1px solid #00ffcc; border-radius: 10px; }
    h1, h2, h3 { color: #00ffcc !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 2. تفعيل الذكاء الاصطناعي
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى إضافة GROQ_API_KEY في الإعدادات.")
    st.stop()

# 3. إدارة الجلسة والأمان
if "auth" not in st.session_state: st.session_state.auth = False
if "chat_recipes" not in st.session_state: st.session_state.chat_recipes = []
if "chat_general" not in st.session_state: st.session_state.chat_general = []

if not st.session_state.auth:
    st.markdown("<h1>🔬 SHOMA LAB PRO</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل الرمز السري:", type="password")
    if st.button("دخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
        else: st.error("خطأ.")
    st.stop()

# 4. قاعدة البيانات الشاملة (100 وصفة)
all_recipes = [
    # --- قسم الشعر ---
    {"name": "سيروم الروزماري والبروكابيل", "cat": "الشعر", "ing": "ماء 85%, بروكابيل 3%, جلسرين 10%, حافظة 2%", "method": "خلط بارد للإنبات."},
    {"name": "شامبو البيوتين", "cat": "الشعر", "ing": "قاعدة شامبو 90%, بيوتين 5%, زيت خروع 5%", "method": "إضافة تدريجية."},
    {"name": "ماسك السدر الملكي", "cat": "الشعر", "ing": "سدر 50%, منقوع إكليل جبل 40%, زيت جوجوبا 10%", "method": "علاج تساقط."},
    {"name": "بلسم الكيراتين", "cat": "الشعر", "ing": "قاعدة بلسم 85%, كيراتين 10%, زيت أرغان 5%", "method": "ترميم."},
    {"name": "سيروم الكافيين 5%", "cat": "الشعر", "ing": "ماء 90%, كافيين 5%, بانثينول 5%", "method": "تنشيط الفروة."},
    {"name": "بخاخ الفلفل المنبت", "cat": "الشعر", "ing": "ماء 90%, مستخلص فلفل 5%, زنجبيل 5%", "method": "تحفيز."},
    {"name": "زيت الثوم المركز", "cat": "الشعر", "ing": "زيت زيتون 70%, زيت ثوم 20%, فيتامين E 10%", "method": "تطويل."},
    {"name": "ماسك الشيا والمايونيز", "cat": "الشعر", "ing": "زبدة شيا 40%, مايونيز شعر 50%, عسل 10%", "method": "ترطيب."},
    {"name": "بخاخ جل الصبار", "cat": "الشعر", "ing": "جل صبار 90%, ماء ورد 10%", "method": "انتعاش."},
    {"name": "سيروم منع النفشة", "cat": "الشعر", "ing": "سيليكون 90%, زيت جوز هند 5%, عطر 5%", "method": "تلميع."},
    {"name": "زيت القطران للقشرة", "cat": "الشعر", "ing": "زيت زيتون 90%, قطران 10%", "method": "للقشرة."},
    {"name": "ماسك المشاط", "cat": "الشعر", "ing": "مشاط 50%, سدر 30%, زيت سمسم 20%", "method": "تطويل."},
    {"name": "سيروم الببتيدات", "cat": "الشعر", "ing": "ماء 90%, ببتيدات 8%, حافظة 2%", "method": "تكثيف."},
    {"name": "تونيك الزعتر", "cat": "الشعر", "ing": "ماء 80%, زعتر 10%, إكليل جبل 10%", "method": "تطهير."},
    {"name": "ماسك الحناء بالوسط الزيتي", "cat": "الشعر", "ing": "حناء 60%, زيت لوز 30%, ليمون 10%", "method": "تغذية."},

    # --- قسم التبييض والوجه ---
    {"name": "كريم ألفا أربوتين 2%", "cat": "التبييض", "ing": "قاعدة كريم 80%, أربوتين 2%, عرقسوس 10%, نياسيناميد 8%", "method": "تفتيح."},
    {"name": "سيروم فيتامين سي 20%", "cat": "التبييض", "ing": "ماء 70%, فيتامين سي 20%, فيروليك 1%, جلسرين 9%", "method": "نضارة."},
    {"name": "ماسك النيلة المغربية", "cat": "التبييض", "ing": "نيلة 20%, زبادي 70%, نشا 10%", "method": "تفتيح فوري."},
    {"name": "كريم الكوجيك أسيد", "cat": "التبييض", "ing": "قاعدة كريم 90%, كوجيك 5%, ليمون 5%", "method": "تصبغات."},
    {"name": "سيروم الترانيكساميك", "cat": "التبييض", "ing": "ماء 85%, ترانيكساميك 5%, نياسيناميد 10%", "method": "للكلف."},
    {"name": "لوشن العرقسوس المركز", "cat": "التبييض", "ing": "لوشن 80%, عرقسوس 20%", "method": "للجسم."},
    {"name": "كريم الجلوتاثيون", "cat": "التبييض", "ing": "قاعدة 80%, جلوتاثيون 10%, فيتامين سي 10%", "method": "أكسدة."},
    {"name": "جل المناطق الحساسة", "cat": "التبييض", "ing": "جل صبار 80%, عرقسوس 10%, بابونج 10%", "method": "آمن."},
    {"name": "ماسك الأرز والحليب", "cat": "التبييض", "ing": "دقيق أرز 50%, ماء ورد 40%, حليب 10%", "method": "نعومة."},
    {"name": "تونر الليمون المسامي", "cat": "التبييض", "ing": "ماء ورد 90%, ليمون 10%", "method": "مسام."},
    {"name": "كريم اللؤلؤ الطبيعي", "cat": "التبييض", "ing": "بودرة لؤلؤ 10%, كريم مرطب 90%", "method": "نضارة."},
    {"name": "سيروم التوت البري", "cat": "التبييض", "ing": "ماء 80%, مستخلص توت 20%", "method": "طبيعي."},
    {"name": "لوشن البابايا المبيض", "cat": "التبييض", "ing": "لوشن 80%, إنزيم بابايا 20%", "method": "تنعيم."},
    {"name": "كريم الكركم العلاجي", "cat": "التبييض", "ing": "كركم 10%, لبن 80%, عسل 10%", "method": "توحيد لون."},
    {"name": "ماسك القهوة والنشا", "cat": "التبييض", "ing": "قهوة 30%, نشا 30%, ماء ورد 40%", "method": "نضارة."},

    # --- قسم التقشير ---
    {"name": "مقشر AHA 30%", "cat": "التقشير", "ing": "ماء 60%, جليكوليك 30%, جلسرين 10%", "method": "تقشير قوي."},
    {"name": "غسول الساليسيليك 2%", "cat": "التقشير", "ing": "منظف 95%, ساليسيليك 2%, شجرة شاي 3%", "method": "لحب الشباب."},
    {"name": "مقشر القهوة والسكر", "cat": "التقشير", "ing": "سكر 40%, قهوة 40%, زيت لوز 20%", "method": "جسم."},
    {"name": "الطين المغربي المنقي", "cat": "التقشير", "ing": "طين 70%, ماء ورد 30%", "method": "تنظيف."},
    {"name": "مقشر إنزيم البابايا", "cat": "التقشير", "ing": "بودرة بابايا 50%, بودرة أناناس 50%", "method": "بارد."},
    {"name": "تونر الجليكوليك 7%", "cat": "التقشير", "ing": "ماء 90%, جليكوليك 7%, ورد 3%", "method": "تجديد."},
    {"name": "ملح الحليب للجسم", "cat": "التقشير", "ing": "ملح 70%, حليب بودرة 20%, زيت 10%", "method": "نعومة."},
    {"name": "ماسك الفحم النشط", "cat": "التقشير", "ing": "فحم 10%, جيلاتين 40%, ماء 50%", "method": "رؤوس سوداء."},
    {"name": "مقشر الشوفان للحساسة", "cat": "التقشير", "ing": "شوفان 70%, حليب 30%", "method": "هدوء."},
    {"name": "سيروم اللاكتيك أسيد", "cat": "التقشير", "ing": "ماء 85%, لاكتيك 10%, هيالورونيك 5%", "method": "ترطيب."},
    {"name": "سكراب اللافندر والملح", "cat": "التقشير", "ing": "ملح 80%, لافندر 20%", "method": "استرخاء."},
    {"name": "الطين البركاني", "cat": "التقشير", "ing": "طين 80%, خل تفاح 20%", "method": "سموم."},
    {"name": "مقشر قشور الجوز", "cat": "التقشير", "ing": "جوز 20%, كريم 80%", "method": "خشن."},
    {"name": "لوشن جلد الدجاجة (KP)", "cat": "التقشير", "ing": "لوشن 90%, ساليسيليك 5%, لاكتيك 5%", "method": "تقشير جسم."},
    {"name": "مقشر بيكربونات الصودا", "cat": "التقشير", "ing": "صودا 30%, غسول 70%", "method": "تنظيف أنف."},

    # --- قسم الجسم والترطيب ---
    {"name": "لوشن اليوريا 10%", "cat": "الجسم", "ing": "قاعدة 85%, يوريا 10%, زيت 5%", "method": "خشونة."},
    {"name": "زبدة الشيا المخفوقة", "cat": "الجسم", "ing": "شيا 60%, كاكاو 20%, جوز هند 20%", "method": "ترطيب."},
    {"name": "زيت التان الطبيعي", "cat": "الجسم", "ing": "جزر 50%, جوز هند 40%, لون 10%", "method": "شمس."},
    {"name": "جل النعناع المبرد", "cat": "الجسم", "ing": "صبار 95%, زيت نعناع 5%", "method": "تبريد."},
    {"name": "كريم الكولاجين للشد", "cat": "الجسم", "ing": "كولاجين 10%, قاعدة 90%", "method": "شد."},
    {"name": "لوشن المسك الأبيض", "cat": "الجسم", "ing": "لوشن 90%, مسك 10%", "method": "تعطير."},
    {"name": "كريم تفتيح الركب", "cat": "الجسم", "ing": "يوريا 20%, ساليسيليك 5%, قاعدة 75%", "method": "سواد."},
    {"name": "زيت لمعان الجسم", "cat": "الجسم", "ing": "زيت 95%, مايكا 5%", "method": "لمعان."},
    {"name": "زبدة الكاكاو للتشققات", "cat": "الجسم", "ing": "كاكاو 80%, فيتامين E 20%", "method": "تمدد."},
    {"name": "لوشن الحليب والعسل", "cat": "الجسم", "ing": "حليب 10%, عسل 10%, قاعدة 80%", "method": "يومي."},
    {"name": "بخاخ النوم الهادئ", "cat": "الجسم", "ing": "ماء 80%, لافندر 20%", "method": "مفارش."},
    {"name": "سيروم شد السيلوليت", "cat": "الجسم", "ing": "كافيين 10%, قرفة 5%, قاعدة 85%", "method": "مساج."},
    {"name": "لوشن فيتامين E المركز", "cat": "الجسم", "ing": "لوشن 95%, فيتامين E 5%", "method": "ترميم."},
    {"name": "جل شد الصدر", "cat": "الجسم", "ing": "صبار 80%, حلبة 20%", "method": "شد."},
    {"name": "صابون النيلة والودع", "cat": "الجسم", "ing": "صابون 90%, نيلة 10%", "method": "تبييض."},

    # --- قسم العلاجيات ---
    {"name": "مرهم الحروق الطبيعي", "cat": "علاجيات", "ing": "زيت سمسم 80%, شمع نحل 20%", "method": "ترميم."},
    {"name": "كريم الإكزيما المهدئ", "cat": "علاجيات", "ing": "شيا 50%, بابونج 20%, زنك 30%", "method": "تهدئة."},
    {"name": "جل فطريات الجلد", "cat": "علاجيات", "ing": "شجرة شاي 50%, زيت زيتون 50%", "method": "دهان."},
    {"name": "كريم الزنك للأطفال", "cat": "علاجيات", "ing": "زنك 40%, فازلين 60%", "method": "حماية."},
    {"name": "محلول المرة المعقم", "cat": "علاجيات", "ing": "ماء 90%, مرة 10%", "method": "تعقيم."},
    {"name": "بخاخ الملح للجروح", "cat": "علاجيات", "ing": "ماء 95%, ملح 5%", "method": "تطهير."},
    {"name": "مرهم الكبريت للحبوب", "cat": "علاجيات", "ing": "كبريت 10%, فازلين 90%", "method": "تجفيف."},
    {"name": "مرهم لدغات الحشرات", "cat": "علاجيات", "ing": "صبار 90%, منثول 10%", "method": "تبريد."},
    {"name": "كريم مسكن العضلات", "cat": "علاجيات", "ing": "منثول 10%, كافور 10%, قاعدة 80%", "method": "مساج."},
    {"name": "علاج فطريات الأظافر", "cat": "علاجيات", "ing": "خل تفاح 50%, زيت شاي 50%", "method": "نقع."},
    {"name": "بودرة القدم المعقمة", "cat": "علاجيات", "ing": "تلك 70%, بوريك 20%, نعناع 10%", "method": "تجفيف."},
    {"name": "مرهم علاج التشققات", "cat": "علاجيات", "ing": "لانولين 50%, فازلين 50%", "method": "ترميم."},
    {"name": "بخاخ الأنف الملحي", "cat": "علاجيات", "ing": "ماء 99%, ملح 1%", "method": "تنظيف."},
    {"name": "جل تسكين اللثة", "cat": "علاجيات", "ing": "قرنفل 10%, زيت زيتون 90%", "method": "تسكين."},
    {"name": "ماسك الوردية المبرد", "cat": "علاجيات", "ing": "خيار 50%, طين أبيض 50%", "method": "تبريد."},

    # --- قسم العطور والمخمرية ---
    {"name": "مخمرية العود الملكي", "cat": "العطور", "ing": "فازلين 80%, عود 10%, صندل 10%", "method": "ثبات."},
    {"name": "عطر الشعر اللامع", "cat": "العطور", "ing": "سيليكون 90%, زيت فرنسي 10%", "method": "لمعان."},
    {"name": "المسك الجامد", "cat": "العطور", "ing": "شمع 30%, لوز 50%, مسك 20%", "method": "تذويب."},
    {"name": "بدي ميست منعش", "cat": "العطور", "ing": "كحول 70%, ماء 20%, عطر 10%", "method": "رذاذ."},
    {"name": "عطر خلف الأذن", "cat": "العطور", "ing": "جوجوبا 90%, مسك 10%", "method": "ثبات."},
    {"name": "لافندر الاسترخاء", "cat": "العطور", "ing": "فازلين 80%, لافندر 20%", "method": "هدوء."},
    {"name": "بخور المعمول الدوسري", "cat": "العطور", "ing": "دقة عود 50%, زيوت 50%", "method": "تخمير."},
    {"name": "مكعبات المسك للملابس", "cat": "العطور", "ing": "شمع 50%, مسك 50%", "method": "تعطير."},
    {"name": "سبراي الورد الجوري", "cat": "العطور", "ing": "ماء ورد 95%, ورد 5%", "method": "انتعاش."},
    {"name": "عطر الأطفال المائي", "cat": "العطور", "ing": "ماء 95%, زيت مائي 5%", "method": "آمن."},
    {"name": "المسك المتسلق", "cat": "العطور", "ing": "فازلين 80%, ورد 20%", "method": "زكية."},
    {"name": "بودرة الجسم المعطرة", "cat": "العطور", "ing": "نشا 70%, مسك 30%", "method": "جفاف."},
    {"name": "زيت المساج العطري", "cat": "العطور", "ing": "لوز 90%, ياسمين 10%", "method": "استرخاء."},
    {"name": "مخمرية بودرة النظافة", "cat": "العطور", "ing": "فازلين 80%, عطر بودرة 20%", "method": "نظافة."},
    {"name": "عطر الفواحة المركز", "cat": "العطور", "ing": "كحول 80%, عطر 20%", "method": "تركيز."},

    # --- قسم الصابون والعناية بالقدم ---
    {"name": "صابون النيلة والكركم", "cat": "صابون", "ing": "قاعدة 90%, نيلة 10%", "method": "تفتيح."},
    {"name": "غسول اليد المعقم", "cat": "صابون", "ing": "قاعدة 95%, زيت شاي 5%", "method": "حماية."},
    {"name": "صابون الفحم والليمون", "cat": "صابون", "ing": "قاعدة 95%, فحم 5%", "method": "دهنية."},
    {"name": "شاور جل التوت", "cat": "صابون", "ing": "قاعدة 90%, توت 10%", "method": "انتعاش."},
    {"name": "مقشر اليوريا 40%", "cat": "القدم", "ing": "يوريا 40%, فازلين 40%, ساليسيليك 20%", "method": "تشققات."},
    {"name": "أملاح نقع القدم", "cat": "القدم", "ing": "ماء 70%, ملح 20%, خل 10%", "method": "فطريات."},
    {"name": "كريم توريد القدم", "cat": "القدم", "ing": "فازلين 95%, دم غزال 5%", "method": "توريد."},
    {"name": "سبراي رائحة القدم", "cat": "القدم", "ing": "كحول 80%, منثول 20%", "method": "تعقيم."},
    {"name": "سكراب القدم الخشن", "cat": "القدم", "ing": "ملح 60%, زيت 30%, ليمون 10%", "method": "إزالة."},
    {"name": "سيروم تقوية الأظافر", "cat": "القدم", "ing": "خروع 90%, فيتامين E 10%", "method": "تقوية."}
]

# 5. الواجهة الجانبية (الحاسبة)
with st.sidebar:
    st.markdown("<h3>⚖️ حاسبة الوزن الكلي</h3>", unsafe_allow_html=True)
    total_w = st.number_input("الوزن المطلوب (غرام):", min_value=1, value=1000)
    st.divider()
    if st.button("🗑️ تفريغ الذاكرة"):
        st.session_state.chat_recipes = []
        st.session_state.chat_general = []
        st.rerun()

# 6. الأقسام (Tabs)
tabs = st.tabs(["📚 مستودع الوصفات (100)", "🧪 خبير التركيبات (AI)", "🤖 الخبير العام (AI)"])

# تبويب الوصفات والعرض
with tabs[0]:
    search = st.text_input("🔍 ابحث في الـ 100 وصفة:")
    filtered = [r for r in all_recipes if search.lower() in r['name'].lower() or search.lower() in r['cat'].lower()]
    for r in filtered:
        with st.expander(f"✨ {r['name']} - [{r['cat']}]"):
            parts = r['ing'].split(',')
            calc_data = []
            for p in parts:
                match = re.search(r'(\d+)%', p)
                if match:
                    perc = int(match.group(1))
                    weight = (perc / 100) * total_w
                    calc_data.append({"المادة": p.split(str(perc))[0].strip(), "الوزن (g)": f"{weight:,.2f}"})
            st.table(pd.DataFrame(calc_data))

# تبويب خبير التركيبات (يدعم صور متعددة)
with tabs[1]:
    st.info("🧪 هذا القسم مرتبط بقاعدة الوصفات ويفهم مكوناتها.")
    for msg in st.session_state.chat_recipes:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    r_imgs = st.file_uploader("📸 ارفع صور المكونات (متعدد):", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="rcp_img")
    r_in = st.chat_input("اسأل عن أي وصفة أو اطلب تحليل الصور...")
    
    if r_in:
        st.session_state.chat_recipes.append({"role": "user", "content": r_in})
        with st.chat_message("user"): st.markdown(r_in)
        with st.chat_message("assistant"):
            ctx = json.dumps(all_recipes, ensure_ascii=False)
            payload = [{"type": "text", "text": f"أنت خبير في هذه الوصفات: {ctx}. أجب بدقة وعلمية وحلل الصور المرفقة."}]
            payload.append({"type": "text", "text": r_in})
            if r_imgs:
                for img in r_imgs:
                    encoded = base64.b64encode(img.read()).decode('utf-8')
                    payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}})
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": payload}])
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_recipes.append({"role": "assistant", "content": ans})

# تبويب الخبير العام (يدعم صور متعددة)
with tabs[2]:
    st.info("🤖 خبير في البرمجة، التحاليل الطبية، وكافة المجالات.")
    for msg in st.session_state.chat_general:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    g_imgs = st.file_uploader("📸 ارفع صور التحاليل أو الأكواد (متعدد):", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="gen_img")
    g_in = st.chat_input("اسأل في أي موضوع...")
    
    if g_in:
        st.session_state.chat_general.append({"role": "user", "content": g_in})
        with st.chat_message("user"): st.markdown(g_in)
        with st.chat_message("assistant"):
            payload = [{"type": "text", "text": "أنت خبير شامل مطور من قبل شيماء علي عبد الحسين. أجب بوضوح ودقة وموضوعية وبلا مجاملة."}]
            payload.append({"type": "text", "text": g_in})
            if g_imgs:
                for img in g_imgs:
                    encoded = base64.b64encode(img.read()).decode('utf-8')
                    payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}})
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": payload}])
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_general.append({"role": "assistant", "content": ans})

st.markdown("---")
st.caption("SHOMA LAB PRO © 2026 | تطوير: شيماء علي عبد الحسين")
