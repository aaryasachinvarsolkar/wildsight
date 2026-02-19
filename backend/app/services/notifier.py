import os
import resend
from dotenv import load_dotenv

load_dotenv()

class NotifierService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "alerts@wildsight.org")
        
        if self.api_key:
            resend.api_key = self.api_key
            self.is_dev_mode = False
        else:
            print("[WARNING] RESEND_API_KEY not found. Running in MOCK MODE.")
            self.is_dev_mode = True

    def send_email(self, to_email: str, subject: str, message_body: str):
        if self.is_dev_mode:
            print(f"\n--- [DEV MODE EMAIL] ---")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {message_body}")
            print(f"------------------------\n")
            return True

        try:
            params = {
                "from": f"WildSight <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": message_body.replace("\n", "<br>"),
            }
            print(f"  [LOG] 📧 Sending Email to: {to_email} | Subject: {subject}")
            resend.Emails.send(params)
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to send email via Resend: {e}")
            return False

    def notify_user_about_species(self, user_email: str, user_name: str, species_name: str, distance_km: float, risk_score: float):
        subject = f"🚨 URGENT: High-Risk {species_name} Detected Near You"
        
        body = f"""Dear {user_name},

Our EcoGuard AI has detected an urgent situation regarding the <b>{species_name}</b>, which has been sighted within <b>{distance_km:.1f} km</b> of your monitored location.

<b>AI Intelligence Report:</b>
- Risk Index: {risk_score:.2f}/1.00
- Priority Level: URGENT
- Context: Immediate conservation actions are recommended to protect the local habitat.

Stay vigilant and thank you for being a part of the WildSight network.

Best regards,
The WildSight AI Team"""

        return self.send_email(user_email, subject, body)

notifier_service = NotifierService()
