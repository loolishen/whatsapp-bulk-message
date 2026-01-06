from __future__ import annotations

import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test Google Cloud Vision OCR + hint-based parsing using either a local file path or a public image URL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--image-url",
            required=True,
            help="Either a local file path (e.g. img/receipt.jpg) or a publicly accessible image URL (jpg/png).",
        )
        parser.add_argument("--fallback-city", default=None, help="Fallback city (optional).")
        parser.add_argument("--fallback-state", default=None, help="Fallback state (optional).")

    def handle(self, *args, **opts):
        from messaging.receipt_ocr_service import ReceiptOCRService

        image_url: str = opts["image_url"]
        fallback_city = opts.get("fallback_city") or None
        fallback_state = opts.get("fallback_state") or None

        svc = ReceiptOCRService()
        wrapper = getattr(svc, "ocr_service", None)

        self.stdout.write(self.style.SUCCESS("=== OCR CONFIG ==="))
        self.stdout.write(f"ocr_available={getattr(svc, 'ocr_available', None)}")
        self.stdout.write(f"wrapper_class={wrapper.__class__.__name__ if wrapper else None}")
        self.stdout.write(f"vision_available={getattr(wrapper, 'available', None) if wrapper else None}")
        self.stdout.write(f"parsers_loaded={getattr(wrapper, 'parsers_loaded', None) if wrapper else None}")
        self.stdout.write(f"store_hints={len(getattr(wrapper, 'store_hints', []) or []) if wrapper else None}")
        self.stdout.write(f"product_hints={len(getattr(wrapper, 'product_hints', []) or []) if wrapper else None}")
        self.stdout.write(f"store_loc_map={len(getattr(wrapper, 'store_loc_map', {}) or {}) if wrapper else None}")

        self.stdout.write(self.style.SUCCESS("\n=== RUN OCR ==="))
        result = svc.process_receipt_image(
            image_url=image_url,
            fallback_city=fallback_city,
            fallback_state=fallback_state,
        )

        # Pretty print
        self.stdout.write(self.style.SUCCESS("\n=== OCR RESULT (JSON) ==="))
        self.stdout.write(json.dumps(result, indent=2, ensure_ascii=False, default=str))


