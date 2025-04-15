import streamlit as st
from datetime import datetime, timedelta
import json
import pandas as pd
import streamlit.components.v1
import base64

db_file = "bookings.json"
#image_folder = "uploaded_images"

with open(db_file, "r") as file:
    bookings = json.load(file)

st.title("Booking App")
st.markdown("---")

st.sidebar.header("TGA Booking")

selection = st.sidebar.radio("Request", 
                             ["Booking Calendar", "Book Apartment", 
                              "Check Previous Booking", "Download booking data"])

if selection == "Booking Calendar":
    st.info("Dates colored red have been booked")
    # Adjust end dates in the booking data
    for booking in bookings:
        booking["check_out"] = (datetime.strptime(booking["check_out"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    # Convert booking data into JSON-like structure for FullCalendar
    events = [
        {"title": booking["apartment"], "start": booking["check_in"], "end": booking["check_out"]}
        for booking in bookings
    ]

    # FullCalendar.js with selectable dates
    fullcalendar_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/locales-all.min.js"></script>
    <style>
        .fc-event-title {{
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
        }}
    </style>
    </head>
    <body>
    <div id="calendar"></div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {{
            initialView: 'dayGridMonth',
            selectable: true,
            events: {events},  // Inject event data
            eventColor: '#FF0000',  // Set event color to red
        }});
        calendar.render();
        }});
    </script>
    </body>
    </html>
    """

    # JavaScript and Python communication handler
    streamlit.components.v1.html(fullcalendar_code, height=500)

    # Button to show the booking record checker
    info_button = st.button("Check booking record")

    if info_button or "check_booking_triggered" in st.session_state:
        st.session_state.check_booking_triggered = True  # Persist state for this section
        
        # Inputs for booking record check
        check_in_date = st.date_input("Check-In date", key="check_in_date")
        apartment = st.selectbox(
            "Choose apartment",
            ["Upper floor", "Middle floor", "Ground floor"],
            key="apartment_choice"
        )

        # Button to trigger the check
        submit = st.button("Check", key="submit_check")

        if submit:
            # Check the booking record
            records = []
            for booking in bookings:
                if booking["check_in"] == check_in_date.isoformat() and booking["apartment"] == apartment:
                    records.append(booking)
                    break
            else:
                st.error(f"No booking is available for {apartment} on the selected date")

            # Display the result as a table
            if records:
                df = pd.DataFrame(records)
                # Render the table with images
                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                #st.table(df)


elif selection == "Book Apartment":
    st.subheader("Book Apartment")
    name = st.text_input("Name of the Customer")
    address = st.text_input("Address")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    apartment = st.selectbox("Choose apartment", 
                             ["Upper floor", "Middle floor", "Ground floor"])
    check_in = st.date_input("Check-In date")
    check_out = st.date_input("Check-Out date")
    #upload_image = st.file_uploader("Upload ID card", type=["JPG", "JPEG", "PNG"])

    submit = st.button("Book")

    if submit:
        # Validate if the booking dates overlap
        overlap = False
        for booking in bookings:
            if booking["apartment"] == apartment:
                existing_check_in = datetime.fromisoformat(booking["check_in"]).date()
                existing_check_out = datetime.fromisoformat(booking["check_out"]).date()
                
                # Check for overlap
                if (check_in <= existing_check_out and check_out >= existing_check_in):
                    overlap = True
                    break

        if overlap:
            st.error("This apartment is already booked for the selected dates. Please choose different dates.")
        else:
            # No overlap, proceed with booking

            # Save the uploaded image locally
            timestamp = datetime.now().strftime("%Y%m%d")
            #image_filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"            
            #image_html = f'<img src="data:image/jpeg;base64,{get_base64_encoded_image(image_filename)}" width="100" />'

            
            book_dict = {
                "name": name.title(),
                "address": address,
                "phone": phone,
                "email": email,
                "apartment": apartment,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "days": (check_out - check_in).days,
                "client_id": ""
            }

            bookings.append(book_dict)
            
            # Save bookings to the database file
            with open(db_file, "w") as file:
                json.dump(bookings, file, indent=4)

            st.success("Room has been booked successfully!!")
    
elif selection == "Check Previous Booking":
    st.subheader("Previous Booking")
    df = pd.DataFrame(bookings)
    # Render the table with images
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    #st.table(df)

elif selection == "Download booking data":
    with open(db_file, "r") as file:
        json_data = file.read()
    st.download_button("Download Booking Data", json_data, "bookings.json")
