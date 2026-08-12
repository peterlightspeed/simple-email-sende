import streamlit as st
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr

st.set_page_config(page_title="Simple Bulk Email Sender", page_icon="📧")

st.title("📧 Simple Bulk Email Sender")
st.write("Send the same message to a list of recipients using your Gmail account.")

sender_name = st.text_input(
    "Sender Name (this is what recipients will see instead of your raw email)"
)
sender_email = st.text_input("Sender Email")
app_password = st.text_input(
    "Google App Password",
    type="password",
    help="Use a 16-character Google App Password, not your normal Gmail password."
)
subject = st.text_input("Email Subject")
body = st.text_area("Message Body", height=200)
uploaded_images = st.file_uploader(
    "Attach Images (optional)",
    type=["png", "jpg", "jpeg", "gif"],
    accept_multiple_files=True
)
recipients_raw = st.text_area(
    "Recipient Emails (comma or newline separated)",
    height=150
)

send_button = st.button("Send Bulk Emails", type="primary", use_container_width=True)

if send_button:
    if not sender_email or not app_password or not subject or not body or not recipients_raw:
        st.error("Please fill in all required fields before sending.")
    else:
        # Parse recipients: allow commas and/or newlines as separators
        raw_list = recipients_raw.replace(",", "\n").split("\n")
        recipients = [addr.strip() for addr in raw_list if addr.strip()]

        if not recipients:
            st.error("Please enter at least one recipient email.")
        else:
            # Read uploaded images into memory once, before sending starts
            image_attachments = []
            if uploaded_images:
                for img in uploaded_images:
                    image_attachments.append((img.name, img.getvalue()))

            # Build the "From" display name. If a name is given, recipients
            # will see that name first; the address is still technically
            # present in the header (that's how email works) but is not
            # what's shown up front in the inbox.
            display_from = formataddr((sender_name, sender_email)) if sender_name else sender_email

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
                        msg["From"] = display_from
                        msg["To"] = recipient
                        msg["Subject"] = subject
                        msg.attach(MIMEText(body, "plain"))

                        for filename, data in image_attachments:
                            image_part = MIMEImage(data, name=filename)
                            image_part.add_header(
                                "Content-Disposition", "attachment", filename=filename
                            )
                            msg.attach(image_part)

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
                    st.success(f" Done at lightspeed! {sent_count} out of {total} emails were sent successfully.")
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
