import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from django.conf import settings
from django.utils import timezone
from .models import Customer, Tenant
from .ocr_extractor import run_ocr
from .parsers import (
    extract_store_name, extract_store_location, extract_products, 
    extract_amount_spent, extract_nric_info, decide_validity
)


class OCRService:
    """Service for processing OCR and extracting customer information"""
    
    def __init__(self):
        self.temp_dir = Path(settings.MEDIA_ROOT) / 'temp_ocr'
        self.temp_dir.mkdir(exist_ok=True)
    
    def clean_phone_number(self, phone: str) -> str:
        """Clean and normalize phone number"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Handle Malaysian phone numbers
        if cleaned.startswith('+60'):
            cleaned = cleaned[3:]
        elif cleaned.startswith('60'):
            cleaned = cleaned[2:]
        
        # Add country code if missing
        if not cleaned.startswith('+'):
            cleaned = '+60' + cleaned
        
        return cleaned
    
    def process_image(self, image_path: str, tenant: Tenant, phone_number: str) -> Dict[str, Any]:
        """
        Process an image with OCR and extract customer information
        
        Args:
            image_path: Path to the image file
            tenant: Tenant instance
            phone_number: Customer's phone number
            
        Returns:
            Dict with extracted information and processing status
        """
        try:
            # Run OCR on the image
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                return {
                    'success': False,
                    'error': 'Image file not found',
                    'extracted_data': {}
                }
            
            # Run OCR
            ocr_lines = run_ocr(image_path_obj)
            
            if not ocr_lines:
                return {
                    'success': False,
                    'error': 'No text extracted from image',
                    'extracted_data': {}
                }
            
            # Extract information using parsers
            extracted_data = self._extract_customer_data(ocr_lines)
            
            # Clean phone number
            cleaned_phone = self.clean_phone_number(phone_number)
            
            # Find or create customer
            customer = self._find_or_create_customer(tenant, cleaned_phone, extracted_data)
            
            # Update customer with extracted data
            self._update_customer_data(customer, extracted_data, ocr_lines)
            
            return {
                'success': True,
                'customer': customer,
                'extracted_data': extracted_data,
                'ocr_lines': ocr_lines
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'extracted_data': {}
            }
    
    def _extract_customer_data(self, ocr_lines: List[str]) -> Dict[str, Any]:
        """Extract customer data from OCR lines"""
        data = {}
        
        # Extract store information
        data['store_name'] = extract_store_name(ocr_lines)
        data['store_location'] = extract_store_location(ocr_lines, None, None)
        
        # Extract products
        products = extract_products(ocr_lines, max_items=5)
        data['products'] = [{'name': name, 'quantity': qty} for name, qty in products]
        
        # Extract amount spent
        amount_str = extract_amount_spent(ocr_lines)
        if amount_str:
            # Convert RM123.45 to 123.45
            amount_clean = re.sub(r'[^\d.]', '', amount_str)
            try:
                data['total_spent'] = float(amount_clean)
            except ValueError:
                data['total_spent'] = None
        else:
            data['total_spent'] = None
        
        # Extract NRIC information
        nric_info = extract_nric_info(ocr_lines)
        data.update(nric_info)
        
        # Determine validity
        validity, reason = decide_validity(amount_str, products, False)
        data['validity'] = validity
        data['validity_reason'] = reason
        
        return data
    
    def _find_or_create_customer(self, tenant: Tenant, phone_number: str, extracted_data: Dict[str, Any]) -> Customer:
        """Find existing customer or create new one"""
        try:
            # Try to find customer by phone number
            customer = Customer.objects.get(tenant=tenant, phone_number=phone_number)
        except Customer.DoesNotExist:
            # Create new customer
            name = extracted_data.get('name', 'Unknown Customer')
            customer = Customer.objects.create(
                tenant=tenant,
                name=name,
                phone_number=phone_number
            )
        
        return customer
    
    def _update_customer_data(self, customer: Customer, extracted_data: Dict[str, Any], ocr_lines: List[str]):
        """Update customer with extracted data"""
        updated = False
        
        # Update name if we have a better one
        if extracted_data.get('name') and extracted_data['name'] != 'Unknown Customer':
            if not customer.name or customer.name == 'Unknown Customer':
                customer.name = extracted_data['name']
                updated = True
        
        # Update NRIC
        if extracted_data.get('nric') and not customer.nric:
            customer.nric = extracted_data['nric']
            updated = True
        
        # Update address
        if extracted_data.get('address') and not customer.address:
            customer.address = extracted_data['address']
            updated = True
        
        # Update store information
        if extracted_data.get('store_name'):
            customer.store_name = extracted_data['store_name']
            updated = True
        
        if extracted_data.get('store_location'):
            customer.store_location = extracted_data['store_location']
            updated = True
        
        # Update spending information
        if extracted_data.get('total_spent'):
            customer.total_spent = extracted_data['total_spent']
            customer.last_receipt_date = timezone.now()
            updated = True
        
        # Update products purchased
        if extracted_data.get('products'):
            # Merge with existing products
            existing_products = customer.products_purchased or []
            new_products = extracted_data['products']
            
            # Simple merge - in production, you might want more sophisticated logic
            all_products = existing_products + new_products
            customer.products_purchased = all_products[-10:]  # Keep last 10 purchases
            updated = True
        
        # Update OCR confidence (simplified - in production, calculate actual confidence)
        customer.ocr_confidence = 0.8 if extracted_data.get('validity') == 'VALID' else 0.5
        updated = True
        
        if updated:
            customer.save()
    
    def process_whatsapp_image(self, image_url: str, tenant: Tenant, phone_number: str) -> Dict[str, Any]:
        """
        Process image from WhatsApp webhook
        
        Args:
            image_url: URL or path to the image
            tenant: Tenant instance
            phone_number: Customer's phone number
            
        Returns:
            Dict with processing results
        """
        try:
            # For now, assume image_url is a local path
            # In production, you might need to download from URL first
            return self.process_image(image_url, tenant, phone_number)
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process WhatsApp image: {str(e)}',
                'extracted_data': {}
            }