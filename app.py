import streamlit as st
import pandas as pd
import re
from groq import Groq
import base64
import json

# 1. إعدادات الواجهة والجمالية
st.set_page_config(page_title="SHOMA LAB PRO", layout="wide", page_icon="🔬")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button { 
        background: linear-gradient(45deg, #00ffcc, #0055ff); 
        color: white; border-radius: 10px; border: none; font-weight: bold; width: 100%;
    }
    .stExpander { background-color: #161b22; border: 1px solid #00ffcc; border-radius: 10px; margin-bottom: 10px; }
    h1, h2, h3 { color: #00ffcc !important; text-align: center; font-family: 'Arial'; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stDataFrame { background-color: #1e2130; }
</style>
""", unsafe_allow_html=True)

# 2. تهيئة محرك الذكاء الاصطناعي
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى إضافة GROQ_API_KEY في إعدادات المنصة.")
    st.stop()

# 3. إدارة الجلسة والبيانات
if "auth" not in st.session_state: st.session_state.auth = False
if "chat_recipes" not in st.session_state: st.session_state.chat_recipes = []
if "chat_general" not in st.session_state: st.session_state.chat_general = []

# --- المستودع الكامل (الوصفات المميزة + الـ 100 وصفة) ---
if "my_recipes" not in st.session_state:
    st.session_state.my_recipes = [
        # ⭐ الوصفات المميزة (الجديدة)
        {"name": "التقشير البارد المنزلي (Retinoid Boost)", "cat": "الوجه", "ing": "Differin (Adapalene) 50%, Panthenol 50%", "method": "تجديد الطبقة القرنية وعلاج المسام والتصبغات. ليلاً فقط."},
        {"name": "تبييض المناطق الخشنة (الركب والأكواع)", "cat": "الجسم", "ing": "Glyco-A (12%) 50%, Lipobase 50%", "method": "إذابة الخلايا الميتة وعلاج جلد الدجاجة (KP)."},
        {"name": "التحفيز الكيميائي للبصيلات (Aminexil+)", "cat": "الشعر", "ing": "Vichy Dercos 98%, زيت نعناع مركز 2%", "method": "منع تصلب الكولاجين وتوسيع الأوعية الدموية."},
        {"name": "التركيبة الثلاثية الآمنة (المناطق الحساسة)", "cat": "تبييض", "ing": "Alpha Arbutin 40%, Beesline 40%, بودرة تلك 20%", "method": "توقيف إنتاج الصبغة دون تهييج الجلد."},
        {"name": "بديل لاتيس (للرموش والحواجب)", "cat": "علاجيات", "ing": "زيت خروع جمايكي 70%, نواة تمر محمصة 30%", "method": "زيادة كثافة الشعرة وإطالة عمرها."},
        {"name": "الفيلر الموضعي (المسمنات)", "cat": "علاجيات", "ing": "زيت حلبة مركز 70%, Omega 3 30%", "method": "تحفيز الامتلاء الموضعي بالتدليك المستمر."},
        {"name": "التثبيت الجزيئي للعطور", "cat": "عطور", "ing": "فازلين طبي 40%, زيت جليسرين 30%, عطر خام 30%", "method": "تثبيت الرائحة ومنع تبخر الكحول."},
        
        # 📚 مجموعة الشعر (1-15)
        {"name": "سيروم الروزماري والبروكابيل", "cat": "الشعر", "ing": "ماء 85%, بروكابيل 3%, جلسرين 10%, حافظة 2%", "method": "إنبات الفراغات."},
        {"name": "شامبو البيوتين والبروتين", "cat": "الشعر", "ing": "قاعدة شامبو 90%, بيوتين 5%, كيراتين 5%", "method": "تقوية الشعر الضعيف."},
        {"name": "ماسك السدر الملكي", "cat": "الشعر", "ing": "سدر 50%, منقوع إكليل جبل 40%, جوجوبا 10%", "method": "كثافة وتطهير."},
        {"name": "سيروم الكافيين 5%", "cat": "الشعر", "ing": "ماء 90%, كافيين 5%, بانثينول 5%", "method": "تنشيط البصيلات."},
        {"name": "بلسم الكيراتين والحرير", "cat": "الشعر", "ing": "قاعدة بلسم 85%, كيراتين 10%, زيت أرغان 5%", "method": "تنعيم وترميم."},
        {"name": "بخاخ الفلفل والزنجبيل", "cat": "الشعر", "ing": "ماء 90%, مستخلص فلفل 5%, زنجبيل 5%", "method": "تحفيز الدورة الدموية."},
        {"name": "زيت الثوم والجرجير", "cat": "الشعر", "ing": "زيت زيتون 70%, زيت ثوم 20%, فيتامين E 10%", "method": "تطويل مكثف."},
        {"name": "ماسك زبدة الشيا والمايونيز", "cat": "الشعر", "ing": "شيا 40%, مايونيز 50%, عسل 10%", "method": "ترطيب الشعر الجاف."},
        {"name": "بخاخ جل الصبار العضوي", "cat": "الشعر", "ing": "جل صبار 90%, ماء ورد 10%", "method": "تهدئة وترطيب."},
        {"name": "سيروم منع النفشة", "cat": "الشعر", "ing": "سيليكون 90%, زيت جوز هند 10%", "method": "تلميع وحماية."},
        {"name": "زيت القطران العلاجي", "cat": "الشعر", "ing": "زيت زيتون 90%, قطران 10%", "method": "علاج القشرة."},
        {"name": "ماسك المشاط الأحمر", "cat": "الشعر", "ing": "مشاط 50%, سدر 30%, زيت سمسم 20%", "method": "تطويل وتعطير."},
        {"name": "سيروم الببتيدات المكثف", "cat": "الشعر", "ing": "ماء 90%, ببتيدات 8%, حافظة 2%", "method": "زيادة الكثافة."},
        {"name": "تونيك الزعتر الجبلي", "cat": "الشعر", "ing": "ماء 80%, زعتر 10%, إكليل جبل 10%", "method": "تطهير الفروة."},
        {"name": "ماسك الحناء الزيتي", "cat": "الشعر", "ing": "حناء 60%, زيت لوز 30%, ليمون 10%", "method": "تغذية ولون."},

        # 📚 مجموعة تبييض ونضارة (16-30)
        {"name": "كريم ألفا أربوتين 2%", "cat": "تبييض", "ing": "قاعدة 80%, أربوتين 2%, عرقسوس 10%, نياسيناميد 8%", "method": "تفتيح آمن."},
        {"name": "سيروم فيتامين سي 20%", "cat": "تبييض", "ing": "ماء 70%, فيتامين سي 20%, فيروليك 1%, جلسرين 9%", "method": "نضارة ومحاربة أكسدة."},
        {"name": "ماسك النيلة المغربية", "cat": "تبييض", "ing": "نيلة 20%, زبادي 70%, نشا 10%", "method": "تفتيح فوري للجسم."},
        {"name": "كريم الكوجيك أسيد", "cat": "تبييض", "ing": "قاعدة 90%, كوجيك 5%, ليمون 5%", "method": "علاج تصبغات قوية."},
        {"name": "سيروم الترانيكساميك", "cat": "تبييض", "ing": "ماء 85%, ترانيكساميك 5%, نياسيناميد 10%", "method": "علاج الكلف والنمش."},
        {"name": "لوشن عرقسوس الجسم", "cat": "تبييض", "ing": "لوشن 80%, عرقسوس 20%", "method": "توحيد لون الجسم."},
        {"name": "كريم الجلوتاثيون", "cat": "تبييض", "ing": "قاعدة 80%, جلوتاثيون 10%, فيتامين سي 10%", "method": "تبييض ونضارة."},
        {"name": "جل المناطق الحساسة", "cat": "تبييض", "ing": "جل صبار 80%, عرقسوس 10%, بابونج 10%", "method": "تفتيح هادئ."},
        {"name": "ماسك الأرز والبودرة", "cat": "تبييض", "ing": "دقيق أرز 50%, ماء ورد 40%, حليب 10%", "method": "تنعيم وتفتيح."},
        {"name": "تونر الليمون للمسام", "cat": "تبييض", "ing": "ماء ورد 90%, ليمون 10%", "method": "تفتيح وقبض مسام."},
        {"name": "كريم بودرة اللؤلؤ", "cat": "تبييض", "ing": "لؤلؤ 10%, كريم مرطب 90%", "method": "إشراقة ملكية."},
        {"name": "سيروم مستخلص التوت", "cat": "تبييض", "ing": "ماء 80%, مستخلص توت 20%", "method": "تفتيح طبيعي."},
        {"name": "لوشن البابايا الإنزيمي", "cat": "تبييض", "ing": "لوشن 80%, بابايا 20%", "method": "تنعيم وتفتيح الجسم."},
        {"name": "كريم الكركم واللبن", "cat": "تبييض", "ing": "كركم 10%, لبن 80%, عسل 10%", "method": "علاج البهتان."},
        {"name": "ماسك القهوة الموحد", "cat": "تبييض", "ing": "قهوة 30%, نشا 30%, ماء ورد 40%", "method": "نضارة فورية."},

        # 📚 مجموعة التقشير (31-45)
        {"name": "مقشر AHA 30% القوي", "cat": "تقشير", "ing": "ماء 60%, جليكوليك 30%, جلسرين 10%", "method": "تقشير كيميائي."},
        {"name": "غسول الساليسيليك 2%", "cat": "تقشير", "ing": "منظف 95%, ساليسيليك 2%, شجرة شاي 3%", "method": "علاج حب الشباب."},
        {"name": "مقشر القهوة والسكر", "cat": "تقشير", "ing": "سكر 40%, قهوة 40%, زيت لوز 20%", "method": "سنفرة فيزيائية."},
        {"name": "الطين المغربي المنقي", "cat": "تقشير", "ing": "طين 70%, ماء ورد 30%", "method": "تنظيف مسام عميق."},
        {"name": "مقشر البابايا والأناناس", "cat": "تقشير", "ing": "بابايا 50%, أناناس 50%", "method": "تقشير إنزيمي بارد."},
        {"name": "تونر الجليكوليك 7%", "cat": "تقشير", "ing": "ماء 90%, جليكوليك 7%, ورد 3%", "method": "تجديد السطح."},
        {"name": "ملح الحليب والزيوت", "cat": "تقشير", "ing": "ملح 70%, حليب 20%, زيت لوز 10%", "method": "تفتيح الركب."},
        {"name": "ماسك الفحم والجيلاتين", "cat": "تقشير", "ing": "فحم 10%, جيلاتين 40%, ماء 50%", "method": "إزالة الرؤوس السوداء."},
        {"name": "مقشر الشوفان الناعم", "cat": "تقشير", "ing": "شوفان 70%, حليب 30%", "method": "لبشرة حساسة."},
        {"name": "سيروم اللاكتيك 10%", "cat": "تقشير", "ing": "ماء 85%, لاكتيك 10%, هيالورونيك 5%", "method": "تقشير وترطيب."},
        {"name": "سكراب اللافندر والملح", "cat": "تقشير", "ing": "ملح بحري 80%, لافندر 20%", "method": "تقشير واسترخاء."},
        {"name": "الطين البركاني والخل", "cat": "تقشير", "ing": "طين 80%, خل تفاح 20%", "method": "سحب السموم."},
        {"name": "مقشر قشور الجوز", "cat": "تقشير", "ing": "جوز مطحون 20%, كريم 80%", "method": "للمناطق الخشنة."},
        {"name": "لوشن جلد الدجاجة", "cat": "تقشير", "ing": "لوشن 90%, ساليسيليك 5%, لاكتيك 5%", "method": "علاج المسام البارزة."},
        {"name": "مقشر الصودا والمنظف", "cat": "تقشير", "ing": "صودا 30%, غسول وجه 70%", "method": "تنظيف الأنف."},

        # 📚 مجموعة الجسم والترطيب (46-60)
        {"name": "لوشن اليوريا 10%", "cat": "الجسم", "ing": "قاعدة 85%, يوريا 10%, زيت زيتون 5%", "method": "علاج الخشونة."},
        {"name": "زبدة الشيا والكاكاو", "cat": "الجسم", "ing": "شيا 60%, كاكاو 20%, جوز هند 20%", "method": "ترطيب عميق."},
        {"name": "زيت التان والبرونز", "cat": "الجسم", "ing": "زيت جزر 50%, جوز هند 40%, لون 10%", "method": "لون برونزي."},
        {"name": "جل النعناع والبانثينول", "cat": "الجسم", "ing": "جل صبار 90%, نعناع 5%, بانثينول 5%", "method": "تبريد الحروق."},
        {"name": "كريم الكولاجين والشد", "cat": "الجسم", "ing": "كولاجين 10%, بانثينول 10%, قاعدة 80%", "method": "شد الجلد."},
        {"name": "لوشن المسك والزيوت", "cat": "الجسم", "ing": "لوشن 90%, زيت مسك 10%", "method": "تعطير الجسم."},
        {"name": "كريم تفتيح المفاصل", "cat": "الجسم", "ing": "يوريا 20%, ساليسيليك 5%, قاعدة 75%", "method": "للمفاصل السوداء."},
        {"name": "زيت لمعان الجسم Glow", "cat": "الجسم", "ing": "زيت جاف 95%, مايكا 5%", "method": "لمعان ذهبي."},
        {"name": "زبدة الكاكاو للتمدد", "cat": "الجسم", "ing": "كاكاو 80%, فيتامين E 20%", "method": "علاج التمدد."},
        {"name": "لوشن الحليب والعسل", "cat": "الجسم", "ing": "حليب 10%, عسل 10%, قاعدة 80%", "method": "ترطيب يومي."},
        {"name": "بخاخ اللافندر للنوم", "cat": "الجسم", "ing": "ماء 80%, زيت لافندر 20%", "method": "تعطير مريح."},
        {"name": "سيروم كافيين للسيلوليت", "cat": "الجسم", "ing": "كافيين 10%, قرفة 5%, قاعدة 85%", "method": "شد السيلوليت."},
        {"name": "لوشن فيتامين E المركز", "cat": "الجسم", "ing": "لوشن 95%, زيت فيتامين E 5%", "method": "ترميم الجلد."},
        {"name": "جل الحلبة لشد الجسم", "cat": "الجسم", "ing": "جل صبار 80%, زيت حلبة 20%", "method": "شد موضعي."},
        {"name": "صابون النيلة والودع", "cat": "الجسم", "ing": "قاعدة صابون 90%, نيلة 10%", "method": "تبييض وتنظيف."},

        # 📚 مجموعة علاجيات (61-75)
        {"name": "مرهم الحروق والندبات", "cat": "علاجيات", "ing": "سمسم 80%, شمع نحل 20%", "method": "ترميم."},
        {"name": "كريم الإكزيما", "cat": "علاجيات", "ing": "شيا 50%, بابونج 20%, زنك 30%", "method": "تهدئة الحكة."},
        {"name": "جل الفطريات", "cat": "علاجيات", "ing": "شجرة شاي 50%, زيت زيتون 50%", "method": "مضاد فطريات."},
        {"name": "كريم الزنك للأطفال", "cat": "علاجيات", "ing": "زنك 40%, فازلين 60%", "method": "التهاب الحفاظ."},
        {"name": "محلول المرة الطبيعي", "cat": "علاجيات", "ing": "ماء 90%, مرة 10%", "method": "تعقيم."},
        {"name": "بخاخ المحلول الملحي", "cat": "علاجيات", "ing": "ماء 95%, ملح 5%", "method": "تنظيف."},
        {"name": "مرهم الكبريت", "cat": "علاجيات", "ing": "كبريت 10%, فازلين 90%", "method": "تجفيف الحبوب."},
        {"name": "جل الصبار والمنثول", "cat": "علاجيات", "ing": "صبار 90%, منثول 10%", "method": "لدغات."},
        {"name": "كريم كافور للمساج", "cat": "علاجيات", "ing": "منثول 10%, كافور 10%, قاعدة 80%", "method": "آلام."},
        {"name": "علاج فطريات الأظافر", "cat": "علاجيات", "ing": "خل تفاح 50%, زيت شاي 50%", "method": "نقع."},
        {"name": "بودرة القدم المعقمة", "cat": "علاجيات", "ing": "تلك 70%, حمض بوريك 20%, نعناع 10%", "method": "روائح."},
        {"name": "مرهم اللانولين للتشقق", "cat": "علاجيات", "ing": "لانولين 50%, فازلين 50%", "method": "ترميم الشفاه."},
        {"name": "بخاخ الجيوب الأنفية", "cat": "علاجيات", "ing": "ماء 99%, ملح 1%", "method": "غسول."},
        {"name": "جل القرنفل للثة", "cat": "علاجيات", "ing": "قرنفل 10%, زيت زيتون 90%", "method": "تسكين."},
        {"name": "ماسك تهدئة الوردية", "cat": "علاجيات", "ing": "خيار 50%, طين أبيض 50%", "method": "تبريد."},

        # 📚 مجموعة العطور (76-90)
        {"name": "مخمرية العود والمسك", "cat": "عطور", "ing": "فازلين 80%, عود 10%, صندل 10%", "method": "تعطير."},
        {"name": "عطر الشعر السيليكوني", "cat": "عطور", "ing": "سيليكون 90%, زيت عطري 10%", "method": "لمعان ورائحة."},
        {"name": "المسك الجامد الفاخر", "cat": "عطور", "ing": "شمع 30%, لوز 50%, مسك 20%", "method": "عطر صلب."},
        {"name": "بدي ميست الزهور", "cat": "عطور", "ing": "كحول 70%, ماء 20%, عطر 10%", "method": "بخاخ عطري."},
        {"name": "عطر الزيوت النقي", "cat": "عطور", "ing": "جوجوبا 90%, مسك مركز 10%", "method": "ثبات."},
        {"name": "فازلين اللافندر", "cat": "عطور", "ing": "فازلين 80%, لافندر 20%", "method": "مساج مريح."},
        {"name": "بخور المعمول الملكي", "cat": "عطور", "ing": "دقة عود 50%, زيوت 50%", "method": "تبخير."},
        {"name": "مكعبات المسك", "cat": "عطور", "ing": "برافين 50%, مسك 50%", "method": "تعطير الخزانات."},
        {"name": "سبراي ماء الورد", "cat": "عطور", "ing": "ماء ورد 95%, زيت ورد 5%", "method": "انتعاش."},
        {"name": "عطر الأطفال المائي", "cat": "عطور", "ing": "ماء 95%, زيت مائي 5%", "method": "آمن للأطفال."},
        {"name": "المسك المتسلق المخملي", "cat": "عطور", "ing": "فازلين 80%, ورد طائفي 20%", "method": "مناطق حساسة."},
        {"name": "بودرة الجسم بالياسمين", "cat": "عطور", "ing": "نشا 70%, ياسمين 30%", "method": "تعطير جاف."},
        {"name": "زيت المساج الاسترخائي", "cat": "عطور", "ing": "لوز حلو 90%, لافندر 10%", "method": "مساج."},
        {"name": "مخمرية بودرة النظافة", "cat": "عطور", "ing": "فازلين 80%, عطر بودرة 20%", "method": "رائحة نظافة."},
        {"name": "زيت الفواحة المركز", "cat": "عطور", "ing": "كحول 80%, زيت عطري 20%", "method": "تعطير الجو."},

        # 📚 مجموعة القدم (91-100)
        {"name": "صابون النيلة والكركم", "cat": "صابون", "ing": "صابون 90%, نيلة 5%, كركم 5%", "method": "تبييض الجسم."},
        {"name": "غسول اليد المعقم", "cat": "صابون", "ing": "صابون سائل 95%, شجرة شاي 5%", "method": "تعقيم يدين."},
        {"name": "صابون الفحم والليمون", "cat": "صابون", "ing": "صابون 95%, فحم 5%", "method": "للبشرة الدهنية."},
        {"name": "شاور جل التوت والكرز", "cat": "صابون", "ing": "قاعدة صابون 90%, توت 10%", "method": "استحمام منعش."},
        {"name": "مقشر اليوريا 40%", "cat": "القدم", "ing": "يوريا 40%, فازلين 40%, ساليسيليك 20%", "method": "تشقق قدم شديد."},
        {"name": "أملاح نقع القدم", "cat": "القدم", "ing": "ماء 70%, ملح إبسوم 20%, خل 10%", "method": "علاج الفطريات والروائح."},
        {"name": "كريم توريد كعب القدم", "cat": "القدم", "ing": "فازلين 95%, دم غزال 5%", "method": "لون وردي طبيعي."},
        {"name": "سبراي إزالة رائحة القدم", "cat": "القدم", "ing": "كحول 80%, منثول 20%", "method": "تعقيم الحذاء والقدم."},
        {"name": "سكراب ملح القدم", "cat": "القدم", "ing": "ملح 60%, زيت لوز 30%, ليمون 10%", "method": "تقشير خشن."},
        {"name": "سيروم الخروع للأظافر", "cat": "القدم", "ing": "خروع 90%, فيتامين E 10%", "method": "تقوية الأظافر."},
    ]

# 4. نظام الدخول
if not st.session_state.auth:
    st.markdown("<h1>🔬 SHOMA LAB PRO</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل الرمز السري للمختبر (247):", type="password")
    if st.button("دخول آمن"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
        else: st.error("الرمز غير صحيح.")
    st.stop()

# 5. القائمة الجانبية (الحاسبة وإضافة وصفات)
with st.sidebar:
    st.markdown("### ⚖️ حاسبة الأوزان")
    total_w = st.number_input("الوزن المطلوب (غرام):", min_value=1, value=1000)
    
    st.divider()
    st.markdown("### ➕ إضافة وصفة جديدة")
    with st.form("add_form", clear_on_submit=True):
        n_name = st.text_input("اسم المنتج:")
        n_cat = st.selectbox("القسم:", ["الوجه", "الجسم", "الشعر", "تبييض", "تقشير", "علاجيات", "عطور", "صابون", "القدم"])
        n_ing = st.text_area("المكونات (مثال: ماء 90%, زيت 10%):")
        n_meth = st.text_area("طريقة العمل:")
        if st.form_submit_button("إضافة للمستودع"):
            if n_name and n_ing:
                st.session_state.my_recipes.append({"name": n_name, "cat": n_cat, "ing": n_ing, "method": n_meth})
                st.success(f"تمت إضافة {n_name}")
                st.rerun()

    st.divider()
    if st.button("🗑️ تصفير الذاكرة"):
        st.session_state.chat_recipes = []
        st.session_state.chat_general = []
        st.rerun()

# 6. الأقسام الرئيسية
tabs = st.tabs(["📚 المستودع الشامل", "🧪 خبير التركيبات AI", "🤖 الخبير العام AI"])

# --- التبويب الأول: إدارة المستودع (تعديل وحذف) ---
with tabs[0]:
    search_q = st.text_input("🔍 ابحث في الـ 100+ وصفة (مثلاً: مميزة، شعر، تبييض):")
    for i, r in enumerate(st.session_state.my_recipes):
        if search_q.lower() in r['name'].lower() or search_q.lower() in r['cat'].lower():
            with st.expander(f"🛠️ إدارة: {r['name']} ({r['cat']})"):
                col_edit, col_calc = st.columns([1, 1])
                
                with col_edit:
                    e_name = st.text_input("الاسم", value=r['name'], key=f"n_{i}")
                    e_ing = st.text_area("المكونات", value=r['ing'], key=f"i_{i}")
                    e_meth = st.text_area("الطريقة", value=r['method'], key=f"m_{i}")
                    
                    b1, b2 = st.columns(2)
                    if b1.button("✅ حفظ التغيير", key=f"s_{i}"):
                        st.session_state.my_recipes[i] = {"name": e_name, "cat": r['cat'], "ing": e_ing, "method": e_meth}
                        st.success("تم الحفظ!")
                        st.rerun()
                    if b2.button("🗑️ حذف نهائي", key=f"d_{i}"):
                        st.session_state.my_recipes.pop(i)
                        st.rerun()
                
                with col_calc:
                    st.markdown("**حساب الغرامات:**")
                    parts = e_ing.split(',')
                    calc_rows = []
                    for p in parts:
                        match = re.search(r'(\d+)%', p)
                        if match:
                            perc = int(match.group(1))
                            w = (perc / 100) * total_w
                            calc_rows.append({"المادة": p.split(str(perc))[0].strip(), "الوزن (g)": f"{w:,.2f}"})
                    if calc_rows: st.table(pd.DataFrame(calc_rows))

# --- التبويب الثاني والثالث للذكاء الاصطناعي ---
with tabs[1]:
    for msg in st.session_state.chat_recipes:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    r_imgs = st.file_uploader("📸 صور المكونات:", accept_multiple_files=True, key="u_rcp")
    r_in = st.chat_input("اسأل خبير التركيبات عن مستودعك...")
    
    if r_in:
        st.session_state.chat_recipes.append({"role": "user", "content": r_in})
        with st.chat_message("user"): st.markdown(r_in)
        with st.chat_message("assistant"):
            db_ctx = json.dumps(st.session_state.my_recipes, ensure_ascii=False)
            sys_msg = {"role": "system", "content": f"أنت خبير كيمياء تجميلية. مستودعك الحالي: {db_ctx}. تذكر السياق بدقة."}
            msgs = [sys_msg] + st.session_state.chat_recipes
            if r_imgs:
                content = [{"type": "text", "text": r_in}]
                for img in r_imgs:
                    enc = base64.b64encode(img.read()).decode('utf-8')
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{enc}"}})
                msgs[-1]["content"] = content
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_recipes.append({"role": "assistant", "content": ans})

with tabs[2]:
    for msg in st.session_state.chat_general:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    g_imgs = st.file_uploader("📸 صور تحاليل/أكواد:", accept_multiple_files=True, key="u_gen")
    g_in = st.chat_input("اسأل في أي موضوع...")
    
    if g_in:
        st.session_state.chat_general.append({"role": "user", "content": g_in})
        with st.chat_message("user"): st.markdown(g_in)
        with st.chat_message("assistant"):
            sys_g = {"role": "system", "content": "أنت خبير شامل مطور من قبل شيماء علي عبد الحسين. تذكر السياق بدقة وموضوعية."}
            msgs = [sys_g] + st.session_state.chat_general
            if g_imgs:
                content = [{"type": "text", "text": g_in}]
                for img in g_imgs:
                    enc = base64.b64encode(img.read()).decode('utf-8')
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{enc}"}})
                msgs[-1]["content"] = content
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.chat_general.append({"role": "assistant", "content": ans})

st.markdown("---")
st.caption("SHOMA LAB PRO © 2026 | تطوير: شيماء علي عبد الحسين")
