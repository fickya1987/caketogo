import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
from streamlit_option_menu import option_menu
from streamlit_star_rating import st_star_rating
from functions import (contact_email, add_row, generate_row,
                       customer_email, rating_stars, create_post, pdf_file,
                       valid_email, valid_postalcode)
from PIL import Image
from datetime import datetime, timedelta
import re
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# use image logo as header of website
header_image = Image.open("images/caketogo.png")
st.image(header_image, use_column_width=True)

# option_menu is the navigation bar that has all the "pages" of the website (About, Contact, Menu etc)
# if selected == "page" goes to that specific page
selected = option_menu(

    menu_title=None,
    options=["About", "Contact", "Menu", "Order", "Reviews"],
    icons=["heart", "envelope", "book", "calendar", "star"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5!important", "background-color": "#DDBDD5"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#DDBDD5"},
    }

)

if selected == "About":
    # region About
    col1, col2 = st.columns(2)

    with col1:
        st.image("images/about.jpg")

    with col2:
        st.markdown("<h1 style='text-align: center; '>Our Story</h1>", unsafe_allow_html=True)
        content = '''
            **Cake On The Go was conceptualized by Jason GokHo Ing after studying abroad in the 
            dessert capital of the world - France. While attending her lectures, Jason became enamored by the 
            quality of Paris' home made pastries. 
            The complex flavor pallet and intricate designs of the French was unlike anything he had seen before. 
            It was the yearning to share these French delicacies with his friends and family that inspired 
            Jason to start his very own custom cake delivery service.**
            '''
        st.write(content)

    # endregion

if selected == "Contact":

    # region Contact
    col3, col4 = st.columns([1.5, 1.5])
    with col3:
        st.markdown("<h1 style='text-align: center; '>Contact Us</h1>", unsafe_allow_html=True)

        contact_us = '''
        
        1190 Victoria Dr, Vancouver, BC V5L 4G5 :house:\
        
        Email: cakeonthego@gmail.com :email:\
        
        Phone: 123-456-7890 :phone:\
        
        For custom cake orders please fill out the form below: :clipboard: '''

        st.write(contact_us)
        # form that asks for customer email and message

        user_email = st.text_input('**Your email address:**', key='user_email')

        if user_email and not valid_email(user_email):
            st.warning("Must be a valid email")

        user_message = st.text_area('**Please enter your message below:**')
        message = f""" Subject: New email from {user_email} \n
        From: {user_email}
    
        {user_message} 
        """

        if not (user_email and user_message):
            st.warning("*All required fields need to be filled to submit the form.")

        submit_button = st.button(label='Submit', disabled=not (user_email and user_message))

        # The code below should be indented inside the form context manager
        if submit_button:
            if user_email and user_message:
                contact_email(message)
                st.info("Your email was sent successfully")

    with col4:
        st.image("images/contact_cake.jpg", width=400)
    # endregion

if selected == "Menu":
    st.markdown("<h1 style='text-align: center; '>Our Menu</h1>", unsafe_allow_html=True)

    head_col1, head_col2, head_col3 = st.columns([2, 6, 2])

    with head_col2:
        st.markdown("<h2 style='text-align: center; '> Small is  $25, Medium is $45, and Large is $55</h2>",
                    unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; '> All our cakes come with Vanilla Meringue Icing</h4>",
                    unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; '> Add one of our signature fillings for $5: \n\n"
                    "(Fruit Compote, Chocolate Ganache, Matcha, Fresh Fruit, Caramel, Oreo)</h4>",
                    unsafe_allow_html=True)

    st.markdown('---')

    col1, col2, col3, col4 = st.columns([1.0, 1.0, 1.45, 1.0])
    with col1:
        # import data from cakes.csv file to form menu
        df = pd.read_csv("cakes.csv")
        for index, entry in df[0:2].iterrows():
            st.subheader(entry["cake"])
            st.write(entry["description"])
    with col2:
        for index, entry in df[0:2].iterrows():
            st.image("images/" + entry["image"], width=200)
    with col3:
        for index, entry in df[2:4].iterrows():
            st.subheader(entry["cake"])
            st.write(entry["description"])

    with col4:
        for index, entry in df[2:4].iterrows():
            st.image("images/" + entry["image"], width=200)

if selected == "Order":

    st.success("Cake On The Go delivers within the Metro Vancouver Area. All Order requests are subject of approval")

    tab1, tab2, tab3 = st.columns([1.8, 0.3, 3.5])
    # tab1 contains customer order form  where it gathers input data (first_name, last_name)
    with tab1:
        st.markdown("<h1 style='text-align: center;'>Customer Info</h1>", unsafe_allow_html=True)

        st.write("Let's start with the basic details.")

        name_cols = st.columns(2)

        with name_cols[0]:
            cust_firstname = st.text_input(label='*Customer Name', placeholder='First Name', key="first_name")
        with name_cols[1]:
            cust_last_name = st.text_input(label='*Last Name', placeholder='Last Name', key="last_name")

        cust_email = st.text_input(label='*Customer Email', placeholder='Your Email', key='email')
        # makes sure e-mail is valid
        email_pattern = r"[^@]+@[^@]+\.[^@]+"
        if cust_email and not valid_email(cust_email):
            st.warning("Must be a valid email")

        st.write("Enter the address you would like us to **deliver** to:")

        address_cols = st.columns([8, 3])
        with address_cols[0]:
            delivery_address = st.text_input(label='*Address', key='address',
                                             placeholder='8888 University Dr W, Burnaby')

        with address_cols[1]:
            postal = st.text_input(label='*Postal Code', key='postal code', placeholder='V5A-1S6')
            postal = postal.upper()
        if postal and not valid_postalcode(postal):
            st.warning("*Invalid Postal Code")

        st.markdown('---')
        st.write("Enter your payment details below")
        credit_card = st.text_input(label='*Credit Card', placeholder='Credit Card', key="credit_card")

        exp_cols = st.columns([5, 5, 3, 2, 2])
        # creates a selection of dates and times from today
        now = datetime.now()
        with exp_cols[0]:
            rng_month = pd.date_range(pd.Timestamp(now), periods=12, freq='M')
            expiry_month = st.selectbox(label='*Expiry Month', options=rng_month.strftime("%b"))

        with exp_cols[1]:

            rng_year = pd.date_range(pd.Timestamp(now), periods=12, freq='Y')
            expiry_year = st.selectbox(label='*Expiry Year', options=rng_year.strftime("%Y"))

        with exp_cols[2]:
            cvv = st.text_input(label='*CVV', placeholder='CVV', max_chars=3)
            cvv_pattern = re.compile("[0-9][0-9][0-9]")
            valid_cvv = re.match(cvv_pattern, cvv)
        if not valid_cvv and len(cvv) != 0:
            st.warning("*Invalid CVV")

        with exp_cols[3]:
            st.write("")
            st.write("")
            st.image('images/visa.png')

        with exp_cols[4]:
            st.write("")
            st.write("")
            st.image('images/mastercard.png')

        st.write("**All orders must be made 7 days in advance**")
        date_cols = st.columns(2)
        with date_cols[0]:
            seven_days = datetime.today() + timedelta(days=7)
            max_days = datetime.today() + timedelta(days=50)
            delivery_date = st.date_input('*Delivery Date', value=seven_days, min_value=seven_days, max_value=max_days)
        with date_cols[1]:
            time_range = pd.date_range(pd.Timestamp("9:00"), periods=10, freq='H')
            time_range = time_range.strftime('%I:%M%p')

            delivery_time = st.selectbox('*Delivery Time', options=time_range)

    with tab3:
        st.markdown("<h1 style='text-align: center;'>Order Form</h1>", unsafe_allow_html=True)
        st.image("images/cake_gallery.png")
        st.markdown("##### Click 'Add' to get started on your online order!")
        col3, col4, = st.columns([2.5, 1.85])

        # session state refers to when page is being used (session)
        # during sessions, variables can be and are shared with one another (generate_row, add_row, remove_row)
        # checks to see if rows does not already exist in the session
        if "rows" not in st.session_state:
            st.session_state["rows"] = [0]

        # rows_collection is a variable that holds the data by generate_row
        rows_collection = []

        # for loop is executed when the "Add Item" button is clicked
        # used to generate the unique_id and rows

        for entry in st.session_state["rows"]:
            # generate the data via the generate_row function
            # data generated and stored in a variable called row_data
            row_data = generate_row(entry)
            # adds the data from the generated row function to the row_collection
            rows_collection.append(row_data)

        # have a button that when clicked calls the add_row function
        st.button(label="Add", on_click=add_row)

        # construct a data frame based on the rows collected and the unique_id
        data = pd.DataFrame(rows_collection)
        # calculate order total from data['total']

        # calculate the order_total, taxes, and grand_total of items
        order_total = float(data['total'].sum())
        # calculate taxes
        taxes = order_total * 0.12
        grand_total = order_total + taxes

        col1, col2, col3 = st.columns([10, 4.75, 3])
        with col2:
            # headings to show what the values mean
            st.markdown("##### Order Total: ")
            st.markdown("##### Taxes: ")
            st.subheader(f"Grand Total: ")
        with col3:
            # using rounding functions to make currency appear more neat
            st.markdown(f"#####   ${'%.2f' % round(order_total, 2)}")
            st.markdown(f"##### + ${'%.2f' % round(taxes, 2)}")
            st.subheader(f"   ${'%.2f' % round(grand_total, 2)}")
        st.markdown('----')

    st.markdown('----')

    # gives options for customers to add photos or additional comments
    uploaded_file = st.file_uploader("Have an idea for a cake design? Submit your image here! "
                                     "(Must be in png, jpg or jpeg format)", type=['png', 'jpg'],
                                     accept_multiple_files=True)

    add_message = st.text_area(label="Please feel free to include any other additional requests here:")

    footer_col1, footer_col2, footer_col3 = st.columns([10, 8.0, 3.0])

    with footer_col2:
        # warns customers that a required field has not been filled
        if not any(cust_firstname and cust_last_name and cust_email and delivery_address and postal
                   and credit_card and cvv and expiry_year and expiry_month):
            st.warning("*all required fields need to be filled to submit an order")

    with footer_col3:
        # will not let customer submit unless all required fields are filled out
        submit_order = st.button("Submit", disabled=not any(cust_firstname and cust_last_name and cust_email and postal
                                                            and delivery_address and credit_card and cvv
                                                            and expiry_year and expiry_month))
    # means the order has been submitted
    if submit_order:
        # creates an invoice number based on the exact time
        invoice_nr = datetime.now().strftime("%Y%m%d%H%M%S")
        filter_cols = row_data

        # generate csv file into the csv/ folder of Cake On The Go server
        csv = 'csv/' + f'{invoice_nr}{cust_firstname[:1]}{cust_last_name}.csv'
        data.to_csv(csv, columns=filter_cols, index=True)

        # pop up window that notifies customer of order status
        streamlit_js_eval(js_expressions="alert('Your order request has been successfully processed. You "
                                         "will receive an email shortly with more details regarding your order"
                                         " Please press the ok button to exit the order form ')")

        # reloads page and restarts session state
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

        # gather customer input to create pdf file
        pdf_file(csv, cust_firstname, cust_last_name,
                 delivery_time, delivery_date, delivery_address, postal,
                 invoice_nr, order_total, grand_total, taxes)

        # function that sends customer invoice
        customer_email(cust_firstname, cust_last_name, delivery_time, delivery_date, postal,
                       delivery_address, cust_email, invoice_nr)

if selected == "Reviews":

    # checks to see if existing_reviews is already established in session_state
    if 'existing_reviews' not in st.session_state:
        # Load existing reviews from the CSV file if it exists, or initialize as an empty DataFrame
        try:
            st.session_state['existing_reviews'] = pd.read_csv("reviews.csv").to_dict(orient="records")
        except FileNotFoundError:
            st.session_state['existing_reviews'] = []

    st.title('Cake On The Go Review Page')
    st.write('Welcome to our review page! Please leave your feedback about our cakes below:')

    # asks customer for their rating, username, comments they may have, and image of cake
    rating = st_star_rating(label="Rate our cakes:", size=40, read_only=False, maxValue=5, defaultValue=0)

    username = st.text_input("Please enter your name:")

    review_text = st.text_area("Write your review here:")

    image_files = st.file_uploader("Show off your :cake:", type=["jpg", "jpeg", "png"])

    # warns customers that a required field has not been filled
    if not (rating and review_text and username):
        st.warning("*Please enter a rating, a short description, and your name")

    # submit review has been pressed
    if st.button('Submit Review', disabled=not (rating and review_text and username)):
        st.write("Thank you. Your review has been successfully posted!")
        # create_posts insert new review into the existing_reviews
        new_review = create_post(username, review_text, rating, image_files)
        # Insert new_review to the top of existing_reviews
        st.session_state['existing_reviews'].insert(0, new_review)

        # Convert the list of dictionaries to a DataFrame
        df_reviews = pd.DataFrame(st.session_state['existing_reviews'])
        # Write the DataFrame to reviews.csv to save changes
        df_reviews.to_csv("reviews.csv", index=False)

    st.header("Existing Reviews")
    # prints out existing_reviews to be viewed by customers
    rev_col1, rev_col2 = st.columns([3, 5])

    with rev_col1:
        if len(st.session_state['existing_reviews']) > 0:
            for review in st.session_state['existing_reviews']:
                # check to see if username and rating exist
                username = review['username']
                rating = int(review['rating'])
                st.subheader(f"{username} {rating_stars(rating)}")
                st.write(review['review_text'])

                # Check if 'image_path' exists and is not NaN
                if "image_path" in review and isinstance(review['image_path'], str):
                    if os.path.exists(review['image_path']):
                        st.image(review['image_path'], use_column_width=True)
        st.write("---")

        # reads file of updated reviews
        # converts to json via streamlit

        with open("reviews.csv", "r") as file:
            loaded_data = pd.read_csv(file)
        # below code is for testing purposes
        # st.json(loaded_data.to_dict(orient="records"))
