import tiktoken

enc=tiktoken.encoding_for_model("gpt-4o")

text="Hey, My name is Divyansh Singh"
tokens=enc.encode(text)

print(tokens) #[25216, 11, 3673, 1308, 382, 12302, 121378, 71, 44807] result of the tokenization

decoded=enc.decode([25216, 11, 3673, 1308, 382, 12302, 121378, 71, 44807])
print(decoded)