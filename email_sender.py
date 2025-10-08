import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import logging
import os
import getpass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_credentials():
    """Helper function to set up credentials safely"""
    print("=" * 60)
    print("GMAIL BULK EMAIL SETUP")
    print("=" * 60)
    print("\nNOTE: You need to use an APP PASSWORD, not your regular Gmail password!")
    print("To get your App Password:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Factor Authentication")
    print("3. Generate an App Password for 'Mail'")
    print("4. Use the 16-character code (looks like: abcd efgh ijkl mnop)")
    print("=" * 60)
    
    gmail_address = input("Enter your Gmail address: ").strip()
    app_password = getpass.getpass("Enter your APP PASSWORD (16-character code): ").strip()
    
    return gmail_address, app_password

class GmailBulkSenderWithAttachments:
    def __init__(self, gmail_address, app_password):
        if not app_password or len(app_password.replace(" ", "")) != 16:
            print("\n❌ ERROR: App Password should be 16 characters long!")
            print("Make sure you're using the App Password, not your regular Gmail password.")
            raise ValueError("Invalid App Password format")
            
        self.gmail_address = gmail_address
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.port = 587
        
    def test_connection(self):
        """Test if credentials work"""
        try:
            server = self.create_connection()
            if server:
                server.quit()
                print("✅ Connection test successful!")
                return True
            return False
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Make sure 2-Factor Authentication is ENABLED")
            print("2. Use the 16-character App Password (not your regular password)")
            print("3. Check if you generated the App Password for 'Mail'")
            return False
        
    def create_connection(self):
        """Create SMTP connection"""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls(context=context)
            server.login(self.gmail_address, self.app_password)
            logger.info("Successfully connected to Gmail SMTP server")
            return server
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return None
    
    def safe_string_convert(self, value):
        """Safely convert any value to string, handling NaN and None"""
        if pd.isna(value) or value is None:
            return ""
        return str(value)
    
    def attach_file(self, msg, file_path):
        """Attach a file to the email message"""
        try:
            file_path_str = self.safe_string_convert(file_path)
            if not file_path_str or not os.path.exists(file_path_str):
                logger.error(f"Attachment file not found: {file_path_str}")
                return False
                
            with open(file_path_str, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path_str)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            
            msg.attach(part)
            logger.info(f"Successfully attached: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {str(e)}")
            return False
    
    def send_single_email(self, server, to_email, name, subject, message, pdf_attachment=None):
        """Send a single email with optional PDF attachment"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = self.safe_string_convert(to_email)
            msg['Subject'] = self.safe_string_convert(subject)
            
            # Convert all values to strings safely
            name_str = self.safe_string_convert(name)
            message_str = self.safe_string_convert(message)
            
            # Personalize message
            personalized_message = message_str.replace('{name}', name_str)
            msg.attach(MIMEText(personalized_message, 'plain'))
            
            # Add PDF attachment if provided
            if pdf_attachment and self.safe_string_convert(pdf_attachment).strip():
                attachment_path = self.safe_string_convert(pdf_attachment).strip()
                if not self.attach_file(msg, attachment_path):
                    logger.warning(f"Failed to attach PDF for {to_email}, sending without attachment")
            
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_bulk_emails(self, csv_file_path, delay_seconds=2):
        """Send bulk emails from CSV file with PDF attachments"""
        success_count = 0
        fail_count = 0
        
        try:
            # Read CSV file with explicit string conversion
            df = pd.read_csv(csv_file_path, dtype=str)  # Force all columns to be read as strings
            
            # Replace NaN with empty strings
            df = df.fillna('')
            
            logger.info(f"Loaded {len(df)} emails from CSV file")
            
            server = self.create_connection()
            if not server:
                return 0, len(df)
            
            for index, row in df.iterrows():
                try:
                    # Extract values with safe conversion
                    email = self.safe_string_convert(row['email'])
                    name = self.safe_string_convert(row.get('name', ''))
                    subject = self.safe_string_convert(row['subject'])
                    message = self.safe_string_convert(row['message'])
                    pdf_attachment = self.safe_string_convert(row.get('attachment', ''))
                    
                    logger.info(f"Processing {index + 1}/{len(df)}: {email}")
                    
                    if self.send_single_email(server, email, name, subject, message, pdf_attachment):
                        success_count += 1
                    else:
                        fail_count += 1
                    
                    if index < len(df) - 1:
                        time.sleep(delay_seconds)
                        
                except Exception as e:
                    logger.error(f"Error processing row {index}: {str(e)}")
                    fail_count += 1
            
            server.quit()
            logger.info(f"Completed: {success_count} successful, {fail_count} failed")
            return success_count, fail_count
            
        except Exception as e:
            logger.error(f"Error in bulk email sending: {str(e)}")
            return success_count, fail_count + (len(df) - (success_count + fail_count)) if 'df' in locals() else (0, 0)

def main():
    try:
        # Get credentials safely
        GMAIL_ADDRESS, APP_PASSWORD = setup_credentials()
        
        # Initialize sender
        sender = GmailBulkSenderWithAttachments(GMAIL_ADDRESS, APP_PASSWORD)
        
        # Test connection first
        print("\nTesting connection to Gmail...")
        if not sender.test_connection():
            print("Failed to connect. Please check your credentials and try again.")
            return
        
        # Send bulk emails
        CSV_FILE_PATH = "emails.csv"
        
        if not os.path.exists(CSV_FILE_PATH):
            print(f"❌ CSV file not found: {CSV_FILE_PATH}")
            return
            
        print(f"\nStarting bulk email sending from: {CSV_FILE_PATH}")
        success, failed = sender.send_bulk_emails(
            csv_file_path=CSV_FILE_PATH,
            delay_seconds=2
        )
        
        print(f"\n" + "="*50)
        print("FINAL RESULTS:")
        print(f"✅ Successful: {success}")
        print(f"❌ Failed: {failed}")
        print(f"📧 Total processed: {success + failed}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()

