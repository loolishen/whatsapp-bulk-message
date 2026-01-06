"""
Google Cloud Vision OCR Wrapper for Django
Uses Google Cloud Vision API + custom parsers with hints for receipt processing
"""
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class DeepSeekOCRWrapper:
    """Wrapper for Google Cloud Vision API OCR with custom parsers (filename kept for backwards compatibility)"""
    
    def __init__(self):
        self.available = True
        try:
            from google.cloud import vision
            self.vision_client = vision.ImageAnnotatorClient()
            logger.info("Google Cloud Vision API initialized successfully")
        except Exception as e:
            logger.warning(f"Google Cloud Vision API not available: {e}")
            self.available = False
        
        # Load OCR parsers with hints
        self.parsers_loaded = False
        try:
            # Add ocr/app to Python path to import parsers
            ocr_app_path = Path(__file__).parent.parent / 'ocr' / 'app'
            if ocr_app_path.exists() and str(ocr_app_path) not in sys.path:
                sys.path.insert(0, str(ocr_app_path))
            
            from parsers import (
                extract_store_name,
                extract_store_location,
                extract_amount_spent,
                extract_products,
                PREFERRED_STORE_HINTS,
                PREFERRED_PRODUCT_HINTS,
                STORE_LOC_MAP,
            )
            self.extract_store_name = extract_store_name
            self.extract_store_location = extract_store_location
            self.extract_amount_spent = extract_amount_spent
            self.extract_products = extract_products
            self.store_hints = PREFERRED_STORE_HINTS or []
            self.product_hints = PREFERRED_PRODUCT_HINTS or []
            self.store_loc_map = STORE_LOC_MAP or {}
            self.parsers_loaded = True
            logger.info(f"OCR parsers loaded: {len(self.store_hints)} store hints, {len(self.product_hints)} product hints")
        except Exception as e:
            logger.warning(f"Could not load OCR parsers with hints: {e}")
    
    def process_receipt_image(
        self, 
        image_path: Path,
        fallback_city: Optional[str] = None,
        fallback_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process receipt image using Google Cloud Vision API + custom parsers
        
        Returns structured data:
        {
            'success': bool,
            'store_name': str,
            'store_location': str,
            'amount_spent': str,
            'products': [(name, qty), ...],
            'validity': 'VALID' | 'INVALID',
            'reason': str,
            'raw_text': str
        }
        """
        if not self.available:
            return self._error_response("Google Cloud Vision API not configured")
        
        try:
            # Extract text using Google Cloud Vision
            raw_text, text_lines = self._extract_text_with_vision(image_path)
            
            if not raw_text:
                return self._error_response("No text extracted from image")
            
            # Parse receipt using custom parsers with hints
            parsed_data = self._parse_receipt_with_hints(text_lines, raw_text)
            
            # Determine validity
            validity, reason = self._determine_validity(parsed_data)
            
            # Apply fallback location if needed
            store_location = parsed_data.get('store_location', 'Unknown')
            if store_location == 'Unknown' and fallback_city:
                store_location = f"{fallback_city}, {fallback_state}" if fallback_state else fallback_city
            
            result = {
                'success': True,
                'store_name': parsed_data.get('store_name') or 'Unknown',
                'store_location': store_location,
                'amount_spent': parsed_data.get('amount_spent') or '0.00',
                'products': parsed_data.get('items', []),
                'validity': validity,
                'reason': reason,
                'raw_text': raw_text
            }
            
            logger.info(f"GCP Vision OCR processed: {result['store_name']}, {result['amount_spent']}, {len(result['products'])} items")
            return result
            
        except Exception as e:
            logger.error(f"GCP Vision OCR failed: {e}", exc_info=True)
            return self._error_response(f"OCR processing error: {str(e)}")
    
    def _extract_text_with_vision(self, image_path: Path) -> Tuple[str, List[str]]:
        """
        Extract text from receipt using Google Cloud Vision API
        Returns: (raw_text, text_lines)
        """
        try:
            from google.cloud import vision
            
            # Read image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform text detection
            response = self.vision_client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Get full text
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Get text lines (preserve line structure)
            text_lines = []
            if full_text:
                text_lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            logger.info(f"Vision API extracted {len(text_lines)} lines of text")
            return full_text, text_lines
            
        except Exception as e:
            logger.error(f"Google Cloud Vision text extraction failed: {e}", exc_info=True)
            return "", []
    
    def _parse_receipt_with_hints(self, text_lines: List[str], raw_text: str) -> Dict[str, Any]:
        """
        Parse receipt using custom parsers with store/product hints
        """
        result = {
            'store_name': None,
            'store_location': None,
            'amount_spent': None,
            'items': []
        }
        
        if not self.parsers_loaded:
            logger.warning("Parsers not loaded, using basic extraction")
            return self._parse_receipt_basic(text_lines)
        
        try:
            # Extract store name using hints
            store_name = self.extract_store_name(text_lines, preferred_stores=self.store_hints)
            result['store_name'] = store_name
            
            # Extract location (hinted store_loc_map isn't used by parsers.py; it uses fallback city/state)
            # Keep store_loc_map loaded anyway because it may be used by other helpers.
            result['store_location'] = self.extract_store_location(text_lines, None, None)
            
            # Extract amount
            amount = self.extract_amount_spent(text_lines)
            result['amount_spent'] = amount
            
            # Extract products using hints
            products = self.extract_products(
                text_lines,
                preferred_items=self.product_hints
            )
            result['items'] = products
            
            logger.info(
                "Parsed with hints: store=%s, location=%s, amount=%s, items=%s",
                store_name,
                result.get("store_location"),
                amount,
                len(products),
            )
            return result
            
        except Exception as e:
            logger.error(f"Hint-based parsing failed, falling back to basic: {e}", exc_info=True)
            return self._parse_receipt_basic(text_lines)
    
    def _parse_receipt_basic(self, text_lines: List[str]) -> Dict[str, Any]:
        """
        Basic fallback parser without hints
        """
        import re
        
        result = {
            'store_name': None,
            'store_location': None,
            'amount_spent': None,
            'items': []
        }
        
        # Try to find store name (usually in first few lines, all caps)
        for line in text_lines[:5]:
            if len(line) > 3 and line.isupper():
                result['store_name'] = line
                break
        
        # Try to find total amount
        amount_pattern = r'(?:TOTAL|AMOUNT|GRAND\s*TOTAL)[\s:]*(?:RM|MYR)?\s*(\d+\.?\d*)'
        for line in reversed(text_lines):
            match = re.search(amount_pattern, line, re.IGNORECASE)
            if match:
                result['amount_spent'] = f"RM{match.group(1)}"
                break
        
        # Try to extract items (lines with prices)
        item_pattern = r'^(.+?)\s+(?:RM|MYR)?\s*(\d+\.\d{2})$'
        for line in text_lines:
            match = re.search(item_pattern, line)
            if match:
                item_name = match.group(1).strip()
                if len(item_name) > 2:
                    result['items'].append((item_name, 1))
        
        return result
    
    def _determine_validity(self, parsed_data: Dict[str, Any]) -> tuple[str, str]:
        """Determine if receipt is valid based on parsed data"""
        
        if not parsed_data:
            return 'INVALID', 'Failed to parse receipt data'
        
        # Check for required fields
        amount = parsed_data.get('amount_spent')
        store = parsed_data.get('store_name')
        items = parsed_data.get('items', [])
        
        if not amount or amount == 'null' or amount == '0.00':
            return 'INVALID', 'No purchase amount detected'
        
        if not store or store == 'null':
            return 'INVALID', 'Store name not detected'
        
        if not items or len(items) == 0:
            return 'INVALID', 'No items detected on receipt'
        
        # Check minimum amount (optional - adjust as needed)
        try:
            amount_num = float(amount.replace('RM', '').replace(',', '').strip())
            if amount_num < 1.0:
                return 'INVALID', f'Amount too low: {amount}'
        except (ValueError, AttributeError):
            return 'INVALID', f'Invalid amount format: {amount}'
        
        return 'VALID', 'Receipt validated successfully'
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Return standardized error response"""
        return {
            'success': False,
            'store_name': None,
            'store_location': None,
            'amount_spent': None,
            'products': [],
            'validity': 'INVALID',
            'reason': error_msg,
            'raw_text': ''
        }

