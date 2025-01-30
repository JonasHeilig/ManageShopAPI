import os
import logging
from datetime import datetime


class LogSystem:
    def __init__(self):
        # Create log folder
        self.log_folder = os.path.join(os.getcwd(), "serverlogs")
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

        # Generate log filename
        log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.log")
        self.log_file_path = os.path.join(self.log_folder, log_filename)

        # Initialize logger
        self.logger = logging.getLogger("ServerLogger")
        self.logger.setLevel(logging.DEBUG)  # Default log level

        # File handler
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.DEBUG)

        # Define log format
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)

    def initialize(self, description):
        """
        Initializes the log by writing the first entry in the log file
        with a description of the server or the test.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f" Log initialized at {timestamp} ")
        self.logger.info(f" Description: {description} ")

    def log_info(self, message):
        """Logs an INFO level message."""
        self.logger.info(f" {message} ")

    def log_warning(self, message):
        """Logs a WARNING level message."""
        self.logger.warning(f" {message} ")

    def log_error(self, message):
        """Logs an ERROR level message."""
        self.logger.error(f" {message} ")