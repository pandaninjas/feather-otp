# feather-otp
feather-otp is a simple, easy to use, lightweight, and secure TOTP (Time-based One-Time Password) generator.
It works on the command line, and is coded in python with the pyotp and pyaescrypt libraries.

## Considerations for use
This encrypts your otp secret with a password, and stores the encrypted secret in a file. It never sends your data to a remote server, so if your password is lost, all your data is lost.