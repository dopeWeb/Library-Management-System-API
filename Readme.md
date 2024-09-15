# Library Management System API

This is a Flask-based API for managing a library system. It allows you to manage books, customers, and loans. The application uses SQLAlchemy for ORM and SQLite as the database and i will add Frontend in the future

## Features

- **Add Customer**: Add new customers to the system.
- **Add Book**: Add new books to the system.
- **Loan Book**: Loan a book to a customer.
- **Return Book**: Return a book from a customer.
- **Display All Books**: Retrieve a list of all books.
- **Display All Customers**: Retrieve a list of all customers.
- **Display All Loans**: Retrieve a list of all loans.
- **Late Loans**: Retrieve a list of overdue books.
- **Find Book by Name**: Search for books by their name.
- **Find Customer by Name**: Search for customers by their name.
- **Remove Book**: Mark a book as deleted.
- **Remove Customer**: Mark a customer as deleted.

## Installation

1. **Clone the Repository**:

    ```bash
    git clone <repository-url>
    ```

2. **Create and Activate a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:

   Install a `requirements.txt` file with this command

    ```bash
    pip install -r .\requirements.txt

    ```

## Configuration

The application uses SQLite for simplicity. The database is stored in `library.db` by default. No additional configuration is required.

## Running the Application

1. **Run the Flask Application**:

    ```bash
    python app.py
    ```

   The application will run in debug mode by default on `http://127.0.0.1:5000`.

## API Endpoints

### **Add Customer**

- **Endpoint**: `/add_customer`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "name": "John Doe",
        "city": "New York",
        "age": 30,
        "email": "john.doe@example.com"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Customer 'John Doe' added successfully."
    }
    ```

### **Add Book**

- **Endpoint**: `/add_book`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "name": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "yearPublished": 1925,
        "type": 1
    }
    ```
- **Response**:
    ```json
    {
        "message": "Book 'The Great Gatsby' added successfully."
    }
    ```

### **Loan Book**

- **Endpoint**: `/loan_book`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "bookId": 1,
        "custId": 1
    }
    ```
- **Response**:
    ```json
    {
        "message": "Book ID 1 loaned to Customer ID 1.",
        "return_date": "2024-09-25T12:34:56+00:00"
    }
    ```

### **Return Book**

- **Endpoint**: `/return_book`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "bookId": 1,
        "custId": 1
    }
    ```
- **Response**:
    ```json
    {
        "message": "Book ID 1 returned by Customer ID 1.",
        "return_date": "2024-09-25T12:34:56+00:00"
    }
    ```

### **Display All Books**

- **Endpoint**: `/display_all_books`
- **Method**: `GET`
- **Response**:
    ```json
    [
        {
            "id": 1,
            "name": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "yearPublished": 1925,
            "type": 1
        }
    ]
    ```

### **Display All Customers**

- **Endpoint**: `/display_all_customers`
- **Method**: `GET`
- **Response**:
    ```json
    [
        {
            "id": 1,
            "name": "John Doe",
            "city": "New York",
            "age": 30,
            "email": "john.doe@example.com"
        }
    ]
    ```

### **Display All Loans**

- **Endpoint**: `/display_all_loans`
- **Method**: `GET`
- **Response**:
    ```json
    [
        {
            "custId": 1,
            "bookId": 1,
            "loanDate": "2024-09-20T12:34:56+00:00",
            "returnDate": "Not returned yet"
        }
    ]
    ```

### **Late Loans**

- **Endpoint**: `/late_loans`
- **Method**: `GET`
- **Response**:
    ```json
    [
        {
            "book_id": 1,
            "book_name": "The Great Gatsby",
            "customer_id": 1,
            "customer_name": "John Doe",
            "loan_date": "2024-09-20T12:34:56+00:00",
            "due_date": "2024-09-30T12:34:56+00:00"
        }
    ]
    ```

### **Find Book by Name**

- **Endpoint**: `/find_book_by_name`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "name": "The Great Gatsby"
    }
    ```
- **Response**:
    ```json
    [
        {
            "name": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "yearPublished": 1925,
            "type": 1
        }
    ]
    ```

### **Find Customer by Name**

- **Endpoint**: `/find_customer_by_name`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "name": "John Doe"
    }
    ```
- **Response**:
    ```json
    [
        {
            "name": "John Doe",
            "city": "New York",
            "age": 30,
            "email": "john.doe@example.com"
        }
    ]
    ```

### **Remove Book**

- **Endpoint**: `/remove_book`
- **Method**: `DELETE`
- **Request Body**:
    ```json
    {
        "bookId": 1
    }
    ```
- **Response**:
    ```json
    {
        "message": "Book ID 1 has been marked as deleted."
    }
    ```

### **Remove Customer**

- **Endpoint**: `/remove_customer`
- **Method**: `DELETE`
- **Request Body**:
    ```json
    {
        "customerId": 1
    }
    ```
- **Response**:
    ```json
    {
        "message": "Customer ID 1 has been marked as deleted."
    }
    ```

## Contributing

Feel free to submit issues or pull requests to improve the application. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

