import time
import logging
import os
from posting_system import PostingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConfigMonitor:
    def __init__(self):
        self.posting_system = PostingSystem()
        self.config_file = os.path.expanduser('~/Library/Mobile Documents/com~apple~Pages/Documents/post_config.pages')
        self.last_mtime = None
        logger.debug(f"Config monitor initialized, target file: {self.config_file}")

    def check_file_change(self):
        """Check if the configuration file has changed"""
        try:
            if os.path.exists(self.config_file):
                current_mtime = os.path.getmtime(self.config_file)
                
                # If this is the first check or the file has changed
                if self.last_mtime is None or current_mtime > self.last_mtime:
                    logger.info(f"Configuration file change detected: {self.config_file}")
                    self.last_mtime = current_mtime
                    
                    # Wait a moment to ensure file is completely written
                    time.sleep(1)
                    
                    # Generate new tweet content
                    logger.debug("Generating new tweet content...")
                    content = self.posting_system.generate_content()
                    if content:
                        logger.info("New tweet generated successfully")
                    else:
                        logger.error("Failed to generate tweet content")
            else:
                logger.debug("Configuration file not found")
                
        except Exception as e:
            logger.error(f"Error checking file change: {str(e)}")

def main():
    """Main function"""
    try:
        monitor = ConfigMonitor()
        logger.info(f"Starting to monitor configuration file: {monitor.config_file}")
        
        try:
            while True:
                monitor.check_file_change()
                time.sleep(2)  # Check every 2 seconds
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main()
