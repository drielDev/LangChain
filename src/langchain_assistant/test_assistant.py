from .assistant import generate_response


questions = [
    "Estou com dores menstruais intensas.",
    "Isso pode durar quantos dias?",
    "Quando devo procurar um médico?"
]


for question in questions:

    response = generate_response(question)

    print("\nPergunta:")
    print(question)

    print("\nResposta:")
    print(response)

    print("\n" + "=" * 50)