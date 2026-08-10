import streamlit as st
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Simple Bulk Email Sender", page_icon="📧")

st.title("📧 Simple Bulk Email Sender")
st.write("Send the same message to a list of recipients using your Gmail account.")

sender_email = st.text_input("Sender Email")
app_password = st.text_input(
    "Google App Password",
    type="password",
    help="Use a 16-character Google App Password, not your normal Gmail password."
)
subject = st.text_input("Email Subject")
body = st.text_area("Message Body", height=200)
recipients_raw = st.text_area(
    "Recipient Emails (comma or newline separated)",
    height=150
)

send_button = st.button("Send Bulk Emails", type="primary", use_container_width=True)

if send_button:
    if not sender_email or not app_password or not subject or not body or not recipients_raw:
        st.error("Please fill in all fields before sending.")
    else:
        # Parse recipients: allow commas and/or newlines as separators
        raw_list = recipients_raw.replace(",", "\n").split("\n")
        recipients = [addr.strip() for addr in raw_list if addr.strip()]

        if not recipients:
            st.error("Please enter at least one recipient email.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            total = len(recipients)
            sent_count = 0
            failed_emails = []

            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)

                for i, recipient in enumerate(recipients):
                    status_text.info(f"Sending email to: {recipient}  ({i + 1} of {total})")

                    try:
                        msg = MIMEMultipart()
                        msg["From"] = sender_email
                        msg["To"] = recipient
                        msg["Subject"] = subject
                        msg.attach(MIMEText(body, "plain"))

                        server.sendmail(sender_email, recipient, msg.as_string())
                        sent_count += 1
                    except Exception as e:
                        failed_emails.append(recipient)
                        st.warning(f"Failed to send to {recipient}: {e}")

                    progress_bar.progress((i + 1) / total)

                    # 2-second delay between sends to avoid spam blocking
                    if i < total - 1:
                        time.sleep(2)

                server.quit()
                status_text.empty()

                if sent_count == total:
                    st.success(f"✅ Success! All {sent_count} emails were sent out.")
                else:
                    st.success(f"✅ Done! {sent_count} out of {total} emails were sent successfully.")
                    if failed_emails:
                        st.write("The following addresses failed to send:")
                        st.write(", ".join(failed_emails))

            except smtplib.SMTPAuthenticationError:
                st.error(
                    "Login failed. Double-check your email and Google App Password "
                    "(it must be an App Password, not your regular Gmail password)."
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")