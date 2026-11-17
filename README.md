# TradeSim India — Email Login + Existing Data Migration

## Included migration
This project is preconfigured with the email account you supplied and a PBKDF2-SHA256 password hash. The password itself is **not** stored in this folder.
The existing `tradesim.db` was copied into `user_databases/75dfce42-c30e-4ba1-a050-c7ee01412457.db`.

Migrated data verified from your uploaded database:
- Account cash: ₹74,077.00003051758 (displayed rounded in the app)
- Portfolio rows: Infosys 0, Tata Consultancy Services 10, Wipro 5
- Trade records: 6

## Run locally
1. Extract this ZIP.
2. Open the extracted folder in VS Code.
3. In a terminal run: `python -m pip install -r requirements.txt`
4. Run: `streamlit run main.py`
5. Log in using the email and password you supplied in chat.

## Important
- The supplied password was used only to create a salted, slow password hash in `users.db`; it is not written in source code or README.
- Because you shared a password in chat, change it anywhere else you may have reused it. This starter project does not yet include a password-change screen.
- Email ownership is not verified: there is no email OTP.
- Keep the whole project folder together. `users.db` and `user_databases/` must remain in the same folder.
- Back up the project folder before making changes.
- This is a local learning project, not hardened for public multi-user hosting.
