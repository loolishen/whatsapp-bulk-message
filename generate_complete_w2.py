#!/usr/bin/env python3
"""
Complete W2 Data Generator for all 199 entries
Run this script to generate the full khind_merdeka_w2_data.py file
"""

def parse_w2_entry(line):
    """Parse a single W2 entry line into a dictionary"""
    parts = line.split('\t')
    
    # Ensure we have enough parts
    while len(parts) < 22:
        parts.append('')
    
    # Map validity correctly
    validity = parts[1].strip().upper()
    if validity == 'VALID':
        validity = 'valid'
    elif validity == 'INVALID':
        validity = 'invalid'
    elif validity == 'DUPLICATE':
        validity = 'duplicate'
    else:
        validity = 'valid'  # default
    
    return {
        'submission_no': parts[0].strip() if len(parts) > 0 else '',
        'validity': validity,
        'reason': parts[2].strip() if len(parts) > 2 else '',
        'amount_spent': parts[3].strip() if len(parts) > 3 else '',
        'store': parts[4].strip() if len(parts) > 4 else '',
        'store_location': parts[5].strip() if len(parts) > 5 else '',
        'product_purchased_1': parts[6].strip() if len(parts) > 6 else '',
        'amount_purchased_1': parts[7].strip() if len(parts) > 7 else '',
        'product_purchased_2': parts[8].strip() if len(parts) > 8 else '',
        'amount_purchased_2': parts[9].strip() if len(parts) > 9 else '',
        'product_purchased_3': parts[10].strip() if len(parts) > 10 else '',
        'amount_purchased_3': parts[11].strip() if len(parts) > 11 else '',
        'full_name': parts[12].strip() if len(parts) > 12 else '',
        'phone_number': parts[13].strip() if len(parts) > 13 else '',
        'email': parts[14].strip() if len(parts) > 14 else '',
        'address': parts[15].strip() if len(parts) > 15 else '',
        'postcode': parts[16].strip() if len(parts) > 16 else '',
        'city': parts[17].strip() if len(parts) > 17 else '',
        'state': parts[18].strip() if len(parts) > 18 else '',
        'receipt_url': parts[19].strip() if len(parts) > 19 else '',
        'how_heard': parts[20].strip() if len(parts) > 20 else '',
        'submitted_date': parts[21].strip() if len(parts) > 21 else ''
    }

def main():
    """
    Instructions:
    1. Copy all your raw W2 data (all 199 lines from MLP_202 to MLP_400)
    2. Paste it into the raw_data variable below (replace the placeholder)
    3. Run this script: python generate_complete_w2.py
    4. It will generate the complete messaging/khind_merdeka_w2_data.py file
    """
    
    # PASTE YOUR COMPLETE RAW DATA HERE (all 199 lines)
    raw_data = """
    # Replace this comment with all your raw data from MLP_202 to MLP_400
    # Each line should be tab-separated as you provided
    # Example format:
    # MLP_202	VALID		RM320.00	LIAN HONG TRADING	KOTA BHARU, KELANTAN	RC118M	1					MOHD ZUFRI BIN MAT RADZI	60145000000	nikazlin.anuar38@gmail.com	PT 258, Kampung Tanjung Bunut Susu	17000	Pasir Mas	Kelantan	https://form-builder-by-hulkapps.s3.amazonaws.com/uploads/khindmarketing.myshopify.com/store_image/image_7e57dc2b-96fb-4663-9601-e97e17036cd9.jpg	In-store Display	12/8/2025 12:16
    """
    
    print("W2 Data Generator")
    print("=================")
    print("To use this script:")
    print("1. Edit this file and paste all your raw W2 data in the raw_data variable")
    print("2. Run: python generate_complete_w2.py")
    print("3. It will generate the complete khind_merdeka_w2_data.py file")
    print()
    print("Current status: Waiting for raw data to be added to script")
    
    # Check if raw data has been added
    if "Replace this comment" in raw_data:
        print("❌ Please add your raw data to the script first")
        return
    
    # Process the data
    entries = []
    lines = [line.strip() for line in raw_data.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
    
    print(f"Processing {len(lines)} entries...")
    
    for line in lines:
        if line.strip():
            try:
                entry = parse_w2_entry(line)
                entries.append(entry)
            except Exception as e:
                print(f"Error processing line: {line[:50]}... - {e}")
    
    # Generate Python file content
    python_content = f'''# Khind Merdeka W2 Contest Data - Complete Dataset ({len(entries)} entries)
KHIND_MERDEKA_W2_DATA = [
'''
    
    for i, entry in enumerate(entries):
        python_content += "    {\n"
        for key, value in entry.items():
            python_content += f"        '{key}': {repr(value)},\n"
        python_content += "    }"
        if i < len(entries) - 1:
            python_content += ","
        python_content += "\n"
    
    python_content += "]\n"
    
    # Write to file
    try:
        with open('messaging/khind_merdeka_w2_data.py', 'w', encoding='utf-8') as f:
            f.write(python_content)
        print(f"✅ Successfully generated complete W2 data file with {len(entries)} entries!")
        print("📁 File saved as: messaging/khind_merdeka_w2_data.py")
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    main()
