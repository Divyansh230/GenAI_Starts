import requests

API_URL = "https://api-inference.huggingface.co/models/google/gemma-3-4b-it"
headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_TOKEN"}

# Payload with both image and text
payload = {
    "inputs": {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
            {"type": "text", "text": "What animal is on the candy?"}
        ]
    }
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json())
