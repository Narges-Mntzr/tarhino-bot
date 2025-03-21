from config import AVAL_API_TOKEN,logging
from langchain_openai import ChatOpenAI

model_name = "gpt-4o-mini"

llm = ChatOpenAI(
    model=model_name, base_url="https://api.avalapis.ir/v1", api_key=AVAL_API_TOKEN
)


def get_title_with_ai(message_text: str):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful persian assistant."},
            {
                "role": "user",
                "content": f"یک عنوان خلاقانه فارسی با تاکید بر موضوع و افراد گفته‌شده بین ۱ تا ۵ کلمه برای این متن بده. فقط عنوان را در پاسخ بنویس. یدون هیچ کاراکتر اضافه: {message_text}",
            },
        ]

        responce = llm.invoke(messages)
        return responce.content
    except Exception as e:
        logging.error(e)
        return None
