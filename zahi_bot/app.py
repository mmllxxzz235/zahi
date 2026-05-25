import os
from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'ZahiBotVerify2026')

@app.route('/', methods=['GET'])
def home():
    return "Zahi Platform Bot is Running!", 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode and token and mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            if 'messaging' in entry:
                for messaging_event in entry.get('messaging', []):
                    sender_id = messaging_event['sender']['id']
                    if messaging_event.get('message', {}).get('quick_reply'):
                        handle_button_click(sender_id, messaging_event['message']['quick_reply'].get('payload'))
                    elif messaging_event.get('message', {}).get('text'):
                        send_main_menu(sender_id)
            if 'changes' in entry:
                for change in entry.get('changes', []):
                    if change.get('field') == 'feed':
                        value = change.get('value', {})
                        if value.get('item') == 'comment' and value.get('verb') == 'add':
                            send_public_comment_reply(value.get('comment_id'))
        return "EVENT_RECEIVED", 200
    return "Not Found", 404

def send_public_comment_reply(comment_id):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/comments"
    requests.post(url, json={'message': "أهلاً بك في منصة زاهي! ✨ تفضل بمراسلتنا على الخاص لتظهر لك قائمة الأسعار التفاعلية فوراً! 📥🚀", 'access_token': PAGE_ACCESS_TOKEN})

def send_main_menu(sender_id):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": sender_id},
        "message": {
            "text": "مرحباً بك في منصة زاهي! 🎮 اختر اللعبة لاستعراض الأسعار:",
            "quick_replies": [
                {"content_type": "text", "title": "🎮 ببجي عالمية", "payload": "PUBG_GLOBAL"},
                {"content_type": "text", "title": "🇱🇾 ببجي كورية", "payload": "PUBG_KR"},
                {"content_type": "text", "title": "🎲 يلا لودو", "payload": "YALLA_LUDO"},
                {"content_type": "text", "title": "💎 فري فاير", "payload": "FREE_FIRE"}
            ]
        }
    }
    requests.post(url, json=payload)

def handle_button_click(sender_id, payload):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    
    if payload == "PUBG_GLOBAL":
        text = "🎮 ببجي عالمية:\n- 60 UC ◀️ 10 د.ل\n- 325 UC ◀️ 50 د.ل\n- 660 UC ◀️ 100 د.ل"
    elif payload == "PUBG_KR":
        text = "🇱🇾 ببجي كورية:\n- 60 UC ◀️ 10 د.ل\n- 180+15 UC ◀️ 30 د.ل\n- 390 UC ◀️ 60 د.ل"
    elif payload == "FREE_FIRE":
        text = "💎 فري فاير:\n- 100 ماسة ◀️ 10 د.ل\n- 210 ماسة ◀️ 20 د.ل\n- 530 ماسة ◀️ 50 د.ل"
    elif payload == "YALLA_LUDO":
        text = ("🎲 يلا لودو:\n\n💎 المجوهرات:\n- 830 مجوهرات ◀️ 20 د.ل\n- 2,320 مجوهرات ◀️ 50 د.ل\n\n💰 الكوينز:\n- 68,500 كوينز ◀️ 20 د.ل\n- 223,700 كوينز ◀️ 50 د.ل")
    else:
        text = "عذراً، لم يتم العثور على الباقة."

    requests.post(url, json={"recipient": {"id": sender_id}, "message": {"text": text + "\n\n📥 أرسل الـ ID لإتمام الشحن!"}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))