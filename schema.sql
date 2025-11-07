-- Library Management System Database Schema
-- PostgreSQL Schema with comprehensive indexing and constraints

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Authors Table
CREATE TABLE IF NOT EXISTS Authors (
    author_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_year INTEGER,
    nationality VARCHAR(100),
    biography TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(first_name, last_name)
);

CREATE INDEX idx_authors_name ON Authors(last_name, first_name);

-- Books Table
CREATE TABLE IF NOT EXISTS Books (
    book_id SERIAL PRIMARY KEY,
    isbn VARCHAR(17) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    publication_year INTEGER,
    genre VARCHAR(100)[] DEFAULT '{}',
    synopsis TEXT,
    total_copies INTEGER DEFAULT 1 CHECK (total_copies >= 0),
    available_copies INTEGER DEFAULT 1 CHECK (available_copies >= 0),
    language VARCHAR(50) DEFAULT 'English',
    publisher VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_available_copies CHECK (available_copies <= total_copies)
);

CREATE INDEX idx_books_isbn ON Books(isbn);
CREATE INDEX idx_books_title ON Books(title);
CREATE INDEX idx_books_genre ON Books USING GIN(genre);

-- Book-Author Junction Table (Many-to-Many Relationship)
CREATE TABLE IF NOT EXISTS BookAuthors (
    book_author_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES Books(book_id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES Authors(author_id) ON DELETE CASCADE,
    UNIQUE(book_id, author_id)
);

CREATE INDEX idx_book_authors_book ON BookAuthors(book_id);
CREATE INDEX idx_book_authors_author ON BookAuthors(author_id);

-- Members Table
CREATE TABLE IF NOT EXISTS Members (
    member_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    membership_type VARCHAR(50) DEFAULT 'Standard',
    member_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended')),
    borrowing_limit INTEGER DEFAULT 5 CHECK (borrowing_limit >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_members_email ON Members(email);
CREATE INDEX idx_members_name ON Members(last_name, first_name);
CREATE INDEX idx_members_status ON Members(status);

-- BorrowingLog Table
CREATE TABLE IF NOT EXISTS BorrowingLog (
    log_id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES Members(member_id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES Books(book_id) ON DELETE CASCADE,
    borrow_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) DEFAULT 'Borrowed' CHECK (status IN ('Borrowed', 'Returned', 'Overdue', 'Lost')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_borrowing_log_member ON BorrowingLog(member_id);
CREATE INDEX idx_borrowing_log_book ON BorrowingLog(book_id);
CREATE INDEX idx_borrowing_log_due_date ON BorrowingLog(due_date);
CREATE INDEX idx_borrowing_log_status ON BorrowingLog(status);

-- Fines Table
CREATE TABLE IF NOT EXISTS Fines (
    fine_id SERIAL PRIMARY KEY,
    log_id INTEGER NOT NULL REFERENCES BorrowingLog(log_id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES Members(member_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    fine_rate_per_day DECIMAL(5, 2) NOT NULL DEFAULT 0.50,
    days_overdue INTEGER NOT NULL DEFAULT 0 CHECK (days_overdue >= 0),
    calculation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Unpaid' CHECK (status IN ('Unpaid', 'Paid', 'Waived')),
    payment_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fines_member ON Fines(member_id);
CREATE INDEX idx_fines_status ON Fines(status);
CREATE INDEX idx_fines_log ON Fines(log_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_authors_updated_at BEFORE UPDATE ON Authors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON Books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_members_updated_at BEFORE UPDATE ON Members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_borrowing_log_updated_at BEFORE UPDATE ON BorrowingLog
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fines_updated_at BEFORE UPDATE ON Fines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for current active borrowings
CREATE OR REPLACE VIEW ActiveBorrowings AS
SELECT 
    bl.log_id,
    bl.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    m.email AS member_email,
    bl.book_id,
    b.title,
    b.isbn,
    bl.borrow_date,
    bl.due_date,
    bl.return_date,
    CASE 
        WHEN bl.due_date < CURRENT_DATE AND bl.status = 'Borrowed' THEN CURRENT_DATE - bl.due_date
        ELSE 0
    END AS days_overdue
FROM BorrowingLog bl
JOIN Members m ON bl.member_id = m.member_id
JOIN Books b ON bl.book_id = b.book_id
WHERE bl.status IN ('Borrowed', 'Overdue');

-- View for member borrowing statistics
CREATE OR REPLACE VIEW MemberStats AS
SELECT 
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    m.email,
    m.status AS membership_status,
    COUNT(DISTINCT bl.log_id) AS total_borrows,
    COUNT(DISTINCT CASE WHEN bl.status = 'Borrowed' THEN bl.log_id END) AS current_borrows,
    COUNT(DISTINCT CASE WHEN bl.status = 'Returned' THEN bl.log_id END) AS returned_count,
    COALESCE(SUM(f.amount), 0) AS total_fines_owed
FROM Members m
LEFT JOIN BorrowingLog bl ON m.member_id = bl.member_id
LEFT JOIN Fines f ON m.member_id = f.member_id AND f.status = 'Unpaid'
GROUP BY m.member_id, m.first_name, m.last_name, m.email, m.status;

