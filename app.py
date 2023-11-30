from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Product
from dotenv import load_dotenv
import os
import asyncio
import aiohttp


app = Flask(__name__)
CORS(app)


class Config:
    def __init__(self):
        load_dotenv()

        self.host = os.getenv('HOST', '127.0.0.1')
        self.port = int(os.getenv('PORT', 5010))
        self.debug = os.getenv('DEBUG', 'True').lower() == 'true'
        self.environment = os.getenv('ENVIRONMENT', 'development')


config = Config()
app.config['SQLALCHEMY_DATABASE_URI'] = 'jdbc:postgresql://localhost:5432/postgres'


books = [
    {
        "id": "1",
        "name": "Грокаем алгоритмы",
        "authors": ["Бхаргава Адитья"],
        "description": "© Алгоритмы — это всего лишь пошаговые инструкции решения задач.",
        "pages": 288
    },
    {
        "id": "2",
        "name": "Чистый код",
        "authors": ["Мартин Роберт"],
        "description": "Плохой код может работать, но он будет мешать развитию проекта и компании-разработчика, требуя дополнительные ресурсы на поддержку и «укрощение». Каким же должен быть код?",
        "pages": 464
    },
    {
        "id": "3",
        "name": "Чистая архитектура",
        "authors": ["Мартин Роберт"],
        "description": "Роберт Мартин дает прямые и лаконичные ответы на ключевые вопросы архитектуры и дизайна.",
        "pages": 352
    }
]
book_id = 1


@app.route('/api/v1/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({
        "status": "success",
        "data": {
            "services": [
                {
                    "name": "core",
                    "availability": 100
                }
            ]
        }
    })


@app.route('/api/v1/books', methods=['GET'])
def get_books():
    return jsonify({
        "data": {
            "books": books
        },
        "status": "success"
    })


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'category_id': product.category_id
        })
    return jsonify(result)


@app.route('/api/v1/books', methods=['POST'])  # @app.route('/bm/v1/books/<book_id>', methods=['GET'])
def add_book():
    global book_id
    data = request.json

    name = data['name']
    authors = data['authors']
    description = data['description']
    pages = data['pages']

    book = {
        'id': str(book_id),
        'name': name,
        'authors': authors,
        'description': description,
        'pages': pages
    }

    books.append(book)
    book_id = 1

    return jsonify({
        'data': {
            'book': book
        },
        'status': 'success'
    }), 201


@app.route('/api/v1/books/<book_id>', methods=['DELETE'])  # @app.route('/bm/v1/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return jsonify({
                'data': {},
                'status': 'success'
            })

    return jsonify({
        'message': 'Book not found',
        'status': 'error'
    }), 404


@app.route('/api/v1/books/<book_id>', methods=['GET'])  # @app.route('/bm/v1/books/<book_id>', methods=['GET'])
def get_book(book_id):
    for book in books:
        if book['id'] == book_id:
            return jsonify({
                'data': {
                    'book': book
                },
                'status': 'success'
            })

    return jsonify({
        'message': 'Book not found',
        'status': 'error'
    }), 404


@app.route('/api/v1/books/<book_id>', methods=['PATCH']) # @app.route('/bm/v1/books/<book_id>', methods=['PATCH'])
def update_book(book_id):
    data = request.json

    for book in books:
        if book['id'] == book_id:
            if 'name' in data:
                book['name'] = data['name']
            if 'authors' in data:
                book['authors'] = data['authors']
            if 'description' in data:
                book['description'] = data['description']
            if 'pages' in data:
                book['pages'] = data['pages']

            return jsonify({
                'data': {
                    'book': book
                },
                'status': 'success'
            })

    return jsonify({
        'message': 'Book not found',
        'status': 'error'
    }), 404


async def fetch_products(session):
    url = 'https://dummyjson.com/products'

    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data['data']['products'][:10]


async def get_all_products():
    async with aiohttp.ClientSession() as session:
        products = await fetch_products(session)
        return products


@app.route('/im/v1/products', methods=['GET'])
async def get_products():
    products = await get_all_products()

    simplified_products = []
    for product in products:
        simplified_product = {
            'id': product['id'],
            'name': product['name'],
            'description': product['description'],
            'stock': product['stock'],
            'brand': product['brand'],
            'category': product['category'],
            'thumbnail': product['thumbnail']
        }
        simplified_products.append(simplified_product)

    return jsonify({
        'data': {
            'products': simplified_products
        },
        'status': 'success'
    })


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(fetch_products()))
    app.run(host=config.host, port=config.port, debug=config.debug)
#   app.run(host='api.cloud-services.flask', port=5010)
