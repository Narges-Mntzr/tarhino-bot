import dns.resolver
from google import genai
from config import GEMINI_API_TOKEN

# Set shecan
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["178.22.122.100", "185.51.200.2"]

client = genai.Client(api_key=GEMINI_API_TOKEN)


def get_title_with_ai(message_text: str):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"یک عنوان خلاقانه فارسی بین ۱ تا ۸ کلمه برای این متن بده. فقط عنوان را در پاسخ بنویس. یدون هیچ کاراکتر اضافه: {message_text}",
    )
    return response.text
