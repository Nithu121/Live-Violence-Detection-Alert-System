import requests

def send_telegram_message(message, chat_id):
    bot_token = '////'
    send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    params = {
        'chat_id': chat_id,
        'text': message
    }

    try:
        print(f"Attempting to send Telegram message to chat ID {chat_id}...")
        response = requests.post(send_message_url, params=params)
        print(f"Response Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send Telegram message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

if __name__ == "__main__":
    send_telegram_message("Test message from minimal script", "1747349588")
