import streamlit as st
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
import time
from streamlit_lottie import st_lottie
import requests

st.set_page_config(page_title="SendMails", layout="centered", page_icon="📧")

@st.cache_data
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

email_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_touohxv0.json")

st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>SendMails App</h1>
    <p style='text-align: center;'>Send personalized emails individually via Gmail using a simple and secure interface.</p>
""", unsafe_allow_html=True)

st_lottie(email_anim, height=200, key="email")

st.markdown("""
### 🔐 Before You Start
To use this tool, you'll need to generate a **Gmail App Password**. Here's how:
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is turned **ON**.
3. Visit [App Passwords](https://myaccount.google.com/apppasswords).
4. Choose Mail as the app and Other for the device (e.g., "BulkEmailApp").
5. Google will give you a **16-character password** (like abcd efgh ijkl mnop). Paste it below.

**Example:**
```
Your Gmail: youremail@gmail.com
App Password: abcd efgh ijkl mnop
```
 
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📎 Upload a CSV or TXT file containing the email addresses you want to send messages to (comma, | or newline separated)", type=['csv', 'txt'])
gmail_user = st.text_input("Your Gmail Address", placeholder="example@gmail.com")
app_password = st.text_input("App Password (16 characters)", type="password")
subject = st.text_input("Email Subject")

st.markdown("### ✍️ Compose your Email:")
message_body = st.text_area("Email Message (Supports HTML)", height=200, help="Use basic HTML for formatting (e.g., <b>Bold</b>, <i>Italic</i>, <u>Underline</u>).")

attachments = st.file_uploader("📁 Attach Files (Images, Docs, PDFs, etc.)", accept_multiple_files=True)
send_button = st.button("📤 Send Emails")

if send_button:
    if not all([gmail_user, app_password, subject, message_body, uploaded_file]):
        st.error("Please fill all the fields and upload the email file.")
    else:
        try:
            file_content = uploaded_file.read().decode("utf-8")

            if uploaded_file.name.endswith(".csv") and "," in file_content and "\n" in file_content:
                try:
                    df = pd.read_csv(uploaded_file)
                    emails = df.iloc[:, 0].dropna().tolist()
                except Exception:
                    emails = [e.strip() for e in file_content.replace("|", ",").replace("\n", ",").split(",") if e.strip()]
            else:
                emails = [e.strip() for e in file_content.replace("|", ",").replace("\n", ",").split(",") if e.strip()]

            if not emails:
                st.error("No valid email addresses found in the file.")
                st.stop()

            st.info(f"📬 Total emails to send: {len(emails)}")

            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
            try:
                server.login(gmail_user, app_password)
            except smtplib.SMTPAuthenticationError:
                st.error("❌ Authentication failed. Please check your App Password.")
                st.stop()
            except smtplib.SMTPException as e:
                st.error(f"❌ SMTP error occurred during login: {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Unexpected error during login: {e}")
                st.stop()

            sent_count = 0
            for email in emails:
                msg = EmailMessage()
                msg["From"] = gmail_user
                msg["To"] = email
                msg["Subject"] = subject
                msg.set_content(message_body, subtype="html")

                for file in attachments:
                    try:
                        file_data = file.read()
                        msg.add_attachment(file_data,
                                           maintype='application',
                                           subtype='octet-stream',
                                           filename=file.name)
                    except Exception as e:
                        st.warning(f"⚠️ Failed to attach {file.name}: {e}")

                try:
                    server.send_message(msg)
                    sent_count += 1
                    st.success(f"✅ Email sent to {email}")
                    time.sleep(0.3)
                except smtplib.SMTPRecipientsRefused:
                    st.error(f"❌ Recipient refused: {email}")
                except smtplib.SMTPException as e:
                    st.error(f"❌ SMTP error while sending to {email}: {e}")
                except Exception as e:
                    st.error(f"❌ Unknown error while sending to {email}: {e}")

            server.quit()
            st.success(f"🎉 Finished sending {sent_count} emails.")

        except UnicodeDecodeError:
            st.error("❌ File could not be decoded. Please upload a valid CSV or TXT file.")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")

st.markdown("""
---
<p style='text-align: center; font-size: 0.9em;'>
Created with ❤️ by <a href="https://mohammedfurquansaleem.in" target="_blank">Mohammed Furquan Saleem</a>  | 
&copy; 2025 <span style='font-size: 1.1em;'>©</span> All Rights Reserved
</p>
""", unsafe_allow_html=True)