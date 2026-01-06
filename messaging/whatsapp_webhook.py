import json
import os
import sys
import re
import requests
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

_DIGITS_ONLY = re.compile(r"\D+")

def _p(*args):
    try:
        print(*args, file=sys.stderr)
    except Exception:
        pass

def _norm_number(n):
    if not n:
        return None
    s = str(n).strip()
    s = _DIGITS_ONLY.sub("", s)
    return s or None

def _safe_json(body_bytes):
    try:
        raw = body_bytes.decode("utf-8", errors="ignore") if body_bytes else ""
        return raw, (json.loads(raw) if raw.strip() else {})
    except Exception:
        return "", {}

def _echo_enabled() -> bool:
    """
    Legacy echo test switch.
    Keep disabled in production; the real bot replies are sent from services
    via `WhatsAppAPIService` using `WABOT_API_TOKEN`.
    """
    return os.getenv("WABOT_ENABLE_AUTOREPLY", "false").lower() == "true"

def _extract_from_and_text(obj):
    """
    Try multiple common shapes. We keep it flexible because wabot can wrap data.
    Handles WABot structure: key.remoteJid and message.conversation
    """
    if not isinstance(obj, dict):
        return None, ""

    # Common direct keys
    sender = obj.get("from") or obj.get("number") or obj.get("phone")
    
    # WABot structure: key.remoteJid contains sender (format: "60123456789@s.whatsapp.net")
    # BUT:
    # - if remoteJidAlt exists, use it (it has the real phone number when addressingMode=lid)
    # - for group messages (remoteJid ends with @g.us), use participantAlt (real sender) when present
    if not sender:
        key_obj = obj.get("key", {})
        if isinstance(key_obj, dict):
            remote_jid_raw = key_obj.get("remoteJid", "") or ""

            # Group message: the true sender is in participantAlt/participant
            if remote_jid_raw.endswith("@g.us"):
                remote_jid = key_obj.get("participantAlt") or key_obj.get("participant") or ""
            else:
                # Prefer remoteJidAlt (real phone number) over remoteJid (internal WhatsApp ID)
                remote_jid = key_obj.get("remoteJidAlt") or remote_jid_raw
            if remote_jid:
                # Remove @s.whatsapp.net suffix
                sender = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid

    # Extract text - handle both string and object formats
    msg_obj = obj.get("message")
    text = ""
    
    if isinstance(msg_obj, dict):
        # WABot structure: message is an object with conversation or extendedTextMessage
        # Try conversation (simple text)
        text = msg_obj.get("conversation", "")
        # Try extendedTextMessage.text (longer messages)
        if not text:
            ext_text = msg_obj.get("extendedTextMessage", {})
            if isinstance(ext_text, dict):
                text = ext_text.get("text", "")
        # Fallback to body or text
        if not text:
            text = msg_obj.get("body") or msg_obj.get("text") or ""
    elif isinstance(msg_obj, str):
        # Direct string message
        text = msg_obj
    else:
        # Fallback to text field
        text = obj.get("text") or ""

    return _norm_number(sender), (str(text) if text is not None else "")

def _extract_media_info(obj):
    """
    Extract media (image, video, document) information from WABot payload.
    Returns: (media_type, media_url, caption, media_meta) or (None, None, None, None)
    """
    if not isinstance(obj, dict):
        return None, None, None, None
    
    msg_obj = obj.get("message")
    if not isinstance(msg_obj, dict):
        return None, None, None, None
    
    # Check for imageMessage
    if "imageMessage" in msg_obj:
        img = msg_obj["imageMessage"]
        meta = img if isinstance(img, dict) else {}
        return "image", meta.get("url"), meta.get("caption", ""), meta
    
    # Check for videoMessage
    if "videoMessage" in msg_obj:
        vid = msg_obj["videoMessage"]
        meta = vid if isinstance(vid, dict) else {}
        return "video", meta.get("url"), meta.get("caption", ""), meta
    
    # Check for documentMessage
    if "documentMessage" in msg_obj:
        doc = msg_obj["documentMessage"]
        meta = doc if isinstance(doc, dict) else {}
        return "document", meta.get("url"), meta.get("caption", ""), meta
    
    return None, None, None, None

def _maybe_log_media_payload(first_msg: dict):
    """
    Debug helper: log just the media payload fields we need to handle encrypted WhatsApp media.
    Enable with env var: WABOT_LOG_MEDIA_PAYLOAD=true
    """
    try:
        if os.getenv("WABOT_LOG_MEDIA_PAYLOAD", "false").lower() != "true":
            return
        if not isinstance(first_msg, dict):
            return
        msg_obj = first_msg.get("message")
        if not isinstance(msg_obj, dict):
                return
            
        def _short(v, n=24):
            s = "" if v is None else str(v)
            return s if len(s) <= n else (s[:n] + "...(truncated)")

        def _redact_url(u: str):
            if not u:
                return ""
            # Remove query params (often contains expiring tokens)
            return u.split("?", 1)[0]

        if "imageMessage" in msg_obj and isinstance(msg_obj["imageMessage"], dict):
            img = msg_obj["imageMessage"]
            _p("MEDIA_PAYLOAD imageMessage:", {
                "url": _redact_url(img.get("url")),
                "mimetype": img.get("mimetype"),
                "directPath": img.get("directPath"),
                "fileLength": img.get("fileLength"),
                "fileSha256": _short(img.get("fileSha256")),
                "fileEncSha256": _short(img.get("fileEncSha256")),
                "mediaKey": _short(img.get("mediaKey")),
                "caption": _short(img.get("caption"), 80),
            })
            return

        if "documentMessage" in msg_obj and isinstance(msg_obj["documentMessage"], dict):
            doc = msg_obj["documentMessage"]
            _p("MEDIA_PAYLOAD documentMessage:", {
                "url": _redact_url(doc.get("url")),
                "mimetype": doc.get("mimetype"),
                "directPath": doc.get("directPath"),
                "fileLength": doc.get("fileLength"),
                "fileSha256": _short(doc.get("fileSha256")),
                "fileEncSha256": _short(doc.get("fileEncSha256")),
                "mediaKey": _short(doc.get("mediaKey")),
                "fileName": _short(doc.get("fileName"), 80),
            })
            return
    except Exception:
        return

def _extract_message_meta(event_data):
    """
    Extract best-effort metadata (message id, fromMe, status) from WABot/Baileys payloads.
    """
    msg = None
    if isinstance(event_data, list) and event_data:
        msg = event_data[0] if isinstance(event_data[0], dict) else None
    elif isinstance(event_data, dict):
        msg = event_data

    if not isinstance(msg, dict):
        return {"msg_id": None, "from_me": None, "status": None, "remote_jid": None, "timestamp": None}

    key_obj = msg.get("key", {}) if isinstance(msg.get("key", {}), dict) else {}
    return {
        "msg_id": key_obj.get("id"),
        "from_me": key_obj.get("fromMe"),
        "remote_jid": key_obj.get("remoteJid"),
        "status": msg.get("status"),
        "timestamp": msg.get("messageTimestamp"),
    }

def _dedupe_key(sender, text, meta):
    """
    Build a short-lived idempotency key to prevent repeated WABot retries/events
    from re-processing the same inbound message.
    """
    if meta.get("msg_id"):
        return f"wabot:seen:msgid:{meta['msg_id']}"
    # fallback: remote+timestamp+text
    remote = meta.get("remote_jid") or sender or ""
    ts = meta.get("timestamp") or ""
    t = (text or "")[:200]
    return f"wabot:seen:fallback:{remote}:{ts}:{t}"

def _is_bot_message(msg_obj):
    """
    Check if a message is from the bot itself (outbound).
    WABot messages have key.fromMe = true for bot messages.
    """
    if not isinstance(msg_obj, dict):
        return False
    
    # Check if it's a list (messages.upsert format)
    if isinstance(msg_obj, list) and len(msg_obj) > 0:
        msg_obj = msg_obj[0]
    
    # Check key.fromMe field (WhatsApp Web protocol)
    key_obj = msg_obj.get("key", {})
    if isinstance(key_obj, dict):
        from_me = key_obj.get("fromMe", False)
        if from_me:
            return True
    
    # Also check top-level fromMe
    if msg_obj.get("fromMe", False):
        return True
    
    return False

def _process_incoming_message(
    sender: str,
    message_text: str,
    message_id: str = "",
    media_url: str = "",
    media_type: str = "",
    media_meta: dict | None = None,
):
    """
    Process incoming WhatsApp message through full contest flow.
    Uses lazy imports to avoid import-time failures.
    Supports both text and media (image/video/document) messages.
    """
    if not sender:
        return
    
    # Allow processing if either text or media is present
    if not message_text and not media_url:
        return
    
    try:
        # Lazy imports to prevent import-time failures
        from django.utils import timezone
        from .models import Customer, CoreMessage, Conversation, WhatsAppConnection, Tenant
        
        # Get tenant first (required for Customer)
        tenant = Tenant.objects.first()
        if not tenant:
            _p("ERROR: No tenant found")
            return
        
        # Get or create customer
        clean_number = sender
        if not clean_number.startswith('60'):
            clean_number = '60' + clean_number
        
        customer, created = Customer.objects.get_or_create(
            tenant=tenant,
            phone_number=clean_number,
            defaults={
                'name': f'Customer {clean_number}',
                'address': '',
            }
        )
        
        if created:
            _p("Created new customer:", customer.phone_number)
        
        # Get WhatsApp connection
        conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
        if not conn:
            _p("ERROR: No WhatsApp connection found")
            return
        
        # Get or create conversation (handle MultipleObjectsReturned)
        conversation = Conversation.objects.filter(
            tenant=tenant,
            customer=customer,
            whatsapp_connection=conn
        ).order_by('-created_at').first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                tenant=tenant,
                customer=customer,
                whatsapp_connection=conn
            )

        # If WABot forwards our outbound messages back to the webhook as "incoming",
        # we can detect it by matching the last outbound message in this conversation.
        try:
            recent_outbound = CoreMessage.objects.filter(
                conversation=conversation,
                direction="outbound",
            ).order_by("-created_at").first()
            if recent_outbound and (recent_outbound.text_body or "").strip() == (message_text or "").strip():
                # If it's very recent, treat as echo of our outbound and skip processing.
                age = timezone.now() - recent_outbound.created_at
                if age.total_seconds() < 180:
                    _p("SKIP: echoed outbound message forwarded to webhook")
                    return
        except Exception as e:
            _p("WARN: outbound-echo check failed:", str(e)[:200])
        
        # Check if this message_id already exists (database-level deduplication)
        # Only skip if the previous attempt finished successfully (sent/delivered/read).
        existing = None
        if message_id:
            existing = CoreMessage.objects.filter(provider_msg_id=message_id, tenant=tenant).order_by("-created_at").first()
            if existing and existing.status in ("sent", "delivered", "read"):
                _p(f"SKIP: message ID {message_id} already processed")
                return
            
        # Create message record as "queued" first; if the process crashes mid-way,
        # retries can still be re-processed (status won't be delivered/read).
        inbound_msg = CoreMessage.objects.create(
            tenant=tenant,
            conversation=conversation,
            direction='inbound',
            status='queued',
            text_body=message_text,
            provider_msg_id=message_id or '',
            created_at=timezone.now()
        )
        
        # DISABLED: Old PDPA service (StepByStepContestService handles PDPA now)
        # This was causing duplicate PDPA messages to be sent
        # try:
        #     from .pdpa_service import PDPAConsentService
        #     pdpa_service = PDPAConsentService()
        #     pdpa_service.handle_incoming_message(customer, message_text, tenant)
        # except Exception as e:
        #     _p("WARN: Error in PDPA service:", str(e)[:200])
        
        # Process step-by-step contest flow (lazy import)
        try:
            from .step_by_step_contest_service import StepByStepContestService
            step_contest_service = StepByStepContestService()
            contest_results = step_contest_service.process_message_for_contests(
                customer,
                message_text,
                tenant,
                conversation,
                media_url=media_url,
                media_type=media_type,
                media_meta=media_meta or {},
            )
            if contest_results.get('flows_processed', 0) > 0:
                _p("Contest processing:", contest_results)
        except Exception as e:
            _p("WARN: Error in contest service:", str(e)[:200])

        # Mark inbound message as delivered once processing completes (even if OCR failed gracefully)
        try:
            inbound_msg.status = "delivered"
            inbound_msg.save(update_fields=["status"])
        except Exception:
            pass
        
        _p("Processed message from", sender, ":", message_text[:50])
        
    except Exception as e:
        _p("ERROR processing message:", str(e)[:300])
        import traceback
        _p("Traceback:", traceback.format_exc()[:500])

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown"))
        ua = (request.META.get("HTTP_USER_AGENT", "unknown") or "")[:80]
        _p(f"WEBHOOK GET HIT path={request.path} IP={ip} UA={ua}")
        return JsonResponse({"status": "ok", "message": "webhook active"}, status=200)

    # Always respond 200 for webhook requests; log errors internally.
    # WABot will retry on non-2xx and that creates duplicate processing + duplicate messages.
    try:
        raw, top = _safe_json(request.body)

        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown"))
        ua = (request.META.get("HTTP_USER_AGENT", "unknown") or "")[:80]
        _p(f"WEBHOOK POST HIT path={request.path} IP={ip} UA={ua}")
        _p("TOP keys=", list(top.keys())[:10], "raw_len=", len(raw))

        # ---- Support BOTH formats ----
        # Format A: {"type":"message","data":{...}}
        event_type = top.get("type")
        event_data = top.get("data")

        # Format B (yours): {"instance_id": "...", "data": {"event": "...", "data": {...}}}
        instance_id = top.get("instance_id") or os.getenv("WABOT_INSTANCE_ID", "")
        if not event_type and isinstance(top.get("data"), dict):
            inner = top["data"]
            inner_event = inner.get("event")
            inner_data = inner.get("data")
            if inner_event:
                event_type = inner_event
                event_data = inner_data
            _p("INNER event=", inner_event, "INNER keys=", list(inner.keys())[:10])

        # Normalize message event names:
        # Some systems use "message", some "incoming_message", etc.
        # WABot uses "messages.upsert" for new messages
        event_str = str(event_type).lower() if event_type else ""
        is_message = event_str in {
            "message", "incoming_message", "messages", "message_received"
        } or event_str.startswith("messages.")

        # For messages.upsert, the actual message data might be nested differently
        # Log the structure to debug
        if isinstance(event_data, dict):
            _p("EVENT_DATA keys=", list(event_data.keys())[:20])
            _p("EVENT_DATA sample=", str(event_data)[:500])
        elif isinstance(event_data, list):
            _p("EVENT_DATA is list, len=", len(event_data))
            if event_data:
                _p("EVENT_DATA[0] keys=", list(event_data[0].keys())[:20] if isinstance(event_data[0], dict) else "not dict")
    
        sender, text = _extract_from_and_text(event_data if isinstance(event_data, dict) else {})
        _p("EVENT type=", event_type, "is_message=", is_message, "from=", sender, "text=", (text or "")[:200])

        meta = _extract_message_meta(event_data)
        _p("META msg_id=", meta.get("msg_id"), "fromMe=", meta.get("from_me"), "status=", meta.get("status"))

        # ---- Ignore group messages (only accept 1:1 chats) ----
        # WhatsApp group JIDs end with "@g.us". We skip these to ensure the bot
        # only interacts with individual chats.
        remote_jid = (meta.get("remote_jid") or "")
        if isinstance(remote_jid, str) and remote_jid.lower().endswith("@g.us"):
            _p("SKIP: group message ignored remote_jid=", remote_jid)
            _p("WEBHOOK 200 OK (group ignored)")
            return JsonResponse({"status": "ok"}, status=200)

        # ---- Dedupe by msg_id even for media-only messages ----
        # WABot frequently retries webhook delivery; if we return non-2xx or a worker dies mid-request,
        # we'll receive the same msg_id again. Use cache to ensure only one handler runs per msg_id.
        msg_id = meta.get("msg_id") or ""
        if is_message and msg_id:
            id_key = f"wabot:seen:msgid:{msg_id}"
            if not cache.add(id_key, True, timeout=10 * 60):
                _p("SKIP: duplicate message event (msg_id dedupe)", msg_id)
                _p("WEBHOOK 200 OK (msg_id dedupe)")
                return JsonResponse({"status": "ok"}, status=200)

        # ---- Dedupe/idempotency to stop retries from causing loops ----
        # Keep fallback key for cases without msg_id
        if is_message and sender and text:
            key = _dedupe_key(sender, text, meta)
            # cache.add returns False if key already exists
            if not cache.add(key, True, timeout=120):
                _p("SKIP: duplicate message event (dedupe)", key)
                _p("WEBHOOK 200 OK (dedupe)")
                return JsonResponse({"status": "ok"}, status=200)

        # If inner data is nested again (sometimes event_data has {"data": {...}})
        if (not sender or not text) and isinstance(event_data, dict) and isinstance(event_data.get("data"), dict):
            sender2, text2 = _extract_from_and_text(event_data["data"])
            sender = sender or sender2
            text = text or text2
            _p("NESTED extract from=", sender, "text=", text[:200])
        
        # For messages.upsert, event_data might be a list of messages
        if (not sender or not text) and isinstance(event_data, list) and len(event_data) > 0:
            first_msg = event_data[0] if isinstance(event_data[0], dict) else {}
            # DEBUG: log raw key object to see actual remoteJid
            if isinstance(first_msg.get("key"), dict):
                _p("RAW KEY:", first_msg.get("key"))
            sender2, text2 = _extract_from_and_text(first_msg)
            sender = sender or sender2
            text = text or text2
            _p("ARRAY extract from=", sender, "text=", text[:200])
        
        # Try extracting from common WABot message fields
        if (not sender or not text) and isinstance(event_data, dict):
            # WABot might use "key" -> "remoteJid" for sender, "message" -> "conversation" for text
            key_obj = event_data.get("key", {})
            if isinstance(key_obj, dict):
                remote_jid = key_obj.get("remoteJid", "")
                if remote_jid:
                    sender = sender or _norm_number(remote_jid.replace("@s.whatsapp.net", ""))
            
            msg_obj = event_data.get("message", {})
            if isinstance(msg_obj, dict):
                conversation = msg_obj.get("conversation", "")
                if conversation:
                    text = text or conversation
            _p("WABOT STRUCT extract from=", sender, "text=", text[:200])

        # ---- Check if message is from bot/outbound status (skip processing) ----
        # Some WABot setups forward outbound messages too; those will cause reply loops.
        is_bot_msg = (meta.get("from_me") is True)
        # Heuristic: Baileys includes `status` primarily for outbound messages.
        if meta.get("status") not in (None, 0, "0"):
            is_bot_msg = True
            _p("SKIP: message has status field (likely outbound)", meta.get("status"))
        if meta.get("from_me") is True:
            _p("SKIP: Message is from bot (fromMe=true), ignoring")
        
        if is_bot_msg:
            _p("WEBHOOK 200 OK (bot message skipped)")
            return JsonResponse({"status": "ok"}, status=200)
        
        # ---- Extract media information (images, videos, documents) ----
        media_type_val, media_url_val, media_caption, media_meta_val = None, None, None, None
        if is_message and isinstance(event_data, list) and len(event_data) > 0:
            first_msg = event_data[0] if isinstance(event_data[0], dict) else {}
            _maybe_log_media_payload(first_msg)
            media_type_val, media_url_val, media_caption, media_meta_val = _extract_media_info(first_msg)
            if media_type_val:
                _p(f"MEDIA DETECTED type={media_type_val} url={media_url_val[:100] if media_url_val else 'None'}")
        
        # ---- Process incoming message ----
        # Allow text-only, media-only, or text+media messages
        if is_message and sender and (text or media_url_val):
            # Process through full contest flow (PDPA, keywords, OCR, etc.)
            # Use caption as text if no conversation text present
            effective_text = text or media_caption or ""
            _process_incoming_message(
                sender,
                effective_text,
                msg_id,
                media_url=media_url_val or "",
                media_type=media_type_val or "",
                media_meta=media_meta_val or {},
            )
        
        # ---- Optional echo reply for testing ----
        # Turn on with env var: WABOT_ENABLE_AUTOREPLY=true
        # Sends via `WhatsAppAPIService` to avoid needing a separate token name.
        if _echo_enabled() and sender and text:
            try:
                from .whatsapp_service import WhatsAppAPIService
                WhatsAppAPIService().send_text_message(sender, f"Echo: {text}")
            except Exception as e:
                _p("ECHO SEND ERROR:", str(e)[:200])

        _p("WEBHOOK 200 OK")
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as e:
        _p("WEBHOOK ERROR:", str(e)[:500])
        import traceback
        _p("WEBHOOK TRACEBACK:", traceback.format_exc()[:1200])
        _p("WEBHOOK 200 OK (error swallowed)")
        return JsonResponse({"status": "ok"}, status=200)
