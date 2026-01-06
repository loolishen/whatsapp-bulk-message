import uuid

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Simulate bad/partial receipt submissions and manual-review completion notifications."

    def add_arguments(self, parser):
        parser.add_argument("--phone", required=True, help="Customer phone number (digits, e.g. 60123456789)")
        parser.add_argument("--contest-name", default=None, help="Contest name (optional; defaults to first active contest)")
        parser.add_argument(
            "--image-url",
            default="https://example.com/does-not-exist.jpg",
            help="Receipt image URL. Use a broken URL to simulate download/OCR failure (manual review path).",
        )
        parser.add_argument(
            "--review-outcome",
            choices=["verified", "rejected", "none"],
            default="none",
            help="After creating an under_review entry, optionally mark it as verified/rejected to test follow-up notification.",
        )
        parser.add_argument("--rejection-reason", default="Receipt image unclear/partial", help="Used if --review-outcome=rejected")

    def handle(self, *args, **opts):
        from messaging.models import (
            Tenant,
            Customer,
            WhatsAppConnection,
            Conversation,
            CoreMessage,
            MessageAttachment,
            Contest,
            ContestFlowState,
            ContestEntry,
        )
        from messaging.step_by_step_contest_service import StepByStepContestService

        tenant = Tenant.objects.first()
        if not tenant:
            raise SystemExit("No Tenant found. Create a tenant first.")

        phone = "".join([c for c in str(opts["phone"]) if c.isdigit()])
        if not phone.startswith("60"):
            phone = "60" + phone

        customer, _ = Customer.objects.get_or_create(
            tenant=tenant,
            phone_number=phone,
            defaults={"name": f"Test Customer {phone}", "address": ""},
        )

        conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
        if not conn:
            raise SystemExit("No WhatsAppConnection found for tenant. Create one in admin first.")

        contest_qs = Contest.objects.filter(tenant=tenant, is_active=True).order_by("-created_at")
        if opts["contest_name"]:
            contest_qs = contest_qs.filter(name=opts["contest_name"])
        contest = contest_qs.first()
        if not contest:
            raise SystemExit("No active contest found. Create/activate a contest first.")

        conversation = (
            Conversation.objects.filter(tenant=tenant, customer=customer, whatsapp_connection=conn)
            .order_by("-created_at")
            .first()
        )
        if not conversation:
            conversation = Conversation.objects.create(tenant=tenant, customer=customer, whatsapp_connection=conn)

        # Put user into awaiting_receipt step
        flow, _ = ContestFlowState.objects.update_or_create(
            customer=customer,
            contest=contest,
            defaults={"current_step": "awaiting_receipt"},
        )

        # Create an inbound message + image attachment (this is what the receipt step reads)
        msg = CoreMessage.objects.create(
            tenant=tenant,
            conversation=conversation,
            direction="inbound",
            status="delivered",
            text_body="(receipt image)",
            provider_msg_id=f"test-{uuid.uuid4().hex[:12]}",
            created_at=timezone.now(),
        )
        MessageAttachment.objects.create(
            tenant=tenant,
            message=msg,
            kind="image",
            storage_path=opts["image_url"],
            mime_type="image/jpeg",
            bytes_size=1234,
            created_at=timezone.now(),
        )

        self.stdout.write(self.style.SUCCESS("Created inbound image attachment for receipt step"))

        # Pass the image URL as media_url so the receipt step can run OCR deterministically.
        svc = StepByStepContestService()
        result = svc.process_message_for_contests(
            customer,
            "RECEIPT",
            tenant,
            conversation,
            media_url=opts["image_url"],
            media_type="image",
        )
        self.stdout.write(self.style.SUCCESS(f"Contest flow result: {result}"))

        entry = ContestEntry.objects.filter(tenant=tenant, contest=contest, customer=customer).first()
        if entry:
            self.stdout.write(
                self.style.SUCCESS(
                    f"ContestEntry: status={entry.status} is_verified={entry.is_verified} receipt_image_url={entry.receipt_image_url}"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("No ContestEntry created. Check logs for errors."))
            return

        outcome = opts["review_outcome"]
        if outcome != "none" and entry.status == "under_review":
            if outcome == "verified":
                entry.status = "verified"
                entry.is_verified = True
                entry.verified_at = timezone.now()
                entry.verified_by = "manual_test"
                entry.save()
                self.stdout.write(self.style.SUCCESS("Set entry to VERIFIED (should trigger follow-up WhatsApp notification)"))
            elif outcome == "rejected":
                entry.status = "rejected"
                entry.is_verified = False
                entry.rejection_reason = opts["rejection_reason"]
                entry.verified_at = timezone.now()
                entry.verified_by = "manual_test"
                entry.save()
                self.stdout.write(self.style.SUCCESS("Set entry to REJECTED (should trigger follow-up WhatsApp notification)"))
        elif outcome != "none":
            self.stdout.write(self.style.WARNING(f"Entry status is {entry.status}, not under_review; not applying review outcome."))



