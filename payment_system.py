import os
import stripe
import tkinter as tk
from tkinter import messagebox
from flask import Flask, request
import threading

# Flask App for Backend
app = Flask(__name__)

# Stripe API Configuration
stripe.api_key = "your_secret_key"  # Replace with your Stripe Secret Key
WEBHOOK_SECRET = "your_webhook_secret"  # Replace with your Stripe Webhook Secret

# Webhook Endpoint
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            print(f"Payment succeeded: {payment_intent['id']}")
        return "Webhook received", 200
    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook Error: {e}")
        return "Webhook signature verification failed", 400

# Start Flask in a separate thread
def run_flask():
    app.run(host="0.0.0.0", port=5000)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Tkinter App for Frontend
def create_payment_intent(amount, currency="usd"):
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,  # Amount in cents
            currency=currency,
            payment_method_types=["card"]
        )
        return intent.client_secret
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        return None

def validate_and_submit():
    card_number = entry_card_number.get()
    expiry_date = entry_expiry_date.get()
    cvc = entry_cvc.get()

    # Validation
    if not card_number.isdigit() or len(card_number) != 16:
        messagebox.showerror("Error", "Invalid Card Number! It should be 16 digits.")
        return
    if not expiry_date or len(expiry_date) != 5 or expiry_date[2] != '/':
        messagebox.showerror("Error", "Invalid Expiry Date! Format: MM/YY")
        return
    if not cvc.isdigit() or len(cvc) not in [3, 4]:
        messagebox.showerror("Error", "Invalid CVC! It should be 3 or 4 digits.")
        return

    # Payment Processing
    try:
        amount_in_cents = 1000  # Example amount: $10
        client_secret = create_payment_intent(amount_in_cents)
        if client_secret:
            messagebox.showinfo("Payment Success", "Payment processed successfully!")
        else:
            raise Exception("Payment processing failed.")
    except Exception as e:
        messagebox.showerror("Error", f"Payment failed: {e}")

# Tkinter GUI
root = tk.Tk()
root.title("Payment Form")
root.geometry("400x300")
root.configure(bg="#f5f5f5")

# Title
tk.Label(root, text="Secure Payment", font=("Arial", 16), bg="#f5f5f5", fg="#007bff").pack(pady=10)

# Card Number
tk.Label(root, text="Card Number", bg="#f5f5f5").pack(anchor="w", padx=20)
entry_card_number = tk.Entry(root, width=30)
entry_card_number.pack(padx=20, pady=5)

# Expiry Date
tk.Label(root, text="Expiry Date (MM/YY)", bg="#f5f5f5").pack(anchor="w", padx=20)
entry_expiry_date = tk.Entry(root, width=30)
entry_expiry_date.pack(padx=20, pady=5)

# CVC
tk.Label(root, text="CVC", bg="#f5f5f5").pack(anchor="w", padx=20)
entry_cvc = tk.Entry(root, width=30, show="*")
entry_cvc.pack(padx=20, pady=5)

# Submit Button
pay_now_button = tk.Button(root, text="Pay Now", bg="#007bff", fg="white", width=20, command=validate_and_submit)
pay_now_button.pack(pady=20)

# Run the Tkinter main loop
root.mainloop()
