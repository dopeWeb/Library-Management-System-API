from flask import Flask,request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Correct column name
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    deleted = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f'<Book {self.name}>'

class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Customer {self.name}>'

class Loan(db.Model):
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    loan_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    return_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Loan CustID={self.cust_id}, BookID={self.book_id}>'

def get_max_loan_days(book_type):
    return {1: 10, 2: 5, 3: 2}.get(book_type, 0)


def seed_data():
    if not Customers.query.first():
        db.session.bulk_save_objects([
            Customers(name='John Doe', city='New York', age=30, email='john.doe@example.com'),
            Customers(name='Jane Smith', city='Los Angeles', age=25, email='jane.smith@example.com'),
            Customers(name='Jade Bmith', city='Los Demons', age=666, email='jade.bmith@example.com')
        ])
        db.session.commit()


    if not Books.query.first():
        db.session.bulk_save_objects([
            Books(name='The Great Gatsby', author='F. Scott Fitzgerald', year_published=1925, type=1),
            Books(name='1984', author='George Orwell', year_published=1949, type=2),
            Books(name='To Kill a Mockingbird', author='Harper Lee', year_published=1960, type=3),
            Books(name='To No Kill a Mockingbird', author='Harper Lee', year_published=2005, type=2),
            Books(name='To Yes Kill a Mockingbird', author='Harper Lee', year_published=1999, type=3)
        ])
        db.session.commit()
        

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    if Customers.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Customer with this email already exists."}), 400
    
    new_customer = Customers(name=data['name'], city=data['city'], age=data['age'], email=data['email'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": f"Customer '{data['name']}' added successfully."}), 201

@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json

    # Normalize field names to lowercase
    normalized_data = {
        'name': data.get('name') or data.get('Name'),
        'author': data.get('author') or data.get('Author'),
        'yearPublished': data.get('yearPublished') or data.get('YearPublished'),
        'type': data.get('type') or data.get('Type')
    }

    # Ensure all required fields are present
    if not normalized_data['name'] or not normalized_data['author'] or not normalized_data['yearPublished'] or normalized_data['type'] is None:
        return jsonify({"message": "Missing required fields."}), 400

    if Books.query.filter_by(name=normalized_data['name']).first():
        return jsonify({"message": "Book with this name already exists."}), 400
    
    if normalized_data['type'] not in [1, 2, 3]:
        return jsonify({"message": "Invalid book type."}), 400

    new_book = Books(name=normalized_data['name'], author=normalized_data['author'], year_published=normalized_data['yearPublished'], type=normalized_data['type'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": f"Book '{normalized_data['name']}' added successfully."}), 201

@app.route('/loan_book', methods=['POST'])
def loan_book():
    data = request.json
    book_id = data.get('bookId')
    cust_id = data.get('custId')

    book = Books.query.get(book_id)
    if not book or book.deleted:
        return jsonify({"message": "Book not found or deleted."}), 404

    customer = Customers.query.get(cust_id)
    if not customer or customer.deleted:
        return jsonify({"message": "Customer not found or deleted."}), 404

    if Loan.query.filter_by(book_id=book_id, return_date=None).first():
        return jsonify({"message": "Book is currently loaned out."}), 400

    if Loan.query.filter_by(cust_id=cust_id, return_date=None).count() >= 3:
        return jsonify({"message": "Customer has already loaned 3 books."}), 400

    max_loan_days = get_max_loan_days(book.type)
    if max_loan_days == 0:
        return jsonify({"message": "Invalid book type."}), 400

    return_date = datetime.now(timezone.utc) + timedelta(days=max_loan_days)
    new_loan = Loan(cust_id=cust_id, book_id=book_id, return_date=None)
    db.session.add(new_loan)
    db.session.commit()
    
    return jsonify({
        "message": f"Book ID {book_id} loaned to Customer ID {cust_id}.",
        "return_date": return_date.isoformat()
    }), 201

@app.route('/return_book', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('bookId')
    cust_id = data.get('custId')

    loan = Loan.query.filter_by(book_id=book_id, cust_id=cust_id, return_date=None).first()
    if not loan:
        return jsonify({"message": "Loan record not found or already returned."}), 404

    loan.return_date = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({
        "message": f"Book ID {book_id} returned by Customer ID {cust_id}.",
        "return_date": loan.return_date.isoformat()
    }), 200

@app.route('/display_all_books', methods=['GET'])
def display_all_books():
    books = Books.query.filter_by(deleted=False).all()
    return jsonify([{
        "id": book.id,
        "name": book.name,
        "author": book.author,
        "yearPublished": book.year_published,
        "type": book.type
    } for book in books]), 200

@app.route('/display_all_customers', methods=['GET'])
def display_all_customers():
    customers = Customers.query.filter_by(deleted=False).all()
    return jsonify([{
        "id": customer.id,
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "email": customer.email
    } for customer in customers]), 200

@app.route('/display_all_loans', methods=['GET'])
def display_all_loans():
    loans = Loan.query.all()
    return jsonify([{
        "custId": loan.cust_id,
        "bookId": loan.book_id,
        "loanDate": loan.loan_date.isoformat(),
        "returnDate": loan.return_date.isoformat() if loan.return_date else "Not returned yet"
    } for loan in loans]), 200

@app.route('/late_loans', methods=['GET'])
def late_loans():
    now_utc = datetime.now(timezone.utc)
    late_loans_query = db.session.query(Loan, Books, Customers).join(Books).join(Customers).filter(
        Loan.return_date == None,
        Loan.loan_date + timedelta(days=get_max_loan_days(Books.type)) < now_utc
    ).all()

    result = [{
        "book_id": book.id,
        "book_name": book.name,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "loan_date": loan.loan_date.isoformat(),
        "due_date": (loan.loan_date + timedelta(days=get_max_loan_days(book.type))).isoformat()
    } for loan, book, customer in late_loans_query]

    return jsonify(result), 200



@app.route('/find_book_by_name', methods=['POST'])
def find_book_by_name():
    data = request.json
    book_name = data.get('name')  # Ensure this matches the JSON key

    if not book_name:
        return jsonify({"message": "Book name is required."}), 400

    try:
        # Perform a case-insensitive search
        books = Books.query.filter(
            db.func.lower(Books.name) == db.func.lower(book_name),  # Use the correct column name
            Books.deleted == False
        ).all()

        if not books:
            return jsonify({"message": "No books found with this name."}), 404

        result = [{
            "name": book.name,
            "author": book.author,
            "yearPublished": book.year_published,
            "type": book.type
        } for book in books]

        return jsonify(result), 200

    except Exception as e:
        
        return jsonify({"message": "An error occurred while processing your request."}), 500





@app.route('/find_customer_by_name', methods=['POST'])
def find_customer_by_name():
    data = request.json
    customer_name = data.get('name')

    if not customer_name:
        return jsonify({"message": "Customer name is required."}), 400

    # Perform a case-insensitive search
    customers = Customers.query.filter(
        db.func.lower(Customers.name) == db.func.lower(customer_name),
        Customers.deleted == False
    ).all()

    if not customers:
        return jsonify({"message": "No customers found with this name."}), 404

    result = [{
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "email": customer.email
    } for customer in customers]

    return jsonify(result), 200




@app.route('/remove_book', methods=['DELETE'])
def remove_book():
    data = request.json
    book_id = data.get('bookId')

    if not book_id:
        return jsonify({"message": "Book ID is required."}), 400

    book = Books.query.get(book_id)
    if not book or book.deleted:
        return jsonify({"message": "Book not found or already deleted."}), 404

    if Loan.query.filter_by(book_id=book_id, return_date=None).first():
        return jsonify({"message": "Cannot remove book. It is currently loaned out."}), 400

    book.deleted = True
    db.session.commit()

    return jsonify({"message": f"Book ID {book_id} has been marked as deleted."}), 200



@app.route('/remove_customer', methods=['DELETE'])
def remove_customer():
    data = request.json
    customer_id = data.get('customerId')

    if not customer_id:
        return jsonify({"message": "Customer ID is required."}), 400

    customer = Customers.query.get(customer_id)
    if not customer or customer.deleted:
        return jsonify({"message": "Customer not found or already deleted."}), 404

    if Loan.query.filter_by(cust_id=customer_id, return_date=None).first():
        return jsonify({"message": "Cannot remove customer. They have active loans."}), 400

    customer.deleted = True
    db.session.commit()

    return jsonify({"message": f"Customer ID {customer_id} has been marked as deleted."}), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
