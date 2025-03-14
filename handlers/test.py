from google.generativeai import genai

client = genai.Client(api_key="AIzaSyBk2Jyjg3FcQ_eFHUgmmMd4uwG6bMJZm0I")

text = "عروسی به  معنای پیوند دو نفر برای شروع زندگی زناشویی می باشد و اگر قرار باشد آن را خاطره انگیز کرده و خاطره ای را نگه داریم"


response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"یک عنوان خلاقانه فارسی بین ۱ تا ۵ کلمه برای این متن بده. فقط عنوان را در پاسخ بنویس. یدون هیچ کاراکتر اضافه: {text}",
)
print(response.text)
