"""Script to generate comprehensive analytics report."""

import logging
from database.db_manager import DBManager
from analytics.reporting import AnalyticsReporter

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
    """Main function to generate report."""
    logger.info("Starting report generation")
    
    try:
        # Initialize components
        db_manager = DBManager()
        reporter = AnalyticsReporter(db_manager)
        
        # Generate full report
        report_file = reporter.generate_full_report("report.txt")
        logger.info(f"Report generated successfully: {report_file}")
        
        print("\n" + "=" * 80)
        print("Report generation completed successfully!")
        print(f"Report saved to: {report_file}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise
    finally:
        db_manager.close()


if __name__ == "__main__":
    main()

