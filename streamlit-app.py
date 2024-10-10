import streamlit as st
import time
import requests
from PIL import Image
from io import BytesIO

import sys
sys.path.append('./ML_server')
import ml_server

def main():
    # Simulated function to fetch product details (replace with real API logic)
    def fetch_product_details(product_url):
        result = ml_server.process_request(product_url)
        product_info = {
            "product_name": result["product"],
            "price": result["price"],
            "image_url": "image.jpg",
            "review": result["summary"],
            "pros": result["pros"],
            "cons": result["cons"],
            "rating": result["avg_rating"]  # Example rating (out of 5)
        }
        return product_info

    # Function to generate star ratings with half-star using CSS
    def display_star_rating(rating):
        full_stars = int(rating)
        half_star = (rating - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)

        # Create full stars, half star, and empty stars
        star_html = '<span class="star full">★</span>' * full_stars
        if half_star:
            star_html += '<span class="star half">★</span>'
        star_html += '<span class="star empty">★</span>' * empty_stars

        # Return stars and decimal rating
        return f'<div class="star-container">{star_html}<span class="rating-text">({rating:.1f})</span></div>'

    # Title and page setup
    st.set_page_config(page_title="Product Insights", page_icon=":mag:", layout="centered")
    st.markdown('<h1 style="text-align: center; animation: fadeIn 1.5s;">🔍 Product Insights</h1>', unsafe_allow_html=True)
    st.write('<p style="text-align: center; animation: fadeInUp 1.5s;">Get detailed insights into any product instantly by entering the product URL below.</p>', unsafe_allow_html=True)

    # Input for product URL
    product_url = st.text_input("Enter Product URL", "")

    # Button to trigger the analysis
    if st.button("Get Insights"):
        if product_url:
            # Progress bar with percentage
            with st.spinner('Fetching product details...'):
                progress_bar = st.progress(0)
                status_text = st.empty()
                for percent_complete in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(percent_complete + 1)
                    status_text.text(f"Loading... {percent_complete + 1}%")

            # Fetch product details (replace this with real logic to scrape/analyze product)
            product_info = fetch_product_details(product_url)

            # Display product name and "Insights" above the image
            st.markdown(f'<h2 style="text-align: center; animation: fadeIn 2s;">Insights: {product_info["product_name"]}</h2>', unsafe_allow_html=True)

            # Display product image with hover effect (with smaller size)
            st.image(product_info['image_url'], caption="Product Image", use_column_width=False, width=300)

            # Display product price after the image
            st.markdown(f'<h3 style="text-align: center; animation: fadeIn 2s;">Price: {product_info["price"]}</h3>', unsafe_allow_html=True)

            # Display review with animation
            st.markdown('<h2 style="text-align: center; animation: fadeIn 2s;">Product Review</h2>', unsafe_allow_html=True)
            st.write(f'<div style="animation: fadeInUp 2s;">{product_info["review"]}</div>', unsafe_allow_html=True)

            # Display product rating as stars and decimal number
            st.markdown('<h3 style="text-align: center; animation: fadeIn 1.5s;">Product Rating</h3>', unsafe_allow_html=True)
            st.write(display_star_rating(product_info['rating']), unsafe_allow_html=True)

            # Display Pros and Cons with styled columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<h3 style="animation: fadeInLeft 1s;">Pros ✅</h3>', unsafe_allow_html=True)
                st.write(f'<ul style="animation: fadeInLeft 1.5s;">{"".join([f"<li>{pro}</li>" for pro in product_info["pros"]])}</ul>', unsafe_allow_html=True)

            with col2:
                st.markdown('<h3 style="animation: fadeInRight 1s;">Cons ❌</h3>', unsafe_allow_html=True)
                st.write(f'<ul style="animation: fadeInRight 1.5s;">{"".join([f"<li>{con}</li>" for con in product_info["cons"]])}</ul>', unsafe_allow_html=True)

        else:
            st.error("Please enter a valid product URL.")

    # Enhanced Styling and Visual Effects
    st.markdown("""
        <style>
            /* Button Animation */
            .stButton button {
                background-color: #4CAF50;
                color: white;
                padding: 15px 32px;
                font-size: 16px;
                margin: 10px 2px;
                border: none;
                transition: 0.4s;
                border-radius: 12px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
            }

            .stButton button:hover {
                background-color: #45a049;
                box-shadow: 0px 6px 8px rgba(0, 0, 0, 0.3);
            }

            /* Progress bar color */
            .stProgress .st-bo {
                background-color: #4CAF50;
            }

            /* Image Hover Effect */
            .stImage img {
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                transition: 0.3s ease-in-out;
            }

            .stImage img:hover {
                transform: scale(1.05);
            }

            /* Star Rating Styling */
            .star-container {
                display: inline-block;
                font-size: 24px;
                position: relative;
                margin-bottom: 10px;
            }
            .star {
                color: #FFD700;
                font-size: 30px;
                display: inline-block;
                position: relative;
            }
            .half {
                background: linear-gradient(90deg, #FFD700 50%, #ddd 50%);
                -webkit-background-clip: text;
                color: transparent;
                display: inline-block;
            }
            .full, .empty {
                color: #FFD700;
            }
            .empty {
                color: #ddd;
            }
            .rating-text {
                font-size: 20px;
                padding-left: 10px;
            }

            /* Text animations */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes fadeInUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            @keyframes fadeInLeft {
                from { transform: translateX(-20px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }

            @keyframes fadeInRight {
                from { transform: translateX(20px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }

            /* Center Text */
            h1, h2, h3 {
                text-align: center;
            }

            ul {
                list-style-type: none;
                padding: 0;
            }

            li {
                padding: 5px 0;
            }
        </style>
    """, unsafe_allow_html=True)

# Ensuring proper use of multiprocessing in Windows
if __name__ == "__main__":
    main()
