"""
Khind Merdeka Campaign Data Service
Integrates W1 and W2 contest data into dashboard and managers
"""
from .khind_merdeka_w1_data import KHIND_MERDEKA_W1_DATA
from .khind_merdeka_w2_data import KHIND_MERDEKA_W2_DATA
from datetime import datetime
import re

class MerdekaDataService:
    """Service to handle Khind Merdeka campaign data"""
    
    def __init__(self):
        self.w1_data = KHIND_MERDEKA_W1_DATA
        self.w2_data = KHIND_MERDEKA_W2_DATA
        self.all_data = self.w1_data + self.w2_data
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard display"""
        total_submissions = len(self.all_data)
        valid_submissions = len([entry for entry in self.all_data if entry.get('validity') == 'valid'])
        invalid_submissions = len([entry for entry in self.all_data if entry.get('validity') == 'invalid'])
        duplicate_submissions = len([entry for entry in self.all_data if entry.get('validity') == 'duplicate'])
        
        # Calculate approved/flagged based on validity
        approved_submissions = valid_submissions
        flagged_submissions = invalid_submissions + duplicate_submissions
        
        # Calculate total amount spent
        total_amount = 0
        for entry in self.all_data:
            if entry.get('validity') == 'valid' and entry.get('amount_spent'):
                amount_str = entry['amount_spent'].replace('RM', '').replace(',', '').strip()
                try:
                    amount = float(amount_str)
                    total_amount += amount
                except (ValueError, TypeError):
                    pass
        
        # Get state distribution
        state_distribution = {}
        for entry in self.all_data:
            if entry.get('validity') == 'valid' and entry.get('state'):
                state = entry['state']
                state_distribution[state] = state_distribution.get(state, 0) + 1
        
        # Get top products
        product_counts = {}
        for entry in self.all_data:
            if entry.get('validity') == 'valid':
                for i in range(1, 4):  # Check product_purchased_1, _2, _3
                    product_key = f'product_purchased_{i}'
                    if entry.get(product_key) and entry[product_key].strip():
                        product = entry[product_key]
                        product_counts[product] = product_counts.get(product, 0) + 1
        
        top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_submissions': total_submissions,
            'valid_submissions': valid_submissions,
            'invalid_submissions': invalid_submissions,
            'duplicate_submissions': duplicate_submissions,
            'approved_submissions': approved_submissions,
            'flagged_submissions': flagged_submissions,
            'total_amount_spent': total_amount,
            'state_distribution': state_distribution,
            'top_products': top_products,
            'w1_count': len(self.w1_data),
            'w2_count': len(self.w2_data)
        }
    
    def get_contest_data(self):
        """Get data formatted for contest manager"""
        contests = [
            {
                'contest_id': 'merdeka_w1',
                'name': 'Khind Merdeka Campaign 2025 - Week 1',
                'description': 'Merdeka Week 1 Contest Submissions',
                'starts_at': '2025-08-01',
                'ends_at': '2025-08-07',
                'is_active': True,
                'total_entries': len(self.w1_data),
                'valid_entries': len([entry for entry in self.w1_data if entry.get('validity') == 'valid']),
                'total_amount': self._calculate_total_amount(self.w1_data)
            },
            {
                'contest_id': 'merdeka_w2',
                'name': 'Khind Merdeka Campaign 2025 - Week 2',
                'description': 'Merdeka Week 2 Contest Submissions',
                'starts_at': '2025-08-08',
                'ends_at': '2025-08-14',
                'is_active': True,
                'total_entries': len(self.w2_data),
                'valid_entries': len([entry for entry in self.w2_data if entry.get('validity') == 'valid']),
                'total_amount': self._calculate_total_amount(self.w2_data)
            }
        ]
        return contests
    
    def get_participants_data(self, contest_week=None):
        """Get participants data for participants manager"""
        if contest_week == 'w1':
            data = self.w1_data
        elif contest_week == 'w2':
            data = self.w2_data
        else:
            data = self.all_data
        
        participants = []
        for entry in data:
            participant = {
                'submission_no': entry.get('submission_no', ''),
                'full_name': entry.get('full_name', ''),
                'phone_number': entry.get('phone_number', ''),
                'email': entry.get('email', ''),
                'address': entry.get('address', ''),
                'city': entry.get('city', ''),
                'state': entry.get('state', ''),
                'postcode': entry.get('postcode', ''),
                'amount_spent': entry.get('amount_spent', ''),
                'store': entry.get('store', ''),
                'store_location': entry.get('store_location', ''),
                'validity': entry.get('validity', ''),
                'reason': entry.get('reason', ''),
                'submitted_date': entry.get('submitted_date', ''),
                'receipt_url': entry.get('receipt_url', ''),
                'how_heard': entry.get('how_heard', ''),
                'products': self._get_products(entry)
            }
            participants.append(participant)
        
        return participants
    
    def _calculate_total_amount(self, data):
        """Calculate total amount spent for a dataset"""
        total = 0
        for entry in data:
            if entry.get('validity') == 'valid' and entry.get('amount_spent'):
                amount_str = entry['amount_spent'].replace('RM', '').replace(',', '').strip()
                try:
                    amount = float(amount_str)
                    total += amount
                except (ValueError, TypeError):
                    pass
        return total
    
    def _get_products(self, entry):
        """Extract products from an entry"""
        products = []
        for i in range(1, 4):
            product_key = f'product_purchased_{i}'
            amount_key = f'amount_purchased_{i}'
            if entry.get(product_key) and entry[product_key].strip():
                products.append({
                    'product': entry[product_key],
                    'amount': entry.get(amount_key, '')
                })
        return products
    
    def get_recent_submissions(self, limit=10):
        """Get recent submissions for dashboard"""
        # Sort by submission number (assuming higher numbers are more recent)
        sorted_data = sorted(self.all_data, key=lambda x: self._extract_submission_number(x.get('submission_no', '')), reverse=True)
        return sorted_data[:limit]
    
    def _extract_submission_number(self, submission_no):
        """Extract numeric part from submission number for sorting"""
        if not submission_no:
            return 0
        numbers = re.findall(r'\d+', submission_no)
        return int(numbers[0]) if numbers else 0
