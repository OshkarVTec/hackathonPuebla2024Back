from openai import OpenAI

client = OpenAI()


def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Vas a recibir una transcripción completa de una clase. Devuelve un resumen bien estructurado de la clase",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


user_input = input("How may I help you? ")
Ask_chatgpt = chat_with_gpt(user_input)
print(f"Assistant: {Ask_chatgpt}")
