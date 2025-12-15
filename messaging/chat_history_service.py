"""
Chat History Service for Khind Merdeka Campaign
Generates hardcoded WhatsApp chat histories for each participant
"""
import random
from datetime import datetime, timedelta

class ChatHistoryService:
    """Service to generate realistic WhatsApp chat histories for participants"""
    
    def __init__(self):
        self.bot_messages = [
            "Hi {name}! 👋 Welcome to the Khind Merdeka W1 Contest! We're celebrating Malaysia's independence with amazing prizes!",
            "Before we continue, we need your consent to collect and process your personal data. Please read our privacy policy here: https://khind.com.my/pages/privacy-policy Do you agree to participate and allow us to process your information? Reply \"I agree\" to continue or \"No\" to opt out.",
            "Wonderful! Welcome to the contest! Ready to submit your entry? Let's get started!",
            "Please provide your details as well as a picture of your NRIC! Name: Email address: NRIC:",
            "Excellent! Now please upload your purchase receipt photo.",
            "For best results, follow these steps:\n1. Place receipt on a flat surface\n2. Ensure good lighting (avoid shadows)\n3. Hold your phone steady\n4. Capture the ENTIRE receipt in frame\n5. Make sure all text is clear and readable",
            "The receipt must show:\n✅ Store name\n✅ Product purchased (Khind product)\n✅ Total amount (minimum RM98)\n✅ Purchase date (within contest period)\n✅ Receipt number/invoice\n\nPlease upload your receipt now!",
            "Processing your receipt... Please wait a moment.",
            "Perfect! I can see your receipt clearly.\nHere's what I found:\n📄 Invoice #{invoice}\n🏪 Store: {store}\n📍 Location: {location}\n📅 Purchase Date: {purchase_date}\n📦 Product: {product}\n💰 Amount: {amount}\n\nAll details verified! ✔\nYour entry is VALID and has been successfully submitted! 🎉",
            "Contest Entry Details:\n👤 Name: {name}\n📧 Email: {email}\n📱 Phone: {phone}\n🏷️ Entry Number: {entry_number}\n\nWinner announcement: November 15, 2025\nWe'll notify winners directly via WhatsApp.\nGood luck!"
        ]
        
        self.user_responses = [
            "hi",
            "I agree",
            "Name: {name}\nEmail Address: {email}\nNRIC: {nric}",
            "Here's my receipt:",
            "Thank you!"
        ]
    
    def generate_chat_history(self, participant):
        """Generate a complete chat history for a participant"""
        name = participant.get('full_name', 'Participant')
        email = participant.get('email', '')
        phone = participant.get('phone_number', '')
        store = participant.get('store', 'Khind Store')
        location = participant.get('store_location', 'Malaysia')
        amount = participant.get('amount_spent', 'RM98.00')
        product = participant.get('products', [{}])[0].get('product', 'Khind Product') if participant.get('products') else 'Khind Product'
        submission_no = participant.get('submission_no', 'MLP_000')
        
        # Generate random times for the conversation
        base_time = datetime.now() - timedelta(days=random.randint(1, 30))
        times = [
            base_time,
            base_time + timedelta(minutes=1),
            base_time + timedelta(minutes=1),
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=3),
            base_time + timedelta(minutes=3),
            base_time + timedelta(minutes=4),
            base_time + timedelta(minutes=4),
            base_time + timedelta(minutes=5)
        ]
        
        # Generate conversation
        chat_history = []
        
        # Message 1: Bot welcome
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[0].format(name=name.split()[0] if name else 'Participant'),
            'timestamp': times[0].strftime('%H:%M'),
            'status': None
        })
        
        # Message 2: Bot privacy policy
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[1],
            'timestamp': times[1].strftime('%H:%M'),
            'status': None,
            'has_link': True,
            'link_url': 'https://khind.com.my/pages/privacy-policy',
            'link_text': 'khind.com.my'
        })
        
        # Message 3: User greeting
        chat_history.append({
            'sender': 'user',
            'message': self.user_responses[0],
            'timestamp': times[2].strftime('%H:%M'),
            'status': 'delivered'
        })
        
        # Message 4: User agreement
        chat_history.append({
            'sender': 'user',
            'message': self.user_responses[1],
            'timestamp': times[3].strftime('%H:%M'),
            'status': 'delivered'
        })
        
        # Message 5: Bot confirmation
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[2],
            'timestamp': times[4].strftime('%H:%M'),
            'status': None
        })
        
        # Message 6: Bot request for details
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[3],
            'timestamp': times[5].strftime('%H:%M'),
            'status': None
        })
        
        # Message 7: User provides details
        nric = self._generate_nric()
        chat_history.append({
            'sender': 'user',
            'message': self.user_responses[2].format(
                name=name,
                email=email,
                nric=nric
            ),
            'timestamp': times[6].strftime('%H:%M'),
            'status': 'delivered'
        })
        
        # Message 8: Bot receipt request
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[4],
            'timestamp': times[7].strftime('%H:%M'),
            'status': None
        })
        
        # Message 9: Bot receipt instructions
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[5],
            'timestamp': times[7].strftime('%H:%M'),
            'status': None
        })
        
        # Message 10: Bot receipt requirements
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[6],
            'timestamp': times[7].strftime('%H:%M'),
            'status': None
        })
        
        # Message 11: User uploads receipt
        chat_history.append({
            'sender': 'user',
            'message': self.user_responses[3],
            'timestamp': times[8].strftime('%H:%M'),
            'status': 'delivered',
            'has_image': True,
            'image_url': participant.get('receipt_url', ''),
            'image_alt': 'Purchase Receipt'
        })
        
        # Message 12: Bot processing
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[7],
            'timestamp': times[9].strftime('%H:%M'),
            'status': None
        })
        
        # Message 13: Bot confirmation with details
        invoice_number = f"1724{random.randint(1, 999)}"
        entry_number = f"KM-W1-{random.randint(100, 999)}"
        purchase_date = self._generate_purchase_date()
        
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[8].format(
                invoice=invoice_number,
                store=store,
                location=location,
                purchase_date=purchase_date,
                product=product,
                amount=amount
            ),
            'timestamp': times[9].strftime('%H:%M'),
            'status': None
        })
        
        # Message 14: Bot final confirmation
        chat_history.append({
            'sender': 'bot',
            'message': self.bot_messages[9].format(
                name=name,
                email=email,
                phone=phone,
                entry_number=entry_number
            ),
            'timestamp': times[9].strftime('%H:%M'),
            'status': None
        })
        
        # Message 15: User thanks
        chat_history.append({
            'sender': 'user',
            'message': self.user_responses[4],
            'timestamp': times[9].strftime('%H:%M'),
            'status': 'delivered'
        })
        
        return chat_history
    
    def _generate_nric(self):
        """Generate a realistic Malaysian NRIC"""
        # Generate random birth year (1950-2000)
        year = random.randint(50, 99)
        # Generate random month (01-12)
        month = f"{random.randint(1, 12):02d}"
        # Generate random day (01-28)
        day = f"{random.randint(1, 28):02d}"
        # Generate random location code
        location = random.randint(1, 14)
        # Generate random sequence
        sequence = f"{random.randint(1, 999):03d}"
        
        return f"{year:02d}{month}{day}-{location:02d}-{sequence}"
    
    def _generate_purchase_date(self):
        """Generate a realistic purchase date within contest period"""
        # Contest period: August 1-14, 2025
        start_date = datetime(2025, 8, 1)
        end_date = datetime(2025, 8, 14)
        
        # Random date within contest period
        random_days = random.randint(0, (end_date - start_date).days)
        purchase_date = start_date + timedelta(days=random_days)
        
        return purchase_date.strftime('%B %d, %Y')
    
    def get_chat_history_for_participant(self, participant_id, all_participants):
        """Get chat history for a specific participant"""
        participant = next((p for p in all_participants if p.get('submission_no') == participant_id), None)
        if not participant:
            return []
        
        return self.generate_chat_history(participant)
