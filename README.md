## How to set gmail email for sending upto 500 emails in a day
```
How to Get Your App Password
Step 1: Enable 2-Factor Authentication
Go to Google Account

Click Security on left sidebar

Under "How you sign in to Google", find 2-Step Verification

Click and follow prompts to enable it

Step 2: Generate App Password
Go back to Security page

Find 2-Step Verification (should now say "ON")

Scroll down to App passwords

You may need to sign in again

Select Mail as the app

Select Other as device (or your computer name)

Click Generate

Copy the 16-character code (looks like: abcd efgh ijkl mnop)



```

## How to Run
```
Install Python 12 software

Install the panda lib
pip install -r requirements.txt

# Run the script using 
python email_sender.py

```

## Sample Output
```
❯ python email_sender.py
============================================================
GMAIL BULK EMAIL SETUP
============================================================

NOTE: You need to use an APP PASSWORD, not your regular Gmail password!
To get your App Password:
1. Go to: https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Generate an App Password for 'Mail'
4. Use the 16-character code (looks like: abcd efgh ijkl mnop)
============================================================
Enter your Gmail address: test123@gmail.com
Enter your APP PASSWORD (16-character code): abcd efgh ijkl mnop

Testing connection to Gmail...
2025-10-08 09:47:27,441 - INFO - Successfully connected to Gmail SMTP server
✅ Connection test successful!

Starting bulk email sending from: emails.csv
2025-10-08 09:47:27,693 - INFO - Loaded 2 emails from CSV file
2025-10-08 09:47:29,069 - INFO - Successfully connected to Gmail SMTP server
2025-10-08 09:47:29,070 - INFO - Processing 1/2: test.qwe@gmail.com
2025-10-08 09:47:29,075 - INFO - Successfully attached: welcome.pdf
2025-10-08 09:47:31,340 - INFO - Email sent successfully to test.qwe@gmail.com
2025-10-08 09:47:33,345 - INFO - Processing 2/2: pops123@gmail.com
2025-10-08 09:47:33,349 - INFO - Successfully attached: cv.pdf
2025-10-08 09:47:35,837 - INFO - Email sent successfully to pops123@gmail.com
2025-10-08 09:47:36,057 - INFO - Completed: 2 successful, 0 failed

==================================================
FINAL RESULTS:
✅ Successful: 2
❌ Failed: 0
📧 Total processed: 2
==================================================

```