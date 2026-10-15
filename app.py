from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Bus Pricing & Details Database
BUS_DETAILS = {
    "Cloud Express AC (Non-Stop)": {
        "price": 650,
        "duration": "5h 30m",
        "washroom": "Yes 🚽",
        "amenities": "AC, Reclining Seats, Charging Port, Water Bottle",
        "stops": "Non-Stop Direct Express"
    },
    "Royal Sleeper Deluxe": {
        "price": 850,
        "duration": "6h 45m",
        "washroom": "Yes 🚽",
        "amenities": "AC Sleeper, Blanket, Charging Port, Wi-Fi 📶",
        "stops": "2 Commercial Highway Stops"
    },
    "Super Luxury Express": {
        "price": 450,
        "duration": "7h 10m",
        "washroom": "No ❌",
        "amenities": "Pushback Seats, Music System, Water Bottle",
        "stops": "3 City Enroute Stops"
    },
    "Metro Star Volvo AC": {
        "price": 950,
        "duration": "5h 15m",
        "washroom": "Yes 🚽",
        "amenities": "Multi-Axle Volvo, Washroom, Live Tracking, Snacks",
        "stops": "1 Quick Refreshment Stop"
    }
}

# In-memory storage for booked passes
bookings_db = {}

def send_email_ticket(recipient_email, booking):
    try:
        sender_email = "jaikrishna4867@gmail.com"
        sender_password = "vtwnvxewbnranzxs"  # Generated App Password
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"CONFIRMED BUS PASS - {booking['pass_id']}"
        
        body = f"""
        ====================================================
                   CLOUD BUS PASS SYSTEM - TICKET
        ====================================================
        Pass ID: {booking['pass_id']}
        Passenger Name: {booking['passenger_name']}
        Tickets / Seats: {booking['seats']}
        Email: {booking['email']}
        ----------------------------------------------------
        Bus Service: {booking['bus_type']}
        From: {booking['source']} ({booking['boarding_point']})
        To: {booking['destination']}
        Travel Date: {booking['travel_date']}
        Estimated Duration: {booking['duration']}
        Route Stops: {booking['stops']}
        Washroom Facility: {booking['washroom']}
        Amenities: {booking['amenities']}
        ----------------------------------------------------
        Total Fare Paid: ₹{booking['total_price']}
        ====================================================
        Have a safe and comfortable journey!
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Using SMTP_SSL on Port 465 to bypass firewall blocks
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        print(f"Real email successfully sent via SSL to {recipient_email}")
    except Exception as e:
        print("Email sending error:", e)

@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        name = request.form.get("passenger_name", "").strip()
        email = request.form.get("email", "").strip()
        source = request.form.get("source", "").strip()
        destination = request.form.get("destination", "").strip()
        boarding_point = request.form.get("boarding_point", "").strip()
        bus_type = request.form.get("bus_type", "").strip()
        seats = request.form.get("seats", "1")
        travel_date = request.form.get("travel_date", "").strip()

        if not all([name, email, source, destination, boarding_point, bus_type, seats, travel_date]):
            error = "Please fill in all mandatory fields."
        elif source.lower() == destination.lower():
            error = "Boarding station and Drop station cannot be the same."
        else:
            try:
                date = datetime.strptime(travel_date, "%Y-%m-%d").date()
                if date < datetime.today().date():
                    error = "Travel date cannot be in the past."
                else:
                    bus_info = BUS_DETAILS.get(bus_type, {
                        "price": 500, "duration": "6h 00m", "washroom": "No ❌",
                        "amenities": "Standard Comfort", "stops": "Enroute Stops"
                    })
                    
                    num_seats = int(seats)
                    total_price = bus_info["price"] * num_seats
                    pass_id = "CBP-" + datetime.now().strftime("%y%m%d%H%M%S")

                    booking_data = {
                        "pass_id": pass_id,
                        "passenger_name": name,
                        "email": email,
                        "source": source,
                        "destination": destination,
                        "boarding_point": boarding_point,
                        "bus_type": bus_type,
                        "seats": num_seats,
                        "travel_date": date.strftime("%d %b %Y"),
                        "price_per_seat": bus_info["price"],
                        "total_price": total_price,
                        "duration": bus_info["duration"],
                        "washroom": bus_info["washroom"],
                        "amenities": bus_info["amenities"],
                        "stops": bus_info["stops"]
                    }

                    # Store in database
                    bookings_db[pass_id] = booking_data
                    
                    # Trigger real SSL email dispatch
                    send_email_ticket(email, booking_data)

                    # REDIRECT TO TICKET PAGE
                    return redirect(url_for('view_ticket', pass_id=pass_id))

            except ValueError:
                error = "Please provide a valid travel date."

    return render_template("index.html", error=error)

@app.route("/ticket/<pass_id>")
def view_ticket(pass_id):
    booking = bookings_db.get(pass_id)
    if not booking:
        return redirect(url_for('home'))
    return render_template("ticket.html", booking=booking)

if __name__ == "__main__":
    app.run(debug=True)