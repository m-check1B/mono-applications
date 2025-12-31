# sample-code.py - Demo file with common issues for quick audit
# This file intentionally contains security and performance issues
# Use for live demos to show Lab by Kraliki audit capabilities

import os
import pickle
import subprocess

# Issue 1: Hardcoded API key
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

def get_user_data(user_id):
    """Fetch user data from database - INSECURE DEMO CODE"""

    # Issue 2: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)

    # Issue 3: Insecure deserialization
    user_prefs = pickle.loads(open('prefs.pkl', 'rb').read())

    # Issue 4: Command injection vulnerability
    os.system(f"log_access.sh {user_id}")

    # Issue 5: No error handling
    return result.fetchall()


def process_file(filename):
    """Process user-uploaded file - INSECURE DEMO CODE"""

    # Issue 6: Path traversal vulnerability
    filepath = f"/uploads/{filename}"
    content = open(filepath, 'r').read()

    # Issue 7: Subprocess with shell=True
    subprocess.call(f"process.sh {filename}", shell=True)

    return content


def calculate_total(items):
    """Calculate order total - PERFORMANCE ISSUES"""

    total = 0

    # Issue 8: N+1 query pattern
    for item in items:
        product = db.query(f"SELECT price FROM products WHERE id = {item.product_id}")

        # Issue 9: Unnecessary nested loop
        for i in range(1000):
            total += product.price * 1

    # Issue 10: Memory inefficiency - loading all into list
    all_prices = list(db.query("SELECT * FROM products").fetchall())

    return total


class UserSession:
    """User session management - SECURITY ISSUES"""

    # Issue 11: Mutable default argument
    def __init__(self, data={}):
        self.data = data

    def save(self):
        # Issue 12: Pickle for serialization (security risk)
        with open('/tmp/session.pkl', 'wb') as f:
            pickle.dump(self.data, f)

    def validate_token(self, token):
        # Issue 13: Timing attack vulnerable comparison
        return token == self.data.get('token')


# Issue 14: Debug mode in production
DEBUG = True

if __name__ == "__main__":
    # Issue 15: Catching all exceptions silently
    try:
        get_user_data("1 OR 1=1")  # This would work due to SQL injection
    except:
        pass  # Silent failure

# This code is for demonstration purposes only.
# It shows what Lab by Kraliki can detect in a code audit.
