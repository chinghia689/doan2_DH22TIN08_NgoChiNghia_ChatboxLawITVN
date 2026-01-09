import requests

API_URL = "http://localhost:8000/chat"

def main():

    while True:
        query = input("Bạn: ")
        if query.lower() in ['exit', 'quit']:
            break
        if not query.strip():
            continue

        print("AI đang trả lời...", end="\r")

        response = requests.post(API_URL, json={"question": query})

        data = response.json()
        print(f"AI: {data['answer']}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()