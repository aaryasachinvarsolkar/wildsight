from app.services.notifier import notifier_service
import sys

# User email from screenshot
to_email = "anshikagupta410756@gmail.com"

print(f"Attempting to send real email to {to_email}...")
print(f"Using API Key: {notifier_service.api_key[:5]}...")

success = notifier_service.send_email(
    to_email=to_email,
    subject="WildSight Verification Email",
    message_body="<h1>It Works!</h1><p>This is a test email from WildSight to verify your alerts are working.</p>"
)

if success:
    print("SUCCESS: Email sent via Resend API.")
else:
    print("FAILURE: Could not send email. Check logs above.")
