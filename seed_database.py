"""Script to seed the database with scraped book data."""

import logging
from database.db_manager import DBManager
from scraper.scraper import BookScraper
from library import Library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lms_log.txt'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to seed the database."""
    logger.info("Starting database seeding process")
    
    try:
        # Initialize components
        db_manager = DBManager()
        library = Library(db_manager)
        scraper = BookScraper()
        
        # Scrape books from catalog
        logger.info("Scraping books from catalog...")
        books_data = scraper.scrape_from_catalog(limit=30)
        
        if not books_data:
            logger.warning("No books scraped. Exiting.")
            return
        
        # Seed database
        logger.info(f"Seeding database with {len(books_data)} books...")
        library.seed_from_scraper(books_data)
        
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        raise
    finally:
        library.close()


if __name__ == "__main__":
    main()

