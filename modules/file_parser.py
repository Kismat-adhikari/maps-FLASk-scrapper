"""
File Parser Module
Handles parsing and validation of CSV and Excel files containing search queries.
"""

import pandas as pd
import logging
from typing import List, Dict, Tuple


class FileParser:
    """Parses CSV and Excel files for search queries."""
    
    @staticmethod
    def parse_csv(file_path: str) -> List[Dict]:
        """
        Parse a CSV file containing search queries.
        Expected columns: keyword, location (or zip_code), url (optional)
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of dictionaries with query data
        """
        logger = logging.getLogger(__name__)
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully read CSV file: {file_path}")
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Clean up the data
            cleaned_data = []
            for row in data:
                # Support both 'location' and 'zip_code' columns
                location = row.get('location', row.get('zip_code', ''))
                cleaned_row = {
                    'keyword': str(row.get('keyword', '')).strip(),
                    'zip_code': str(location).strip(),  # Store as zip_code for compatibility
                    'url': str(row.get('url', '')).strip() if pd.notna(row.get('url')) else ''
                }
                cleaned_data.append(cleaned_row)
            
            logger.info(f"Parsed {len(cleaned_data)} rows from CSV")
            return cleaned_data
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {file_path}")
            return []
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            return []
    
    @staticmethod
    def parse_excel(file_path: str) -> List[Dict]:
        """
        Parse an Excel file containing search queries.
        Expected columns: keyword, location (or zip_code), url (optional)
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            List of dictionaries with query data
        """
        logger = logging.getLogger(__name__)
        
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info(f"Successfully read Excel file: {file_path}")
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Clean up the data
            cleaned_data = []
            for row in data:
                # Support both 'location' and 'zip_code' columns
                location = row.get('location', row.get('zip_code', ''))
                cleaned_row = {
                    'keyword': str(row.get('keyword', '')).strip(),
                    'zip_code': str(location).strip(),  # Store as zip_code for compatibility
                    'url': str(row.get('url', '')).strip() if pd.notna(row.get('url')) else ''
                }
                cleaned_data.append(cleaned_row)
            
            logger.info(f"Parsed {len(cleaned_data)} rows from Excel")
            return cleaned_data
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            return []
    
    @staticmethod
    def validate_data(data: List[Dict]) -> Tuple[bool, str]:
        """
        Validate parsed data to ensure required fields are present and valid.
        
        Args:
            data: List of dictionaries with query data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger = logging.getLogger(__name__)
        
        if not data:
            return False, "No data to validate"
        
        # Check each row for required fields
        for idx, row in enumerate(data, start=1):
            # Check keyword
            keyword = row.get('keyword', '').strip()
            if not keyword or keyword == 'nan':
                return False, f"Row {idx}: Missing or empty 'keyword' field"
            
            # Check zip_code
            zip_code = row.get('zip_code', '').strip()
            if not zip_code or zip_code == 'nan':
                return False, f"Row {idx}: Missing or empty 'zip_code' field"
            
            # URL is optional, so we don't validate it
        
        logger.info(f"Validation passed for {len(data)} rows")
        return True, "Validation successful"
    
    @staticmethod
    def parse_file(file_path: str) -> Tuple[List[Dict], str]:
        """
        Parse a file (CSV or Excel) and validate the data.
        Automatically detects file type based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (data_list, error_message)
            If successful, error_message will be empty string
        """
        logger = logging.getLogger(__name__)
        
        # Determine file type
        if file_path.lower().endswith('.csv'):
            data = FileParser.parse_csv(file_path)
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            data = FileParser.parse_excel(file_path)
        else:
            return [], "Unsupported file format. Please upload CSV or Excel file."
        
        if not data:
            return [], "Failed to parse file or file is empty"
        
        # Validate the data
        is_valid, message = FileParser.validate_data(data)
        
        if not is_valid:
            logger.error(f"Validation failed: {message}")
            return [], message
        
        return data, ""
