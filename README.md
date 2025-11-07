# Advanced Library Management System (LMS)

A production-grade Library Management System built with Python, featuring transactional integrity, web scraping, PostgreSQL database, RESTful API, and comprehensive analytics.

## Features

### Core Functionality
- **Transactional Integrity**: Atomic borrowing operations with rollback on failure
- **Web Scraping**: Automated book data acquisition from public sources
- **PostgreSQL Database**: Normalized schema with proper indexing and constraints
- **RESTful API**: FastAPI-based API with OpenAPI documentation
- **Analytics & Reporting**: Comprehensive reporting system with SQL analytics

### Key Capabilities
- Member registration and management
- Book catalog management with ISBN tracking
- Book borrowing with availability checks and limits
- Return processing with automatic fine calculation
- Fine management and payment tracking
- Multi-author book support
- Genre categorization
- Overdue book tracking
- Monthly and genre-based borrowing trends
- Active member identification

## Project Structure

```
library/
├── models/              # OOP models (Book, Author, Member)
│   ├── __init__.py
│   ├── book.py
│   ├── author.py
│   └── member.py
├── database/           # Database management
│   ├── __init__.py
│   ├── db_manager.py   # Transactional DB operations
│   └── exceptions.py   # Custom exceptions
├── scraper/            # Web scraping
│   ├── __init__.py
│   └── scraper.py      # Book data scraper
├── api/                # RESTful API
│   ├── __init__.py
│   ├── models.py       # Pydantic models
│   └── routes.py       # API endpoints
├── analytics/          # Reporting and analytics
│   ├── __init__.py
│   └── reporting.py    # SQL analytics queries
├── main.py             # FastAPI application entry point
├── library.py          # Core Library class
├── seed_database.py    # Database seeding script
├── generate_report.py  # Analytics report generator
├── config.py           # Configuration settings
├── schema.sql          # PostgreSQL schema definition
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── report.txt          # Sample analytics report
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip package manager

### Step 1: Clone and Install Dependencies

```bash
cd library
pip install -r requirements.txt
```

### Step 2: PostgreSQL Database Setup

1. Install PostgreSQL if not already installed:
   - **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - **macOS**: `brew install postgresql`
   - **Linux**: `sudo apt-get install postgresql` (Ubuntu/Debian)

2. Create database and user:
```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE library_db;

-- Create user (optional)
CREATE USER library_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;

-- Connect to library_db
\c library_db
```

3. Create schema:
```bash
psql -U postgres -d library_db -f schema.sql
```

### Step 3: Configure Database Connection

Update database credentials in `database/db_manager.py` or `config.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'library_db',
    'user': 'postgres',  # or 'library_user'
    'password': 'your_password'
}
```

### Step 4: Seed the Database

Scrape and populate the database with book data:

```bash
python seed_database.py
```

This will:
- Scrape books from Project Gutenberg
- Parse book metadata (title, authors, ISBN, genre, synopsis)
- Insert authors with de-duplication
- Insert books with author relationships
- Handle duplicate ISBN errors gracefully

Expected output:
```
INFO - Starting database seeding process
INFO - Scraping books from catalog...
INFO - Successfully scraped: Pride and Prejudice
INFO - Successfully scraped: The Adventures of Huckleberry Finn
...
INFO - Database seeding completed successfully
```

## Running the Application

### Start the RESTful API Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

### Generate Analytics Report

```bash
python generate_report.py
```

This generates a comprehensive `report.txt` with:
- Top 5 prolific authors
- Borrowing trends by month
- Borrowing trends by genre
- Top 10 most popular books
- Active members (last 90 days)
- Overdue books with calculated fines

## API Endpoints

### Member Management

#### Register a New Member
```http
POST /api/members
Content-Type: application/json

{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "phone": "555-1234",
    "address": "456 Oak Avenue",
    "membership_type": "Premium",
    "borrowing_limit": 10
}
```

Response:
```json
{
    "member_id": 1,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "phone": "555-1234",
    "address": "456 Oak Avenue",
    "membership_type": "Premium",
    "member_since": "2024-01-15T10:30:00",
    "status": "Active",
    "borrowing_limit": 10
}
```

### Book Operations

#### Get Book Details by ISBN
```http
GET /api/books/{isbn}
```

Example: `GET /api/books/9780141441146`

Response:
```json
{
    "book_id": 1,
    "isbn": "9780141441146",
    "title": "Pride and Prejudice",
    "publication_year": 1813,
    "genre": ["Fiction", "Romance"],
    "synopsis": "A romantic novel of manners...",
    "total_copies": 1,
    "available_copies": 1,
    "language": "English",
    "publisher": "Project Gutenberg",
    "authors": [
        {
            "author_id": 1,
            "first_name": "Jane",
            "last_name": "Austen",
            "birth_year": 1775,
            "nationality": "British",
            "biography": "English novelist..."
        }
    ]
}
```

### Borrowing Operations

#### Borrow a Book
```http
POST /api/borrow
Content-Type: application/json

{
    "member_id": 1,
    "isbn": "9780141441146",
    "borrowing_period_days": 14
}
```

Response:
```json
{
    "log_id": 1,
    "member_id": 1,
    "isbn": "9780141441146",
    "borrow_date": "2024-01-15",
    "due_date": "2024-01-29",
    "status": "success"
}
```

**Transactional Integrity**: This operation:
1. Checks book availability (locks row)
2. Validates member status and borrowing limit
3. Decrements available_copies
4. Creates borrowing log entry
5. Rolls back all changes if any step fails

Error Responses:
- `404`: Book or member not found
- `400`: Book not available or borrowing limit exceeded

#### Return a Book
```http
POST /api/return
Content-Type: application/json

{
    "log_id": 1
}
```

Response:
```json
{
    "log_id": 1,
    "return_date": "2024-01-30",
    "status": "success",
    "fine_charged": true,
    "fine_id": 1
}
```

**Automatic Fine Calculation**: If the book is overdue, a fine is automatically calculated and recorded.

### Fine Management

#### Get Outstanding Fines
```http
GET /api/fines/{member_id}
```

Example: `GET /api/fines/1`

Response:
```json
[
    {
        "fine_id": 1,
        "log_id": 1,
        "member_id": 1,
        "amount": 0.50,
        "fine_rate_per_day": 0.50,
        "days_overdue": 1,
        "calculation_date": "2024-01-30T12:00:00",
        "status": "Unpaid",
        "payment_date": null,
        "title": "Pride and Prejudice",
        "isbn": "9780141441146",
        "due_date": "2024-01-29",
        "return_date": "2024-01-30"
    }
]
```

#### Pay a Fine
```http
POST /api/fines/pay
Content-Type: application/json

{
    "fine_id": 1
}
```

Response:
```json
{
    "message": "Fine 1 paid successfully",
    "status": "success"
}
```

### Member Queries

#### Get Current Borrowings
```http
GET /api/borrowings/{member_id}
```

Example: `GET /api/borrowings/1`

### Health Check
```http
GET /api/health
```

## Database Schema

### Key Tables

**Authors**: Author information with unique constraints on (first_name, last_name)
**Books**: Book catalog with ISBN uniqueness, genre array, availability tracking
**Members**: Member accounts with borrowing limits and status
**BorrowingLog**: Transaction log for all borrow/return operations
**Fines**: Overdue fine records with daily rate calculation
**BookAuthors**: Junction table for many-to-many author relationships

### Indexes

- ISBN lookup: `idx_books_isbn`
- Genre searching: `idx_books_genre` (GIN index)
- Author name search: `idx_authors_name`
- Due date queries: `idx_borrowing_log_due_date`
- Member status: `idx_members_status`
- Fine status: `idx_fines_status`

### Views

**ActiveBorrowings**: Current borrowings with overdue calculation
**MemberStats**: Aggregated member borrowing statistics

## Transactional Integrity

The `borrow_book` method in `DBManager` implements full atomicity:

```python
def borrow_book(member_id, isbn, borrowing_period_days=14):
    with self.transaction() as conn:  # Starts transaction
        with conn.cursor() as cur:
            # Lock and check book
            cur.execute("SELECT ... FROM Books WHERE isbn = %s FOR UPDATE", ...)
            
            # Lock and check member
            cur.execute("SELECT ... FROM Members WHERE ... FOR UPDATE", ...)
            
            # Update availability
            cur.execute("UPDATE Books SET available_copies = ...", ...)
            
            # Insert log
            cur.execute("INSERT INTO BorrowingLog ...", ...)
            
        # Auto-commit on success, auto-rollback on exception
```

All operations use `FOR UPDATE` row locking to prevent race conditions.

## Custom Exceptions

- `BookNotAvailableError`: Book has no available copies
- `BorrowLimitExceededError`: Member reached borrowing limit
- `FineNotPaidError`: Operation requires unpaid fines
- `DuplicateISBNError`: Attempted to add duplicate ISBN
- `MemberNotFoundError`: Member ID not found
- `BookNotFoundError`: ISBN not found
- `DatabaseError`: General database operation failure

## Logging

Logs are written to:
- **Console**: Real-time output
- **File**: `lms_log.txt` (time-stamped)

Log levels:
- `INFO`: Normal operations
- `WARNING`: Recoverable errors (e.g., duplicate ISBN)
- `ERROR`: Critical failures
- `DEBUG`: Detailed debugging information

## Configuration

Key settings in `config.py`:

```python
DEFAULT_BORROWING_PERIOD_DAYS = 14
DEFAULT_BORROWING_LIMIT = 5
DEFAULT_FINE_RATE_PER_DAY = 0.50
SCRAPER_BASE_URL = "https://www.gutenberg.org"
```

## Usage Examples

### Python Script Integration

```python
from database.db_manager import DBManager
from library import Library
from models.book import Book, Author
from models.member import Member

# Initialize
db = DBManager(host='localhost', database='library_db', user='postgres', password='postgres')
library = Library(db)

# Register member
member = Member(
    first_name="Alice",
    last_name="Johnson",
    email="alice@example.com"
)
member_id = library.register_member(member)

# Borrow book
result = library.borrow_book(member_id=member_id, isbn="9780141441146")
print(f"Borrowed until: {result['due_date']}")

# Return book (with automatic fine calculation)
result = library.return_book(log_id=1)
if result['fine_charged']:
    print(f"Fine charged: ${result['fine_id']}")

# Get fines
fines = library.get_fines(member_id)
for fine in fines:
    print(f"Outstanding: ${fine['amount']}")

# Cleanup
library.close()
```

## Testing

### Manual Testing with cURL

```bash
# Register member
curl -X POST http://localhost:8000/api/members \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com"}'

# Get book
curl http://localhost:8000/api/books/9780141441146

# Borrow book
curl -X POST http://localhost:8000/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"member_id":1,"isbn":"9780141441146"}'

# Generate report
python generate_report.py
```

### Database Verification

```sql
-- Check book availability
SELECT isbn, title, available_copies, total_copies FROM Books LIMIT 10;

-- View active borrowings
SELECT * FROM ActiveBorrowings;

-- Member statistics
SELECT * FROM MemberStats WHERE total_borrows > 0;

-- Overdue tracking
SELECT * FROM BorrowingLog WHERE due_date < CURRENT_DATE AND status = 'Borrowed';
```

## Advanced Features

### Genre Analytics

```python
from analytics.reporting import AnalyticsReporter

reporter = AnalyticsReporter(db_manager)

# Genre-based trends
genres = reporter.get_borrowing_trends_by_genre()
for genre in genres:
    print(f"{genre['genre']}: {genre['borrow_count']} borrows")
```

### Active Member Detection

```python
# Members with 5+ borrows in last 60 days
active = reporter.get_active_members(days=60, min_borrows=5)
```

### Estimated Fines

```python
overdue = reporter.get_overdue_books_with_fines()
for book in overdue:
    print(f"{book['title']}: ${book['estimated_fine']:.2f}")
```

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U postgres -h localhost -d library_db

# Check if database exists
psql -U postgres -l | grep library_db

# Verify schema
psql -U postgres -d library_db -c "\dt"
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Scraper Timeouts

Adjust delays in `scraper/scraper.py`:
```python
time.sleep(2)  # Increase delay
```

### Transaction Lock Issues

PostgreSQL may lock on transactions. Check active connections:
```sql
SELECT * FROM pg_stat_activity WHERE datname = 'library_db';
```

## Performance Considerations

- **Connection Pooling**: DBManager uses connection pooling (1-10 connections)
- **Indexes**: All foreign keys and frequently queried columns are indexed
- **Query Optimization**: Views pre-aggregate common queries
- **Scalability**: FastAPI handles async operations efficiently

## Future Enhancements

- [ ] Authentication and authorization (JWT tokens)
- [ ] Multi-library branch support
- [ ] Book reservation system
- [ ] Email notifications for due dates
- [ ] Advanced search with full-text indexing
- [ ] Book recommendation engine
- [ ] Mobile app integration
- [ ] Admin dashboard with charts

## License

This project is provided as-is for educational and commercial use.

## Contributors

Developed as a production-grade Library Management System demonstration.

## Support

For issues or questions, review:
- Database logs in `lms_log.txt`
- PostgreSQL logs in system log files
- API documentation at `/docs` endpoint

---

**Version**: 1.0.0  
**Last Updated**: 2025

