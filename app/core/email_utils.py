import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = "noreply@yourapp.com"  # must be verified on Resend

def send_password_reset_email(to_email: str, reset_token: str):
    reset_link = f"https://yourfrontend.com/reset-password?token={reset_token}"

    html_body = f"""
    <h2>Password Reset Request</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_link}" target="_blank">{reset_link}</a>
    <br/><br/>
    <p>If this wasn't you, ignore this email.</p>
    """

    return resend.Emails.send({
        "from": FROM_EMAIL,
        "to": to_email,
        "subject": "Reset Your Password",
        "html": html_body
    })
