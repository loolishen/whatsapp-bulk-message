"""
OCR Service for processing Malaysian IC cards and receipts
"""
import re
import json
import requests
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MalaysianICParser:
    """Parser for Malaysian IC numbers"""
    
    STATE_CODES = {
        '01': 'JHR', '02': 'KDH', '03': 'KTN', '04': 'MLK', '05': 'NSN',
        '06': 'PHG', '07': 'PNG', '08': 'PRK', '09': 'PLS', '10': 'SEL',
        '11': 'TRG', '12': 'SBH', '13': 'SWK', '14': 'KUL', '15': 'LBN',
        '16': 'PJY'
    }
    
    @staticmethod
    def parse_ic_number(ic_number: str) -> Dict:
        """
        Parse Malaysian IC number to extract information
        
        Format: YYMMDD-SS-GGGV
        YY: Birth year (00-30 = 2000-2030, 31-99 = 1931-1999)
        MM: Birth month (01-12)
        DD: Birth day (01-31)
        SS: State code (01-16)
        GGG: Sequential number
        V: Gender (odd = male, even = female)
        """
        if not ic_number or len(ic_number) != 12:
            return {'valid': False, 'error': 'Invalid IC number format'}
        
        try:
            # Remove any dashes or spaces
            ic_clean = re.sub(r'[-\s]', '', ic_number)
            
            if len(ic_clean) != 12 or not ic_clean.isdigit():
                return {'valid': False, 'error': 'IC number must be 12 digits'}
            
            # Extract components
            birth_year = int(ic_clean[:2])
            birth_month = int(ic_clean[2:4])
            birth_day = int(ic_clean[4:6])
            state_code = ic_clean[6:8]
            gender_digit = int(ic_clean[-1])
            
            # Convert birth year
            if birth_year <= 30:
                full_birth_year = 2000 + birth_year
            else:
                full_birth_year = 1900 + birth_year
            
            # Validate date
            try:
                birth_date = date(full_birth_year, birth_month, birth_day)
            except ValueError:
                return {'valid': False, 'error': 'Invalid birth date in IC'}
            
            # Calculate age
            today = date.today()
            age = today.year - birth_date.year
            if today.month < birth_month or (today.month == birth_month and today.day < birth_day):
                age -= 1
            
            # Determine gender
            gender = 'M' if gender_digit % 2 == 1 else 'F'
            
            # Get state
            state = MalaysianICParser.STATE_CODES.get(state_code, 'N/A')
            
            return {
                'valid': True,
                'ic_number': ic_clean,
                'birth_date': birth_date.strftime('%Y-%m-%d'),
                'age': age,
                'gender': gender,
                'state': state,
                'state_code': state_code,
                'birth_year': full_birth_year,
                'birth_month': birth_month,
                'birth_day': birth_day
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Error parsing IC: {str(e)}'}


class ReceiptParser:
    """Parser for receipt text extracted via OCR"""
    
    @staticmethod
    def parse_receipt_text(text: str) -> Dict:
        """
        Parse receipt text to extract purchase information
        """
        if not text:
            return {'valid': False, 'error': 'No text provided'}
        
        try:
            # Clean text
            text_clean = re.sub(r'\s+', ' ', text.strip())
            
            # Extract total amount
            total_amount = ReceiptParser._extract_total_amount(text_clean)
            
            # Extract date
            purchase_date = ReceiptParser._extract_date(text_clean)
            
            # Extract items
            items = ReceiptParser._extract_items(text_clean)
            
            return {
                'valid': True,
                'total_amount': total_amount,
                'purchase_date': purchase_date,
                'items': items,
                'raw_text': text_clean
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Error parsing receipt: {str(e)}'}
    
    @staticmethod
    def _extract_total_amount(text: str) -> Optional[Decimal]:
        """Extract total amount from receipt text"""
        # Common patterns for total amount
        patterns = [
            r'total[:\s]*rm\s*(\d+\.?\d*)',
            r'total[:\s]*\$?\s*(\d+\.?\d*)',
            r'jumlah[:\s]*rm\s*(\d+\.?\d*)',
            r'amount[:\s]*rm\s*(\d+\.?\d*)',
            r'grand\s*total[:\s]*rm\s*(\d+\.?\d*)',
            r'rm\s*(\d+\.?\d*)\s*total',
            r'(\d+\.?\d*)\s*rm\s*total',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return Decimal(match.group(1))
                except:
                    continue
        
        # Fallback: look for any RM amount at the end of lines
        rm_pattern = r'rm\s*(\d+\.?\d*)'
        matches = re.findall(rm_pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Return the largest amount found
                amounts = [Decimal(m) for m in matches]
                return max(amounts)
            except:
                pass
        
        return None
    
    @staticmethod
    def _extract_date(text: str) -> Optional[str]:
        """Extract purchase date from receipt text"""
        # Common date patterns
        patterns = [
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{2,4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{2,4})',  # DD Mon YYYY
        ]
        
        month_names = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 3:
                        if pattern == patterns[2]:  # DD Mon YYYY
                            day, month_name, year = match.groups()
                            month = month_names.get(month_name.lower(), 1)
                            year = int(year)
                            if year < 100:
                                year += 2000 if year < 50 else 1900
                        else:
                            part1, part2, part3 = match.groups()
                            # Try to determine format
                            if len(part3) == 4:  # YYYY format
                                if int(part1) > 12:  # DD/MM/YYYY
                                    day, month, year = int(part1), int(part2), int(part3)
                                else:  # MM/DD/YYYY or YYYY/MM/DD
                                    if int(part1) > 31:  # YYYY/MM/DD
                                        year, month, day = int(part1), int(part2), int(part3)
                                    else:  # MM/DD/YYYY
                                        month, day, year = int(part1), int(part2), int(part3)
                            else:  # YY format
                                if int(part1) > 12:  # DD/MM/YY
                                    day, month, year = int(part1), int(part2), int(part3)
                                    year += 2000 if year < 50 else 1900
                                else:  # MM/DD/YY
                                    month, day, year = int(part1), int(part2), int(part3)
                                    year += 2000 if year < 50 else 1900
                        
                        # Validate date
                        purchase_date = date(year, month, day)
                        return purchase_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        return None
    
    @staticmethod
    def _extract_items(text: str) -> List[Dict]:
        """Extract items from receipt text"""
        items = []
        
        # Look for item patterns
        # This is a simplified version - you might want to enhance this based on your receipt format
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for lines that might contain items with prices
            # Pattern: Item name ... RM amount
            item_match = re.search(r'(.+?)\s+rm\s*(\d+\.?\d*)', line, re.IGNORECASE)
            if item_match:
                item_name = item_match.group(1).strip()
                try:
                    price = Decimal(item_match.group(2))
                    if price > 0 and len(item_name) > 2:  # Basic validation
                        items.append({
                            'name': item_name,
                            'price': float(price),
                            'quantity': 1
                        })
                except:
                    continue
        
        return items


class OCRService:
    """Main OCR service for processing images"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OCR_API_KEY', None)
        self.api_url = getattr(settings, 'OCR_API_URL', 'https://api.ocr.space/parse/image')
    
    def process_image(self, image_url: str, image_type: str = 'OTHER') -> Dict:
        """
        Process image using OCR service
        
        Args:
            image_url: URL of the image to process
            image_type: Type of image ('IC', 'RECEIPT', 'OTHER')
        
        Returns:
            Dict with processing results
        """
        try:
            # For demo purposes, we'll use a mock OCR service
            # In production, you would integrate with a real OCR service like:
            # - Google Cloud Vision API
            # - AWS Textract
            # - Azure Computer Vision
            # - OCR.space API
            
            if image_type == 'IC':
                return self._process_ic_image(image_url)
            elif image_type == 'RECEIPT':
                return self._process_receipt_image(image_url)
            else:
                return self._process_generic_image(image_url)
                
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0
            }
    
    def _process_ic_image(self, image_url: str) -> Dict:
        """Process IC card image"""
        # Mock OCR result for IC card
        # In production, this would call a real OCR service
        mock_text = """
        MALAYSIA
        KAD PENGENALAN
        NAMA: AHMAD BIN ALI
        NO. KAD: 901201-10-1234
        TARIKH LAHIR: 01/12/1990
        TEMPAT LAHIR: JOHOR
        """
        
        # Extract IC number from text
        ic_match = re.search(r'(\d{6}-\d{2}-\d{4})', mock_text)
        if ic_match:
            ic_number = ic_match.group(1).replace('-', '')
            
            # Parse IC number
            ic_parser = MalaysianICParser()
            parsed_data = ic_parser.parse_ic_number(ic_number)
            
            if parsed_data['valid']:
                return {
                    'success': True,
                    'extracted_text': mock_text,
                    'confidence': 0.95,
                    'extracted_data': parsed_data,
                    'image_type': 'IC'
                }
        
        return {
            'success': False,
            'error': 'Could not extract valid IC number',
            'extracted_text': mock_text,
            'confidence': 0.3
        }
    
    def _process_receipt_image(self, image_url: str) -> Dict:
        """Process receipt image"""
        # Mock OCR result for receipt
        mock_text = """
        ABC STORE SDN BHD
        123 MAIN STREET
        KUALA LUMPUR
        
        Date: 15/08/2024
        Time: 14:30
        
        Item 1                    RM 25.50
        Item 2                    RM 15.00
        Item 3                    RM 8.90
        
        Subtotal                  RM 49.40
        Tax (6%)                  RM 2.96
        Total                     RM 52.36
        
        Thank you for your purchase!
        """
        
        # Parse receipt text
        receipt_parser = ReceiptParser()
        parsed_data = receipt_parser.parse_receipt_text(mock_text)
        
        if parsed_data['valid']:
            return {
                'success': True,
                'extracted_text': mock_text,
                'confidence': 0.92,
                'extracted_data': parsed_data,
                'image_type': 'RECEIPT'
            }
        
        return {
            'success': False,
            'error': 'Could not extract valid receipt data',
            'extracted_text': mock_text,
            'confidence': 0.4
        }
    
    def _process_generic_image(self, image_url: str) -> Dict:
        """Process generic image"""
        # Mock OCR result for generic image
        mock_text = "This is a generic image with some text content."
        
        return {
            'success': True,
            'extracted_text': mock_text,
            'confidence': 0.85,
            'extracted_data': {'text': mock_text},
            'image_type': 'OTHER'
        }
    
    def extract_ic_from_text(self, text: str) -> Optional[Dict]:
        """Extract IC number from text and parse it"""
        # Look for IC number patterns
        ic_patterns = [
            r'(\d{6}-\d{2}-\d{4})',  # Standard format with dashes
            r'(\d{12})',  # 12 digits without dashes
        ]
        
        for pattern in ic_patterns:
            match = re.search(pattern, text)
            if match:
                ic_number = match.group(1).replace('-', '')
                ic_parser = MalaysianICParser()
                return ic_parser.parse_ic_number(ic_number)
        
        return None
    
    def extract_receipt_data_from_text(self, text: str) -> Optional[Dict]:
        """Extract receipt data from text"""
        receipt_parser = ReceiptParser()
        return receipt_parser.parse_receipt_text(text)
