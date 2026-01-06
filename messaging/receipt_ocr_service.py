"""
Receipt OCR Service for Contest Flow
Uses DeepSeek Vision API for receipt processing
"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal
import tempfile
import requests
from .deepseek_ocr_wrapper import DeepSeekOCRWrapper

logger = logging.getLogger(__name__)

class ReceiptOCRService:
    """Service to process receipt images using DeepSeek OCR"""
    
    def __init__(self):
        self.ocr_service = DeepSeekOCRWrapper()
        self.ocr_available = self.ocr_service.available
    
    def process_receipt_image(
        self, 
        image_url: str,
        media_meta: Optional[Dict[str, Any]] = None,
        fallback_city: Optional[str] = None,
        fallback_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a receipt image and extract information
        
        Args:
            image_url: URL or path to the receipt image
            fallback_city: Optional city for location fallback
            fallback_state: Optional state for location fallback
        
        Returns:
            Dictionary with extracted receipt data:
            {
                'success': bool,
                'amount_spent': str (e.g., 'RM149.00'),
                'store_name': str,
                'store_location': str,
                'products': List[Tuple[str, int]],  # [(name, qty), ...]
                'validity': str ('VALID' or 'INVALID'),
                'reason': str (reason if invalid),
                'formatted_message': str (for WhatsApp reply),
                'error': str (if success=False)
            }
        """
        if not self.ocr_available:
            return {
                'success': False,
                'error': 'DeepSeek OCR not configured',
                'formatted_message': '⚠️ Receipt processing temporarily unavailable. Please contact support.'
            }
        
        try:
            # Download image to temp file
            try:
                image_path = self._download_image(image_url, media_meta=media_meta or {})
            except ValueError as ve:
                msg = str(ve) or "Invalid receipt image"
                logger.error(f"Receipt download/validation failed: {msg}")
                return {
                    'success': False,
                    'error': msg,
                    'formatted_message': f"❌ {msg}\n\nPlease resend a normal receipt photo (not 'view once')."
                }

            if not image_path:
                return {
                    'success': False,
                    'error': 'Failed to download image',
                    'formatted_message': '❌ Could not download receipt image. Please try again.'
                }
            
            # Process with DeepSeek OCR
            result = self.ocr_service.process_receipt_image(
                image_path, 
                fallback_city, 
                fallback_state
            )
            
            # Format WhatsApp message
            result['formatted_message'] = self._format_receipt_message(result)
            
            # Cleanup temp file
            try:
                image_path.unlink()
            except Exception:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing receipt: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                # Don't include formatted_message on error — let the calling service decide how to handle it
            }
    
    def _download_image(self, image_url: str, media_meta: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """Download image from URL to temporary file. If `.enc` and mediaKey is present, decrypt first."""
        try:
            # If it's already a local path, return it
            if Path(image_url).exists():
                return Path(image_url)
            
            # Download from URL
            logger.info(f"Downloading receipt image: {image_url[:120]}")
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; ReceiptOCRService/1.0)",
                "Accept": "*/*",
            }
            response = requests.get(image_url, timeout=30, headers=headers)
            response.raise_for_status()

            content_type = (response.headers.get('content-type', '') or '').lower()
            content = response.content or b""
            logger.info(f"Receipt download ok: bytes={len(content)} content-type={content_type}")

            # Validate bytes look like an image (WhatsApp often provides encrypted .enc media URLs)
            def _is_jpeg(b: bytes) -> bool:
                return len(b) >= 3 and b[0:3] == b"\xFF\xD8\xFF"
            def _is_png(b: bytes) -> bool:
                return len(b) >= 8 and b[0:8] == b"\x89PNG\r\n\x1a\n"
            def _is_webp(b: bytes) -> bool:
                return len(b) >= 12 and b[0:4] == b"RIFF" and b[8:12] == b"WEBP"

            looks_like_image = _is_jpeg(content) or _is_png(content) or _is_webp(content)
            is_encrypted_hint = (".enc" in image_url) or ("mmg.whatsapp.net" in image_url and "/t62." in image_url)
            if not looks_like_image and is_encrypted_hint:
                # Attempt decryption if we have mediaKey metadata (Baileys-style fields)
                meta = media_meta or {}
                media_key_b64 = meta.get("mediaKey")
                expected_sha_b64 = meta.get("fileSha256")
                mimetype_meta = (meta.get("mimetype") or "").lower()
                if media_key_b64:
                    try:
                        from .whatsapp_media_crypto import decrypt_whatsapp_media
                        media_info = "WhatsApp Image Keys"
                        # (We only handle receipts as images for now)
                        plain = decrypt_whatsapp_media(
                            enc_bytes=content,
                            media_key_b64=str(media_key_b64),
                            media_info=media_info,
                            expected_file_sha256_b64=str(expected_sha_b64) if expected_sha_b64 else None,
                        )
                        content = plain
                        content_type = mimetype_meta or "image/jpeg"
                        looks_like_image = _is_jpeg(content) or _is_png(content) or _is_webp(content)
                        logger.info(f"Receipt media decrypted: bytes={len(content)} mimetype={content_type}")
                    except Exception as e:
                        raise ValueError(
                            "We received an encrypted WhatsApp media link (.enc) and could not decrypt it for OCR. "
                            f"Decrypt error: {str(e)[:120]}"
                        )

            if not looks_like_image:
                # Provide a very explicit message so users know what to do
                if is_encrypted_hint:
                    raise ValueError(
                        "We received an encrypted WhatsApp media link (.enc), so OCR can't read the image. "
                        "Please resend the receipt as a standard photo (not encrypted/view-once)."
                    )
                raise ValueError("The downloaded file is not a valid image. Please resend a clear receipt photo.")
            
            # Save to temp file
            temp_dir = Path(tempfile.gettempdir()) / 'receipt_ocr'
            temp_dir.mkdir(exist_ok=True)
            
            # Determine extension from content-type or URL
            ext = '.jpg'
            if 'png' in content_type:
                ext = '.png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif _is_webp(content):
                ext = '.webp'
            
            temp_file = temp_dir / f'receipt_{hash(image_url)}_{Path(image_url).name}'
            if not temp_file.suffix:
                temp_file = temp_file.with_suffix(ext)
            
            with open(temp_file, 'wb') as f:
                f.write(content)
            
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            return None
    
    
    def _format_receipt_message(self, result: Dict[str, Any]) -> str:
        """Format the receipt data into a WhatsApp message"""
        if not result.get('success'):
            return result.get('formatted_message', '❌ Error processing receipt')
        
        validity = result.get('validity', 'INVALID')
        
        if validity == 'VALID':
            # Success message
            msg = "🎊 Perfect! I can see your receipt clearly.\n\n"
            msg += "📋 Receipt Details:\n"
            
            # Store info
            if result.get('store_name'):
                msg += f"🏪 Store: {result['store_name']}\n"
            if result.get('store_location'):
                msg += f"📍 Location: {result['store_location']}\n"
            
            # Amount
            if result.get('amount_spent'):
                msg += f"💰 Amount: {result['amount_spent']}\n"
            
            # Products
            products = result.get('products', [])
            if products:
                msg += f"\n🛍️ Products:\n"
                for idx, (name, qty) in enumerate(products[:3], 1):
                    msg += f"  {idx}. {name}"
                    if qty > 1:
                        msg += f" (x{qty})"
                    msg += "\n"
            
            msg += "\n✅ All details verified!"
            
        else:
            # Invalid message
            reason = result.get('reason', 'Unknown reason')
            msg = f"❌ Receipt validation failed\n\n"
            msg += f"Reason: {reason}\n\n"
            
            if result.get('store_name'):
                msg += f"Store detected: {result['store_name']}\n"
            if result.get('amount_spent'):
                msg += f"Amount detected: {result['amount_spent']}\n"
            
            msg += "\nPlease upload a clearer image or contact support."
        
        return msg
    
    def save_to_contest_entry(self, entry, result: Dict[str, Any]):
        """Save OCR results to a ContestEntry object"""
        try:
            if not result.get('success'):
                return
            
            # Update entry with extracted data
            if result.get('store_name'):
                entry.store_name = result['store_name']
            
            if result.get('store_location'):
                entry.store_location = result['store_location']
            
            if result.get('amount_spent'):
                # Extract numeric value
                amount_str = result['amount_spent'].replace('RM', '').replace(',', '').strip()
                try:
                    entry.receipt_amount = Decimal(amount_str)
                except Exception:
                    pass
            
            # Save products as JSON
            products = result.get('products', [])
            if products:
                entry.products_purchased = [
                    {'name': name, 'quantity': qty}
                    for name, qty in products
                ]
            
            # Update status based on validity
            if result.get('validity') == 'VALID':
                entry.is_verified = True
                entry.status = 'verified'
            else:
                entry.status = 'rejected'
                entry.rejection_reason = result.get('reason', 'Receipt validation failed')
            
            entry.save()
            logger.info(f"Updated contest entry {entry.entry_id} with OCR results")
            
        except Exception as e:
            logger.error(f"Failed to save OCR results to entry: {e}", exc_info=True)

