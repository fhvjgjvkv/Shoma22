import streamlit as st
import pandas as pd
import re
from groq import Groq
import base64
import json

# 1. إعدادات الهوية والواجهة
st.set_page_config(page_title="SHOMA LAB PRO", layout="wide", page_icon="🔬")

# تصميم الواجهة CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button { 
        background: linear-gradient(45deg, #00ffcc, #0055ff); 
        color: white; border-radius: 10px; border: none; font-weight: bold;
    }
    .stExpander { background-color: #1e2130; border: 1px solid #00ffcc; border-radius: 10px; }
    h1, h2, h3 { color: #00ffcc !important; text-align: center; }
    .stChatMessage { border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# 2. الاتصال بمحرك Groq (استخدام نموذج llama-3.3-70b-versatile المستقر)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى إضافة GROQ_API_KEY في إعدادات Secrets لتفعيل الذكاء الاصطناعي.")
    st.stop()

# 3. إدارة الجلسة والأمان
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.auth:
    st.markdown("<h1>🔬 SHOMA LAB PRO - تسجيل الدخول</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل الرمز السري الخاص بالمختبر:", type="password")
    if st.button("تأكيد الدخول"):
        if pwd == "247":
            st.session_state.auth = True
            st.rerun()
        else: st.error("الرمز السري غير صحيح.")
    st.stop()

# 4. قاعدة بيانات الـ 100 وصفة الشاملة
all_recipes = [
    # قسم الشعر (1-15)
    {"name": "سيروم الروزماري والبروكابيل", "cat": "الشعر", "ing": "ماء 85%, بروكابيل 3%, جلسرين 10%, حافظة 2%", "method": "خلط بارد للإنبات وتنشيط البصيلات."},
    {"name": "شامبو البيوتين", "cat": "الشعر", "ing": "قاعدة شامبو 90%, بيوتين 5%, زيت خروع 5%", "method": "إضافة تدريجية للتقوية ومنع التساقط."},
    {"name": "ماسك السدر الملكي", "cat": "الشعر", "ing": "سدر مطحون 50%, منقوع إكليل جبل 40%, زيت جوجوبا 10%", "method": "علاج طبيعي لتكثيف الشعر."},
    {"name": "سيروم الكافيين 5%", "cat": "الشعر", "ing": "ماء 90%, كافيين 5%, بانثينول 5%", "method": "تنشيط فروة الرأس."},
    {"name": "بلسم الكيراتين", "cat": "الشعر", "ing": "قاعدة بلسم 85%, كيراتين سائل 10%, زيت أرغان 5%", "method": "ترميم وتنعيم الشعر التالف."},
    
    # قسم تبييض البشرة (16-30)
    {"name": "كريم ألفا أربوتين 2%", "cat": "التبييض", "ing": "قاعدة كريم 80%, أربوتين 2%, عرقسوس 10%, نياسيناميد 8%", "method": "تفتيح البقع الداكنة وتوحيد اللون."},
    {"name": "سيروم فيتامين سي 20%", "cat": "التبييض", "ing": "ماء 70%, فيتامين سي 20%, فيروليك 1%, جلسرين 9%", "method": "نضارة وإشراق وحماية من الأكسدة."},
    {"name": "ماسك النيلة المغربية", "cat": "التبييض", "ing": "نيلة 20%, زبادي 70%, نشا 10%", "method": "تفتيح فوري وتبييض للجسم والبشرة."},
    {"name": "كريم الكوجيك أسيد", "cat": "التبييض", "ing": "قاعدة كريم 90%, حمض كوجيك 5%, مستخلص ليمون 5%", "method": "علاج التصبغات الناتجة عن الشمس."},
    
    # قسم التقشير (31-45)
    {"name": "مقشر AHA 30%", "cat": "التقشير", "ing": "ماء 60%, جليكوليك 30%, جلسرين 10%", "method": "تقشير كيميائي سطحي لتجديد البشرة."},
    {"name": "غسول الساليسيليك 2%", "cat": "التقشير", "ing": "قاعدة منظف 95%, ساليسيليك 2%, زيت شجرة شاي 3%", "method": "تنظيف المسام وعلاج حب الشباب."},
    
    # قسم الجسم والترطيب (46-60)
    {"name": "لوشن اليوريا 10%", "cat": "الجسم", "ing": "قاعدة 85%, يوريا 10%, زيت 5%", "method": "علاج جفاف الجلد الشديد وخشونة الركب."},
    {"name": "زبدة الشيا المخفوقة", "cat": "الجسم", "ing": "شيا 60%, كاكاو 20%, جوز هند 20%", "method": "ترطيب عميق جداً وحماية من التشققات."},
    
    # قسم العطور والمخمرية (76-90)
    {"name": "مخمرية العود الملكي", "cat": "العطور", "ing": "فازلين 80%, زيت عود 10%, صندل 10%", "method": "ثبات رائحة عالي جداً للجسم والشعر."},
    
    # قسم الصابون والعناية بالقدم (91-100)
    {"name": "مقشر قدم يوريا 40%", "cat": "القدم", "ing": "يوريا 40%, فازلين 40%, ساليسيليك 20%", "method": "إزالة الجلد الميت القاسي وتشقق القدمين."},
    {"name": "صابون النيلة المغربية", "cat": "صابون", "ing": "قاعدة صابون 90%, نيلة 10%", "method": "تنظيف وتفتيح الجسم بالاستحمام."},
]

# (ملاحظة: يمكنك إضافة باقي الـ 100 وصفة في القائمة أعلاه بنفس التنسيق)

# 5. الواجهة الجانبية (الحاسبة)
with st.sidebar:
    st.markdown("<h3>⚖️ حاسبة الأوزان الذكية</h3>", unsafe_allow_html=True)
    total_w = st.number_input("أدخل الوزن الكلي (غرام):", min_value=1, value=1000)
    st.divider()
    if st.button("🗑️ مسح ذاكرة الخبير"):
        st.session_state.messages = []
        st.rerun()

# 6. التبويبات الرئيسية
tabs = st.tabs(["📚 مستودع الوصفات (100)", "💬 خبير المختبر المترابط (AI)"])

# تبويب الوصفات
with tabs[0]:
    search = st.text_input("🔍 ابحث عن وصفة (بالاسم، المكون، أو القسم):")
    filtered = [r for r in all_recipes if search.lower() in r['name'].lower() or search.lower() in r['ing'].lower() or search.lower() in r['cat'].lower()]
    
    st.write(f"تم العثور على {len(filtered)} نتيجة.")
    
    for r in filtered:
        with st.expander(f"✨ {r['name']} - [{r['cat']}]"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**المكونات الأساسية:**\n{r['ing']}")
                st.info(f"**طريقة العمل:**\n{r['method']}")
            with col2:
                st.markdown("**حسابات المختبر لهذا الوزن:**")
                parts = r['ing'].split(',')
                calc_data = []
                for p in parts:
                    match = re.search(r'(\d+)%', p)
                    if match:
                        perc = int(match.group(1))
                        weight = (perc / 100) * total_w
                        calc_data.append({"المادة": p.split(str(perc))[0].strip(), "الوزن المطلوب (g)": f"{weight:,.2f}"})
                if calc_data: st.table(pd.DataFrame(calc_data))

# تبويب الذكاء الاصطناعي المرتبط
with tabs[1]:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    up_imgs = st.file_uploader("📸 ارفع صورة (تحليل دم، منتج، أو كود):", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    u_input = st.chat_input("اسألني عن الوصفات، البرمجة، أو التحاليل...")

    if u_input:
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"):
            st.markdown(u_input)

        with st.chat_message("assistant"):
            try:
                # تزويد الذكاء الاصطناعي بقاعدة البيانات ليفهمها
                recipes_json = json.dumps(all_recipes, ensure_ascii=False)
                
                system_prompt = f"""
                أنت خبير مختبر وبرمجة ذكي جداً وموضوعي. 
                أنت تعمل ضمن نظام SHOMA LAB PRO المطور من قبل "شيماء علي عبد الحسين".
                لديك صلاحية الوصول الكاملة لقاعدة بيانات الوصفات هذه: {recipes_json}
                
                مهامك:
                1. إذا سألك المستخدم عن أي وصفة من القائمة، اشرحها له بدقة بناءً على البيانات المتوفرة.
                2. إذا طلب تعديل وصفة أو سأل عن بدائل لمكوناتها، أجب بشكل علمي وموضوعي.
                3. يمكنك الإجابة في أي موضوع آخر (برمجة، طب، سيارات) بوضوح ودقة.
                4. أجب بدون مجاملات وبلا تلطيف، كن مباشراً وعملياً.
                """

                payload = [{"type": "text", "text": system_prompt}, {"type": "text", "text": u_input}]
                
                if up_imgs:
                    for img in up_imgs:
                        encoded = base64.b64encode(img.read()).decode('utf-8')
                        payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}})
                
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                history.append({"role": "user", "content": payload})
                
                # استخدام النموذج الإنتاجي المستقر
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history
                )
                
                full_res = response.choices[0].message.content
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
            except Exception as e:
                st.error(f"عذراً، حدث خطأ في الاتصال: {e}")

# التذييل (Footer) بالاسم الجديد
st.markdown("---")
st.caption("SHOMA LAB PRO © 2026 | النسخة المتكاملة | من تطوير شيماء علي عبد الحسين")
