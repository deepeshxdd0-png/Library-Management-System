"""Configuration settings for Library Management System."""

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'library_db',
    'user': 'postgres',
    'password': 'Deepesh@123'
}

# Library Settings
DEFAULT_BORROWING_PERIOD_DAYS = 14
DEFAULT_BORROWING_LIMIT = 5
DEFAULT_FINE_RATE_PER_DAY = 0.50

# Scraper Settings
SCRAPER_BASE_URL = "https://www.gutenberg.org"
SCRAPER_DELAY_SECONDS = 1

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True

# Logging Settings
LOG_FILE = "lms_log.txt"
LOG_LEVEL = "INFO"

