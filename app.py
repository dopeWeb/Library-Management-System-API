from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from flask import Flask
from flask_cors import CORS
from dateutil import tz

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True, nullable=False)
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
    deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Loan CustID={self.cust_id}, BookID={self.book_id}>'

def get_max_loan_days(book_type):
    return {1: 10, 2: 5, 3: 2}.get(book_type, 0)


def seed_data():
    if not Customers.query.first():
        db.session.bulk_save_objects([
            Customers(name='John Doe', city='New York', age=30, email='john.doe@example.com'),
            Customers(name='Jane Smith', city='Los Angeles', age=25, email='jane.smith@example.com'),
            Customers(name='Jade Bmith', city='california', age=55, email='jade.bmith@example.com')
        ])
        db.session.commit()


    if not Books.query.first():
        db.session.bulk_save_objects([
            Books(name='The Great Gatsby', author='F. Scott Fitzgerald', year_published=1925, type=1),
            Books(name='1984', author='George Orwell', year_published=1949, type=2),
            Books(name='To Kill a Mockingbird', author='Harper Lee', year_published=1960, type=3),
            Books(name='Crime and Punishment', author='Fyodor Dostoevsky', year_published=1866, type=1),
        ])
        db.session.commit()


        

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json

    # Normalize field names to lowercase
    normalized_data = {
        'name': data.get('name') or data.get('Name'),
        'city': data.get('city') or data.get('City'),
        'age': data.get('age') or data.get('Age'),
        'email': data.get('email') or data.get('Email')
    }

    # Ensure all required fields are present
    if not normalized_data['name'] or not normalized_data['city'] or normalized_data['age'] is None or not normalized_data['email']:
        return jsonify({"message": "Missing required fields."}), 400

    if Customers.query.filter_by(email=normalized_data['email']).first():
        return jsonify({"message": "Customer with this email already exists."}), 400

    new_customer = Customers(
        name=normalized_data['name'],
        city=normalized_data['city'],
        age=normalized_data['age'],
        email=normalized_data['email']
    )
    db.session.add(new_customer)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while adding the customer: " + str(e)}), 500

    return jsonify({"message": f"Customer '{normalized_data['name']}' added successfully."}), 201




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
    book_name = data.get('bookName')
    customer_email = data.get('customerEmail')

    # Validate input
    if not book_name or not customer_email:
        return jsonify({"message": "Both book name and customer email are required."}), 400

    # Get the book ID based on the name
    book = Books.query.filter_by(name=book_name, deleted=False).first()
    if not book:
        return jsonify({"message": "Book not found."}), 404

    book_id = book.id

    # Get the customer ID based on the email
    customer = Customers.query.filter_by(email=customer_email, deleted=False).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    cust_id = customer.id

    # Check if the book is already loaned out to any customer
    active_loan_for_book = Loan.query.filter_by(book_id=book_id, return_date=None, deleted=False).first()
    if active_loan_for_book:
        return jsonify({"message": f"Book '{book_name}' is currently loaned out to another customer."}), 400

    # Check for existing loans for this customer
    existing_loan = Loan.query.filter_by(cust_id=cust_id, book_id=book_id).first()
    if existing_loan:
        if existing_loan.deleted:
            # Restore the deleted loan
            existing_loan.deleted = False
            existing_loan.loan_date = datetime.now(timezone.utc)
            existing_loan.return_date = None
            
            db.session.commit()
            return jsonify({"message": f"Book '{book_name}' loaned to customer '{customer_email}' successfully."}), 200
        else:
            return jsonify({"message": f"This book is currently loaned out to this customer '{customer_email}'."}), 400

    # Check how many active loans the customer has
    active_loans_count = Loan.query.filter_by(cust_id=cust_id, return_date=None, deleted=False).count()
    if active_loans_count >= 3:
        return jsonify({"message": "Customer cannot loan more than 3 books at the same time."}), 400

    # Create a new loan record
    new_loan = Loan(
        cust_id=cust_id,
        book_id=book_id,
        loan_date=datetime.now(timezone.utc),
        return_date=None,
        deleted=False
    )
    
    db.session.add(new_loan)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while processing the loan: " + str(e)}), 500

    return jsonify({"message": f"Book '{book_name}' loaned to customer '{customer_email}' successfully."}), 201


@app.route('/return_book', methods=['POST'])
def return_book():
    data = request.json
    book_name = data.get('bookName')
    customer_email = data.get('customerEmail')

    # Validate input
    if not book_name or not customer_email:
        return jsonify({"message": "Both book name and customer email are required."}), 400

    # Get the book ID based on the name
    book = Books.query.filter_by(name=book_name, deleted=False).first()
    if not book:
        return jsonify({"message": "Book not found."}), 404

    book_id = book.id

    # Get the customer ID based on the email
    customer = Customers.query.filter_by(email=customer_email, deleted=False).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    cust_id = customer.id

    # Find the active loan record
    loan = Loan.query.filter_by(cust_id=cust_id, book_id=book_id, return_date=None, deleted=False).first()
    if not loan:
        return jsonify({"message": f"No active loan found for customer '{customer_email}' and book '{book_name}'."}), 404

    # Mark the loan as returned
    loan.return_date = datetime.now(timezone.utc)
    loan.deleted = True

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while returning the book: " + str(e)}), 500

    return jsonify({"message": f"Book '{book_name}' returned successfully by customer '{customer_email}'."}), 200



          

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
    result = []
    
    for loan in loans:
        loan_date = loan.loan_date.astimezone(tz.tzlocal())
        return_date = loan.return_date.astimezone(tz.tzlocal()) if loan.return_date else "Not returned yet"
        result.append({
            "custId": loan.cust_id,
            "bookId": loan.book_id,
            "loanDate": loan_date.isoformat(),
            "returnDate": return_date if isinstance(return_date, str) else return_date.isoformat()
        })

    return jsonify(result), 200


@app.route('/late_loans', methods=['GET'])
def late_loans():
    # Get current UTC time
    now_utc = datetime.now(tz.tzutc())

    # Query for late loans
    late_loans_query = db.session.query(Loan, Books, Customers).join(Books).join(Customers).filter(
        Loan.return_date == None,
        Loan.loan_date + timedelta(days=get_max_loan_days(Books.type)) < now_utc
    ).all()

    # Prepare results
    result = []
    for loan, book, customer in late_loans_query:
        # Convert loan date and due date to local timezone
        loan_date_local = loan.loan_date.astimezone(tz.tzlocal())
        due_date_local = (loan.loan_date + timedelta(days=get_max_loan_days(book.type))).astimezone(tz.tzlocal())

        result.append({
            "book_id": book.id,
            "book_name": book.name,
            "customer_id": customer.id,
            "customer_name": customer.name,
            "loan_date": loan_date_local.isoformat(),
            "due_date": due_date_local.isoformat()
        })

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
    book_name = data.get('bookName')
    

    # Validate input
    if not book_name:
        return jsonify({"message": " Book name are required."}), 400

    # Get the book based on the name
    book = Books.query.filter_by(name=book_name, deleted=False).first()
    if not book:
        return jsonify({"message": "Book not found."}), 404

    # Check if the book is currently loaned out
    if Loan.query.filter_by(book_id=book.id, return_date=None).first():
        return jsonify({"message": "Cannot remove book. It is currently loaned out."}), 400

    # Mark the book as deleted
    book.deleted = True
    db.session.commit()

    return jsonify({"message": f"Book '{book_name}' has been marked as deleted."}), 200

@app.route('/remove_customer', methods=['DELETE'])
def remove_customer():
    data = request.json
    customer_email = data.get('customerEmail')

    # Validate input
    if not customer_email:
        return jsonify({"message": "Customer email is required."}), 400

    customer = Customers.query.filter_by(email=customer_email, deleted=False).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    # Check if the customer has active loans
    if Loan.query.filter_by(cust_id=customer.id, return_date=None).first():
        return jsonify({"message": "Cannot remove customer. They have active loans."}), 400

    # Mark the customer as deleted
    customer.deleted = True
    db.session.commit()

    return jsonify({"message": f"Customer '{customer_email}' has been marked as deleted."}), 200

@app.route('/restore_book', methods=['POST'])
def restore_book():
    data = request.json
    book_name = data.get('bookName')

    # Validate input
    if not book_name:
        return jsonify({"message": "Book name is required."}), 400

    book = Books.query.filter_by(name=book_name, deleted=True).first()
    if not book:
        return jsonify({"message": "Deleted book not found."}), 404

    # Restore the deleted book
    book.deleted = False
    db.session.commit()

    return jsonify({"message": f"Book '{book_name}' has been restored."}), 200


@app.route('/restore_customer', methods=['POST'])
def restore_customer():
    data = request.json
    customer_email = data.get('customerEmail')

    # Validate input
    if not customer_email:
        return jsonify({"message": "Customer email is required."}), 400

    customer = Customers.query.filter_by(email=customer_email, deleted=True).first()
    if not customer:
        return jsonify({"message": "Deleted customer not found."}), 404

    # Restore the deleted customer
    customer.deleted = False
    db.session.commit()

    return jsonify({"message": f"Customer '{customer_email}' has been restored."}), 200



@app.route('/get_book_id_by_name', methods=['GET'])
def get_book_id_by_name():
    name = request.args.get('name')
    book = Books.query.filter_by(name=name).first()
    if book:
        return jsonify({"id": book.id}), 200
    return jsonify({"message": "Book not found."}), 404



@app.route('/get_customer_id_by_email', methods=['GET'])
def get_customer_id_by_email():
    email = request.args.get('email')
    customer = Customers.query.filter_by(email=email).first()
    if customer:
        return jsonify({"id": customer.id}), 200
    return jsonify({"message": "Customer not found."}), 404



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
