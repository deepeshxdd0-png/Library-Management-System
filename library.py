"""Core Library Management System class."""

import logging
from typing import List, Dict, Optional
from datetime import date

from database.db_manager import DBManager
from database.exceptions import (
    BookNotAvailableError,
    BorrowLimitExceededError,
    BookNotFoundError,
    MemberNotFoundError,
    DatabaseError
)
from models.book import Book
from models.author import Author
from models.member import Member

logger = logging.getLogger(__name__)


class Library:
    """
    Core Library class managing all library operations.
    
    This class provides a high-level interface for library management operations
    including borrowing, returning, fine calculation, and member management.
    """
    
    def __init__(self, db_manager: DBManager):
        """
        Initialize the Library with a database manager.
        
        Args:
            db_manager: DBManager instance for database operations
        """
        self.db = db_manager
        logger.info("Library initialized")
    
    def register_member(self, member: Member) -> int:
        """
        Register a new member in the library.
        
        Args:
            member: Member object to register
            
        Returns:
            Generated member_id
        """
        try:
            member_id = self.db.insert_member(member)
            logger.info(f"Member registered: {member.full_name} (ID: {member_id})")
            return member_id
        except Exception as e:
            logger.error(f"Failed to register member: {e}")
            raise DatabaseError(f"Failed to register member: {e}")
    
    def get_member(self, member_id: int) -> Optional[Member]:
        """
        Retrieve member information.
        
        Args:
            member_id: Member ID
            
        Returns:
            Member object or None if not found
        """
        return self.db.get_member(member_id)
    
    def add_book(self, book: Book) -> int:
        """
        Add a new book to the library.
        
        Args:
            book: Book object to add
            
        Returns:
            Generated book_id
        """
        try:
            book_id = self.db.insert_book(book)
            logger.info(f"Book added: {book.title} (ID: {book_id})")
            return book_id
        except Exception as e:
            logger.error(f"Failed to add book: {e}")
            raise
    
    def get_book(self, isbn: str) -> Optional[Book]:
        """
        Retrieve book information by ISBN.
        
        Args:
            isbn: ISBN of the book
            
        Returns:
            Book object or None if not found
        """
        return self.db.get_book_by_isbn(isbn)
    
    def borrow_book(
        self,
        member_id: int,
        isbn: str,
        borrowing_period_days: int = 14
    ) -> Dict[str, any]:
        """
        Borrow a book with full transactional integrity.
        
        This method ensures atomic borrowing with all checks:
        - Book availability
        - Member status
        - Borrowing limits
        
        Args:
            member_id: Member ID borrowing the book
            isbn: ISBN of the book to borrow
            borrowing_period_days: Borrowing period in days
            
        Returns:
            Dictionary with borrowing details
            
        Raises:
            BookNotFoundError: If book doesn't exist
            BookNotAvailableError: If no copies available
            MemberNotFoundError: If member doesn't exist
            BorrowLimitExceededError: If member exceeded limit
        """
        try:
            log_id = self.db.borrow_book(member_id, isbn, borrowing_period_days)
            
            # Calculate due date
            from datetime import timedelta
            due_date = date.today() + timedelta(days=borrowing_period_days)
            
            return {
                'log_id': log_id,
                'member_id': member_id,
                'isbn': isbn,
                'borrow_date': date.today().isoformat(),
                'due_date': due_date.isoformat(),
                'status': 'success'
            }
        except (
            BookNotFoundError,
            BookNotAvailableError,
            MemberNotFoundError,
            BorrowLimitExceededError
        ) as e:
            logger.warning(f"Borrow operation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during borrow: {e}")
            raise DatabaseError(f"Borrow operation failed: {e}")
    
    def return_book(self, log_id: int) -> Dict[str, any]:
        """
        Return a book and calculate fines if overdue.
        
        Args:
            log_id: Borrowing log ID
            
        Returns:
            Dictionary with return details and any fines
        """
        try:
            # Return the book
            self.db.return_book(log_id)
            
            # Calculate and record fine if overdue
            fine_id = self.db.calculate_and_record_fine(log_id)
            
            result = {
                'log_id': log_id,
                'return_date': date.today().isoformat(),
                'status': 'success',
                'fine_charged': False
            }
            
            if fine_id:
                result['fine_charged'] = True
                result['fine_id'] = fine_id
                logger.info(f"Fine charged on return: fine_id {fine_id}")
            
            return result
        except Exception as e:
            logger.error(f"Return operation failed: {e}")
            raise DatabaseError(f"Return operation failed: {e}")
    
    def get_fines(self, member_id: int) -> List[Dict]:
        """
        Get outstanding fines for a member.
        
        Args:
            member_id: Member ID
            
        Returns:
            List of fine dictionaries
        """
        return self.db.get_outstanding_fines(member_id)
    
    def pay_fine(self, fine_id: int) -> bool:
        """
        Pay a fine.
        
        Args:
            fine_id: Fine ID to pay
            
        Returns:
            True if successful
        """
        return self.db.pay_fine(fine_id)
    
    def get_current_borrowings(self, member_id: int) -> List[Dict]:
        """
        Get currently borrowed books for a member.
        
        Args:
            member_id: Member ID
            
        Returns:
            List of borrowing log dictionaries
        """
        query = """
            SELECT bl.*, b.title, b.isbn, m.first_name || ' ' || m.last_name as member_name
            FROM BorrowingLog bl
            JOIN Books b ON bl.book_id = b.book_id
            JOIN Members m ON bl.member_id = m.member_id
            WHERE bl.member_id = %s AND bl.status IN ('Borrowed', 'Overdue')
            ORDER BY bl.borrow_date DESC
        """
        return self.db.execute_query(query, (member_id,), fetch=True) or []
    
    def seed_from_scraper(self, books_data: List[Dict]) -> None:
        """
        Seed the library database with scraped book data.
        
        Args:
            books_data: List of book dictionaries from scraper
        """
        self.db.seed_database(books_data)
    
    def close(self):
        """Close the library and database connections."""
        self.db.close()
        logger.info("Library closed")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create database manager
    db = DBManager()
    library = Library(db)
    
    # Example: Register a member
    member = Member(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="555-1234",
        address="123 Main St"
    )
    member_id = library.register_member(member)
    print(f"Registered member: {member_id}")
    
    library.close()

