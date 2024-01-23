import smtplib
import ssl
import time
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from fpdf import FPDF
import pandas as pd
import re


def valid_email(email):
    # Use regular expression to check for a valid email format
    # r used to take string ^@ ensures that all characters are allowed
    # except @. \. means that a '.' is needed
    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    return bool(re.match(email_pattern, email))


# function used on contact page. connects to Google server
def contact_email(message):
    host = "smtp.gmail.com"
    port = 465
    username = "testingpythonapp@gmail.com"
    password = os.getenv("PASSWORD")
    receiver = "testingpythonapp@gmail.com"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)


# function that emails customer invoice
def customer_email(cust_firstname, cust_last_name, delivery_time, delivery_date,
                   delivery_address, postal, cust_email, invoice_nr):
    customer_message = f""" Cake To Go Order #{invoice_nr} \n

    This email is for: {cust_firstname} {cust_last_name},

    Your order has been processed and will be delivered to {delivery_address}, {postal}
    on {delivery_date} at {delivery_time}.
    
    We have attached an invoice of your order to this email.

    Thank you,

    Cake To Go
    """

    host = "smtp.gmail.com"
    port = 465
    username = "testingpythonapp@gmail.com"
    password = os.getenv("PASSWORD")
    context = ssl.create_default_context()

    receiver = 'Cake To Go'

    message = MIMEMultipart()
    message['From'] = username
    message['To'] = receiver
    message['Subject'] = f'Cake To Go Invoice #{invoice_nr}'

    message.attach(MIMEText(customer_message, 'plain'))

    pdf = f'PDFs/{invoice_nr}{cust_firstname[:1]}{cust_last_name}.pdf'

    binary_pdf = open(pdf, 'rb')

    payload = MIMEBase('application', 'octate-stream', Name=pdf)
    payload.set_payload(binary_pdf.read())

    encoders.encode_base64(payload)

    payload.add_header('Content-Decomposition', 'attachment', filename=pdf)
    message.attach(payload)

    text = message.as_string()

    time.sleep(5)

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, cust_email, text)


# giving a Unique row_id starting at 0
unique_id = 0


def add_row():
    # a new row is added and a unique_id is provided
    global unique_id
    unique_id = unique_id + 1
    st.session_state["rows"].append(str(unique_id))


def remove_row(row_id):
    # when remove_row is clicked the row deletes the row with the same unique_id
    st.session_state["rows"].remove(str(row_id))


def generate_row(row_id):
    # always have the row container empty
    row_container = st.empty()
    # user select components to add on generation of row
    row_columns = row_container.columns((1.75, 1.75, 2.5, 1.5, 1, 0.3))
    # these are the columns for the cake options (flavor, size, filling etc)
    row_cake = row_columns[0].selectbox("Cake", key=f"cake_{row_id}",
                                        options=("Red Velvet", "Chocolate", "Carrot", "Vanilla"))

    row_size = row_columns[1].selectbox("Size", key=f"size_{row_id}",
                                        options=("Small", "Medium", "Large"))

    row_fill = row_columns[2].selectbox("Filling", key=f"filling_{row_id}",
                                        options=("No Filling", "Fruit Compote", "Chocolate Ganache",
                                                 "Matcha", "Fresh Fruit", "Caramel", "Oreo"))
    row_qty = row_columns[3].number_input("Quantity",
                                          step=1, key=f"qty_{row_id}", min_value=1, max_value=5)

    size_total = 0
    # if function used to match the size to the pricing
    if row_size == "Small":
        size_total = 25
    if row_size == "Medium":
        size_total = 45
    if row_size == "Large":
        size_total = 55

    if row_fill == "No Filling":
        fill_total = 0
    else:
        fill_total = 5
    # calculate the total price
    total_bef = (size_total + fill_total) * row_qty

    row_total = row_columns[4].text_input("Total", key=f"total_{row_id}", disabled=True,
                                          value=total_bef)

    # button used to delete column by its unique row_id
    row_columns[5].button("❌", key=f"del_{row_id}", on_click=remove_row, args=[row_id])

    # returns inputs to generate order row
    return {"cake": row_cake, "filling": row_fill, "size": row_size, "qty": row_qty,
            "total": int(row_total)}


# checks if postal code is valid
def valid_postalcode(postal):
    postal_pattern = r"^[a-zA-Z]\d[a-zA-Z][\s,-]\d[a-zA-Z]\d$"
    return bool(re.match(postal_pattern, postal))


# collects user data to post review
def create_post(username, review_text, rating, image_files):
    new_review = {
        "username": username,
        "review_text": review_text,
        "rating": rating,
    }
    if image_files is not None:
        # Save the uploaded image and store its path
        image_path = f"images/{image_files.name}"
        new_review['image_path'] = image_path
        # write image to images/ folder then open it to display
        with open(image_path, "wb") as file:
            file.write(image_files.getvalue())
    return new_review


# multiplies rating to return number of stars
def rating_stars(rating):
    star_icon = "⭐" * rating
    return star_icon


# function used to format the pdf file
def pdf_file(csv, cust_firstname, cust_last_name,
             delivery_time, delivery_date, delivery_address, postal,
             invoice_nr, order_total, grand_total, taxes):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font(family="Times", size=20, style="B")
    pdf.cell(w=50, h=8, txt=f"Invoice Number: {invoice_nr}", ln=1)

    pdf.set_font(family="Times", size=10)
    pdf.cell(w=50, h=8, txt=f"Customer name: {cust_firstname} {cust_last_name}", ln=1)
    pdf.cell(w=50, h=8, txt=f"Delivery Date: {delivery_date}", ln=1)
    pdf.cell(w=50, h=8, txt=f"Delivery Time: {delivery_time}", ln=1)

    pdf.cell(w=50, h=8, txt=f"Delivered To:{delivery_address} {postal}", ln=1)

    df = pd.read_csv(csv)

    header = ['order#', 'item name', "filling", "size", "qty", "total"]
    header = [items.title() for items in header]
    pdf.set_font(family="Times", size=10, style='B')
    pdf.cell(w=20, h=6, txt=header[0], border=1)
    pdf.cell(w=30, h=6, txt=header[1], border=1)
    pdf.cell(w=30, h=6, txt=header[2], border=1)
    pdf.cell(w=50, h=6, txt=header[3], border=1)
    pdf.cell(w=30, h=6, txt=header[4], border=1)
    pdf.cell(w=30, h=6, txt=header[5], border=1, ln=1)

    for index, rows in df.iterrows():
        pdf.set_font(family="Times", size=10)
        pdf.cell(w=20, h=6, txt=str(rows[0] + 1), border=1)
        pdf.cell(w=30, h=6, txt=str(rows[1]), border=1)
        pdf.cell(w=30, h=6, txt=str(rows[2]), border=1)
        pdf.cell(w=50, h=6, txt=str(rows[3]), border=1)
        pdf.cell(w=30, h=6, txt=str(rows[4]), border=1)
        pdf.cell(w=30, h=6, txt=str(f'${rows[5]}'), border=1, ln=1)

    pdf.ln(10)
    taxes = '%.2f' % round(taxes, 2)
    order_total = '%.2f' % round(order_total, 2)
    grand_total = '%.2f' % round(grand_total, 2)
    pdf.set_font(family="Times", size=10, style="B")
    pdf.cell(w=50, h=8, txt=str(f'Total: ${order_total}'), ln=1)
    pdf.cell(w=50, h=8, txt=str(f'Taxes: ${taxes}'), ln=1)
    pdf.cell(w=50, h=8, txt=f'The total price is ${grand_total}', ln=1)

    pdf.output(f'PDFs/{invoice_nr}{cust_firstname[:1]}{cust_last_name}.pdf')
