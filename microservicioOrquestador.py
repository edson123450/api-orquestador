from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL de los otros microservicios
MICROSERVICIO_1 = "http://api-microservicio1_c:8001"
MICROSERVICIO_2 = "http://api-microservicio2_c:8002"
MICROSERVICIO_3 = "http://api-microservicio3_c:8003"

# Función auxiliar para manejar errores en las peticiones HTTP
def handle_http_errors(response):
    if response.status_code != 200 and response.status_code != 201:
        return jsonify({"error": f"Error: {response.json().get('error')}"}), response.status_code
    return None

# API 1: Recibir datos y crear una nueva review
@app.route('/orchestrator/new-review', methods=['POST'])
def new_review():
    data = request.json
    title = data['title']
    author_name = data['author_name']
    user_name = data['user_name']
    user_email = data['user_email']
    rating = data['rating']
    comment = data['comment']

    # Paso 1: Obtener o crear el user_id del usuario en el microservicio 2
    user_response = requests.post(f"{MICROSERVICIO_2}/users/find_or_create", json={
        "name": user_name,
        "email": user_email
    })
    error_response = handle_http_errors(user_response)
    if error_response:
        return error_response

    user_id = user_response.json()['user_id']

    # Paso 2: Obtener el book_id del libro en el microservicio 1
    book_response = requests.get(f"{MICROSERVICIO_1}/books/get_book_id", params={
        "title": title,
        "author_name": author_name
    })
    error_response = handle_http_errors(book_response)
    if error_response:
        return error_response

    book_id = book_response.json()['book_id']

    # Paso 3: Obtener el author_id en el microservicio 1
    author_response = requests.get(f"{MICROSERVICIO_1}/authors/get_author_id/", params={
        "author_name": author_name
    })
    error_response = handle_http_errors(author_response)
    if error_response:
        return error_response

    author_id = author_response.json()['author_id']

    # Paso 4: Crear la nueva review en el microservicio 3
    review_response = requests.post(f"{MICROSERVICIO_3}/reviews/new", json={
        "book_id": book_id,
        "author_id": author_id,
        "user_id": user_id,
        "rating": rating,
        "comment": comment
    })
    error_response = handle_http_errors(review_response)
    if error_response:
        return error_response

    return jsonify({"message": "Review created successfully"}), 201


# API 2: Verificar si un usuario ha hecho una review
@app.route('/orchestrator/check-review', methods=['GET'])
def check_review():
    title = request.args.get('title')
    author_name = request.args.get('author_name')
    user_name = request.args.get('user_name')
    user_email = request.args.get('user_email')

    # Paso 1: Obtener el book_id del libro en el microservicio 1
    book_response = requests.get(f"{MICROSERVICIO_1}/books/get_book_id", params={
        "title": title,
        "author_name": author_name
    })
    error_response = handle_http_errors(book_response)
    if error_response:
        return error_response

    book_id = book_response.json()['book_id']

    # Paso 2: Obtener el user_id en el microservicio 2
    user_response = requests.get(f"{MICROSERVICIO_2}/users/get_user_id", params={
        "name": user_name,
        "email": user_email
    })
    error_response = handle_http_errors(user_response)
    if error_response:
        return error_response

    user_id = user_response.json()['user_id']

    # Paso 3: Verificar la existencia de la review en el microservicio 3
    review_response = requests.get(f"{MICROSERVICIO_3}/reviews/check-review", params={
        "bookId": book_id,
        "authorId": book_response.json()['book_id'],
        "userId": user_id
    })
    error_response = handle_http_errors(review_response)
    if error_response:
        return error_response

    review_data = review_response.json()

    # Paso 4: Verificar el valor de "message" en la respuesta
    if review_data['message'] == 'si':
        return jsonify({
            "title": title,
            "author_name": author_name,
            "user_name": user_name,
            "user_email": user_email,
            "rating": review_data['rating'],
            "comment": review_data['comment']
        }), 200
    else:
        return jsonify({"error": "Este usuario no ha realizado un review de ese libro"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004, debug=True)