import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import re


# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(layout="wide", page_title="NYC Airbnb Dashboard")

#get current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths to where you saved your figures
TIME_SERIES_DIR = os.path.join(CURRENT_DIR, "Time Series")
MAPS_DIR = os.path.join(CURRENT_DIR, "Maps")
HOOD_DIR = os.path.join(CURRENT_DIR, "Neighborhoods")
MODEL_DIR = os.path.join(CURRENT_DIR, "Modelling")
SUPPLY_DIR = os.path.join(CURRENT_DIR, "Supply") 

st.title("🗽 NYC Airbnb Market Analysis")
st.markdown("""
**Exploring the hidden drivers of value, risk, and experience in the New York City short-term rental market.**
*By Omarion, Anupam, Matthew & Elliott*
""")

# --- 2. HELPER FUNCTIONS ---

def display_html_file(file_path, height=600, width=None, scrolling=True, animation_duration=50):
    """
    Reads an HTML file (standard Plotly charts), strips internal height restrictions,
    and forces it to fill the Streamlit component area.
    """
    # 1. Path Verification
    if not os.path.exists(file_path):
        filename = os.path.basename(file_path)
        # Fallback search in common folders
        alt_paths = [
            os.path.join(CURRENT_DIR, filename), 
            os.path.join(TIME_SERIES_DIR, filename), 
            os.path.join(MAPS_DIR, filename),
            os.path.join(HOOD_DIR, filename),
            os.path.join(MODEL_DIR, filename),
        ]
        
        found = False
        for p in alt_paths:
            if os.path.exists(p):
                file_path = p
                found = True
                break
        
        if not found:
            st.warning(f"⚠️ Chart not found: `{filename}`")
            return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
            # 2. Animation Speed Logic
            if "animated" in file_path:
                match = re.search(r'Plotly\.newPlot\((.*)\);', html_content, re.DOTALL)
                if match:
                    # Regex to find the layout dict specifically containing updatemenus
                    layout_match = re.search(r'Plotly\.newPlot\([^,]+,\s*\[.*?\],\s*({.*"updatemenus":.*}),\s*{.*}\);', html_content, re.DOTALL)
                    if layout_match:
                        layout_str = layout_match.group(1)
                        try:
                            layout_json = json.loads(layout_str)
                            # Update Button Speed
                            layout_json['updatemenus'][0]['buttons'][0]['args'][1]['frame']['duration'] = animation_duration
                            layout_json['updatemenus'][0]['buttons'][0]['args'][1]['transition']['duration'] = 0
                            # Update Slider Speed
                            if 'sliders' in layout_json:
                                for step in layout_json['sliders'][0]['steps']:
                                    step['args'][1]['frame']['duration'] = animation_duration
                                    step['args'][1]['transition']['duration'] = 0
                            
                            html_content = html_content.replace(layout_str, json.dumps(layout_json))
                        except json.JSONDecodeError:
                            pass 

            # 3. FORCE RESPONSIVENESS (Restored from your original code)
            # Remove fixed height/width attributes from SVG tags so they can scale
            html_content = re.sub(r'(<svg[^>]*)\s+height="[^"]*"', r'\1', html_content)
            html_content = re.sub(r'(<svg[^>]*)\s+width="[^"]*"', r'\1', html_content)
            
            # Handle max-width logic safely for CSS string
            max_width_css = f"max-width: {width}px !important;" if width else "max-width: 100% !important;"

            # Inject CSS to force the plot to take up 100% of the iframe
            css_injection = f"""
            <style>
                html, body {{
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                /* Force the container div to fill the height */
                .main-svg, .plotly-graph-div {{
                    height: 100% !important;
                    width: 100% !important;
                    max-height: {height}px !important;
                    {max_width_css}
                }}
                /* Force the SVG to fill the height */
                svg {{
                    height: auto !important;
                    width: auto !important;
                    max-height: 100% !important;
                    max-width: 100% !important;
                }}
            </style>
            """
            
            # Inject CSS
            if "</head>" in html_content:
                full_html = html_content.replace("</head>", f"{css_injection}</head>")
            else:
                full_html = css_injection + html_content
            
            # 4. Render
            components.html(full_html, height=height, width=width, scrolling=scrolling)
            
    except Exception as e:
        st.error(f"Error reading file: {e}")

def display_html_map(file_path, height=600, width=None):
    """
    Specialized function for displaying Plotly HTML fragments (Maps).
    Wraps the raw DIV in a full HTML structure and enforces responsive sizing.
    """
    # 1. Path Verification
    if not os.path.exists(file_path):
        filename = os.path.basename(file_path)
        alt_paths = [
            os.path.join(CURRENT_DIR, "Maps", filename),
        ]
        found = False
        for p in alt_paths:
            if os.path.exists(p):
                file_path = p
                found = True
                break
        
        if not found:
            st.warning(f"⚠️ Map not found: `{filename}`")
            return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_fragment = f.read()

        # 2. REGEX CLEANUP
        # Strip inline style dimensions (e.g., style="height:450px;")
        import re
        html_fragment = re.sub(r'height:\s*[0-9]+px;?', '', html_fragment)
        html_fragment = re.sub(r'width:\s*[0-9]+px;?', '', html_fragment)
        
        # Also strip attribute dimensions just in case (e.g., height="450")
        html_fragment = re.sub(r'(<svg[^>]*)\s+height="[^"]*"', r'\1', html_fragment)
        html_fragment = re.sub(r'(<svg[^>]*)\s+width="[^"]*"', r'\1', html_fragment)

        # 3. ROBUST CSS WRAPPER (Aligned with display_html_file)
        max_width_css = f"max-width: {width}px !important;" if width else "max-width: 100% !important;"

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                html, body {{
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                /* Force the container div to fill the height, capped at the iframe height */
                .main-svg, .plotly-graph-div {{
                    height: 100% !important;
                    width: 100% !important;
                    max-height: {height}px !important;
                    {max_width_css}
                }}
                /* Ensure SVGs inside scale correctly */
                svg {{
                    height: auto !important;
                    width: auto !important;
                    max-height: 100% !important;
                    max-width: 100% !important;
                }}
            </style>
        </head>
        <body>
            {html_fragment}
        </body>
        </html>
        """

        # 4. RENDER
        # Width=None lets Streamlit handle the responsive column width
        components.html(full_html, height=height, width=width, scrolling=False)

    except Exception as e:
        st.error(f"Error reading map file: {e}")
        
# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to section:", 
    ["Review Trends", "Supply and Demand Dynamics", "Borough & Neighborhood Analysis", "Modelling"]
)

# --- 4. MAIN CONTENT ---

if page == "Review Trends":
    st.header("📈 Market Overview & Seasonality")
    
    st.subheader("Evolution of the NYC Market")
    st.markdown("Review volume over time, highlighting the 2020 pandemic shock and subsequent recovery.")
    
    # Animated Trend
    display_html_file(os.path.join(TIME_SERIES_DIR, "overall_review_trend_animated.html"), height=600, animation_duration=50)
    
    #Borough Trend
    st.subheader("Borough-Level Trends")
    st.markdown("Review volume trends for each NYC borough.")
    display_html_file(os.path.join(TIME_SERIES_DIR, "borough_review_trend.html"), height=600)
    
    #Top neighborhoods Trend
    st.subheader("Top Neighborhoods by Reviews")
    st.markdown("Review volume trends for the top 10 neighborhoods.")
    display_html_file(os.path.join(TIME_SERIES_DIR, "nbhd_review_trend.html"), height=600)

    st.subheader("Trend Decomposition")
    display_html_file(os.path.join(TIME_SERIES_DIR, "time_series_decomposition.html"), height=900)
    
    st.subheader("Seasonality Patterns")
    display_html_file(os.path.join(TIME_SERIES_DIR, "seasonality_monthly_boxplot.html"), height=500)
    
    st.subheader("Monthly Odds Ratios (OLS Model)")
    display_html_file(os.path.join(TIME_SERIES_DIR, "ols_monthly_odds_ratios.html"), height=500)
    
    # 1. Prepare Data Categorized by Section
    # We manually categorize based on the keywords in the label
    categories = {
        "General / Positive": [
            {"Topic Label": "-1_clean_comfortable_subway_close", "Count": 6699},
            {"Topic Label": "2_clean_responsive_comfortable_helpful", "Count": 737},
            {"Topic Label": "0_clean_comfortable_responsive_like", "Count": 224},
            {"Topic Label": "8_david_anthony_amy_comfortable", "Count": 56},
            {"Topic Label": "11_cat_cats_friendly_cute", "Count": 54}
        ],
        "Location Based (Transit & Neighborhoods)": [
            {"Topic Label": "7_williamsburg_restaurants_manhattan_bars", "Count": 129},
            {"Topic Label": "5_harlem_subway_close_central", "Count": 100},
            {"Topic Label": "1_brooklyn_subway_manhattan_close", "Count": 63},
            {"Topic Label": "10_jfk_airport_close jfk_jfk airport", "Count": 52}
        ],
        "Attractions & Lifestyle": [
            {"Topic Label": "4_hotel_staff_square_times square", "Count": 194},
            {"Topic Label": "13_beach_rockaway_close beach_boardwalk", "Count": 45},
            {"Topic Label": "12_ferry_staten_staten island_island", "Count": 41},
            {"Topic Label": "15_italy_chinatown_soho_chinatown italy", "Count": 37}
        ],
        "Complaints & Issues": [
            {"Topic Label": "3_did_didnt_refund_told", "Count": 149},
            {"Topic Label": "6_noise_loud_noisy_hear", "Count": 64}
        ]
    }

    # 2. Main Title
    st.subheader("🗂️ Topic Analysis by Category")
    st.caption("Deep dive into the 4 key drivers of guest reviews")

    # 3. Create Tabs for the 4 Sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "👍 General / Positive",
        "📍 Location Based",
        "🎡 Attractions",
        "⚠️ Complaints"
    ])

    # Helper function to display a dataframe within a tab
    def display_category(data_list):
        df = pd.DataFrame(data_list)
        st.dataframe(
            df,
            column_config={
                "Topic Label": st.column_config.TextColumn(
                    "Topic Cluster",
                    width="large"
                ),
                "Count": st.column_config.NumberColumn(
                    "Listings",
                    format="%d"
                )
            },
            hide_index=True,
            use_container_width=True
        )

    # 4. Populate Tabs
    with tab1:
        st.markdown("##### The 'Standard' Experience")
        st.info("These topics represent the baseline positive Airbnb experience (Clean, Comfortable, Responsive).")
        display_category(categories["General / Positive"])

    with tab2:
        st.markdown("##### Key Neighborhood Hubs")
        st.info("Clusters defined primarily by their proximity to transit or specific boroughs.")
        display_category(categories["Location Based (Transit & Neighborhoods)"])

    with tab3:
        st.markdown("##### Tourism & Vibes")
        st.info("Clusters centered around specific activities (Beaches, Ferries) or famous landmarks (Times Square).")
        display_category(categories["Attractions & Lifestyle"])

    with tab4:
        st.markdown("##### The Red Flags")
        st.warning("These topics define the 'Avoid' list—specifically Refunds and Noise issues.")
        display_category(categories["Complaints & Issues"])
    
elif page == "Supply and Demand Dynamics":
    st.header("🏘️ Supply and Demand Dynamics")
    st.subheader("Zombie Listings")
    st.markdown("Listings that remain active on the platform but receive zero reviews over a prolonged period.")
    st.image(os.path.join(SUPPLY_DIR, "zombie.png"), caption="Zombie Listings by Borough", width=800)
    
    st.subheader("Review Count vs Intensity")
    st.markdown("Which Borough gets more reviews per listing?")
    st.image(os.path.join(SUPPLY_DIR, "intensity.png"), caption="Review Count vs Intensity", width=800)
    
    st.subheader("Listing Growth vs Average Revenue Per Month")
    st.markdown("Analyzing how the growth in listing numbers correlates with average revenue per month across boroughs.")
    st.image(os.path.join(SUPPLY_DIR, "growth_rev.png"), caption="Listing Growth vs Average Revenue Per Month", width=500)
    
    st.subheader("Near Term Vacancy Rates")
    st.markdown("Which boroughs have the highest vacancy rates in the next 30 days?")
    st.image(os.path.join(SUPPLY_DIR, "vacancy.png"), caption="Near Term Vacancy Rates by Borough", width=800)
    
    st.subheader("Freshness of Listings")
    st.markdown("What percent of listings have their first review in the last 6 months?")
    st.image(os.path.join(SUPPLY_DIR, "freshness.png"), caption="Freshness of Listings by Borough", width=800)

elif page == "Borough & Neighborhood Analysis":
    st.header("🏙️ Borough & Neighborhood Analysis")
    st.subheader("Borough Pricing Dynamics")
    display_html_file(os.path.join(HOOD_DIR, "borough_value_map.html"), height=600)
    
    st.subheader("Safety")
    display_html_map(os.path.join(MAPS_DIR, "safety_map.html"))
    
    st.subheader("Pests")
    display_html_map(os.path.join(MAPS_DIR, "pest_heatmap.html"))
    
    st.subheader("Noise Levels")
    col1, col2 = st.columns([1,1])
    with col1:
        display_html_file(os.path.join(HOOD_DIR, "noise_scatter.html"), height=600)
    with col2:
        display_html_file(os.path.join(HOOD_DIR, "noise_table.html"), height=600)
        
    st.subheader("Proximity to Attractions")
    st.markdown("How price and ratings vary with distance to Times Square and Central Park.")
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("**Proximity**")
        display_html_file(os.path.join(HOOD_DIR, "luxury_premium_scatter.html"), height=800)
    with col2:
        st.markdown("**Rating**")
        display_html_file(os.path.join(HOOD_DIR, "rating_distance_scatter.html"), height=800)   
        
    st.subheader("Trending Neighborhoods")
    st.markdown("Scored by **Momentum** which is defined as the rate of reviews in the last 30 days, over their long term monthly average. Adjusted to city median.")
    display_html_file(os.path.join(HOOD_DIR, "hot_list.html"), height=600)
    display_html_file(os.path.join(HOOD_DIR, "cold_list.html"), height=600)
    
        
    st.header("The Rise of Corporate Hosts")
    st.markdown("Mapping the concentration of corporate-owned listings across NYC neighborhoods. Corporate hosts are defined by having a high 'Empire Score'.")
    st.markdown("**Empire Score** = Log(Listings) + Superhost Status + Instant Book")
    st.subheader("Corporate Host Map")
    display_html_map(os.path.join(MAPS_DIR, "corporate_invasion_map.html"), height=600)
    st.subheader("Host Composition by Borough")
    st.markdown("Percentage of listings by host type across boroughs.")
    display_html_file(os.path.join(HOOD_DIR, "host_composition.html"), height=600)
    st.subheader("Scam Risk by Host Tier")
    st.markdown("Percentage of listings with mentions of 'scam' in reviews, segmented by host tier.")
    display_html_file(os.path.join(HOOD_DIR, "scam_risk_host_tier.html"), height=500)
    

elif page == "Modelling":
    st.header("Predictive Modelling")
    st.subheader("Price & Last 365 Day Revenue Prediction Models")
    st.markdown("Explore our XGBoost regression models designed to predict listing prices and annual revenue based on key features.")
    
    st.markdown("""
    **Feature Summary**

    **Numeric Features**  
    - **Physical Attributes (e.g., beds & baths):** 'minimum_nights', 'maximum_nights', 'bedrooms', 'beds', 'bathrooms', 'accommodates', 'availability_90'  
    - **Review-Based Metrics:** 'review_score_composite', 'number_of_reviews'  
    - **Sentiment-Driven Scores (derived from NLP using VADER sentiment analysis):** 'amenity_score', 'empire_score', 'booking_momentum', 'Loc_Subway_score', 'Loc_Safety_score', 'Noise_External_score', 'Noise_Internal_score', 'Prop_Cleanliness_score', 'Host_Service_score'  

    We selected numeric features based on domain logic and which features we expected to influence price or revenue.

    **Categorical Variables**  
    - 'room_type'  
    - 'property_type'  
    - 'Neighbourhood_cleansed'  
    - 'Neighbourhood_group_cleansed'  

    These were later one-hot encoded by the model pipeline.  

    **Flag Variables (Binary Indicators)**  
    - 'has_dealbreaker'  
    - 'Risk_Pests_neg_flag'  
    - 'Risk_Scam_neg_flag'  
    - 'is_superhost'  
    - 'is_instant'  
    - 'is_licensed'  

    These add important sentiment-driven signals and indicators of trust and convenience that visitors can see regarding the host on the platform.
    """)
    
    st.subheader("Price Prediction Model Performance")
    st.markdown("R² score of .785, a MAE of \$56 and a RSME of \$117 on the test set.")
    #Display PNG File of SHAP Plots
    st.image(os.path.join(MODEL_DIR, "SHAP Price.png"), caption="SHAP Plot for Price Prediction Model",width=800)
    st.markdown("""
    **SHAP Plot Summary**   
    Targets listing price. The most impactful variables are the Manhattan neighborhood group, minimum nights, accommodates and private room type.
    """)
    
    st.subheader("Revenue Prediction Model Performance")
    st.markdown("R² of .724, a MAE of \$6,949 and a RMSE of \$16,339 on the test set.")
    st.image(os.path.join(MODEL_DIR, "SHAP Revenue.png"), caption="SHAP Plot for Revenue Prediction Model", width=800)
    st.markdown("""
    **SHAP Plot Summary**   
    Targets last 365-day revenue. The most impactful variables are Host Service Score, composite review score and cleanliness score.
    """)
    