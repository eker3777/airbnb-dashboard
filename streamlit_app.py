import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(layout="wide", page_title="NYC Airbnb Dashboard")

# Define paths to where you saved your figures
# Adjust these paths if your notebook saved them elsewhere!
TIME_SERIES_DIR = "Time Series"
MAPS_DIR = "Maps"

st.title("🗽 NYC Airbnb Market Analysis")
st.markdown("""
**Exploring the hidden drivers of value, risk, and experience in the New York City short-term rental market.**
*By the Data Science Team*
""")

# --- 2. HELPER FUNCTIONS ---
def display_html_file(file_path, height=600, width=1000, scrolling=False, animation_duration=50):
    """Reads an HTML file and displays it in the Streamlit app with robust error handling and responsiveness."""
    if not os.path.exists(file_path):
        # Try looking in the root or other common folders if not found
        filename = os.path.basename(file_path)
        alt_paths = [filename, os.path.join("Figs", filename), os.path.join("Time Series", filename)]
        found = False
        for p in alt_paths:
            if os.path.exists(p):
                file_path = p
                found = True
                break
        
        if not found:
            st.warning(f"⚠️ Plot not found: `{filename}`. Please ensure it is saved in the directory.")
            return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
            import re
            import json
            
            # Fix animation speed for specific charts
            if "animated" in file_path:
                # Robustly find and modify the Plotly animation settings
                match = re.search(r'Plotly\.newPlot\((.*)\);', html_content, re.DOTALL)
                if match:
                    # Extract the arguments string (div, data, layout, config)
                    args_str = match.group(1)
                    # Find the layout JSON object specifically
                    # It's the third argument, starting with '{' and containing 'updatemenus'
                    layout_match = re.search(r'Plotly\.newPlot\([^,]+,\s*\[.*?\],\s*({.*"updatemenus":.*}),\s*{.*}\);', html_content, re.DOTALL)
                    if layout_match:
                        layout_str = layout_match.group(1)
                        layout_json = json.loads(layout_str)

                        # 1. Modify the PLAY BUTTON speed (for manual play)
                        layout_json['updatemenus'][0]['buttons'][0]['args'][1]['frame']['duration'] = animation_duration
                        layout_json['updatemenus'][0]['buttons'][0]['args'][1]['transition']['duration'] = 0

                        # 2. Modify the SLIDER steps speed (for autoplay)
                        for step in layout_json['sliders'][0]['steps']:
                            step['args'][1]['frame']['duration'] = animation_duration
                            step['args'][1]['transition']['duration'] = 0

                        # Replace the old layout with the modified one
                        html_content = html_content.replace(layout_str, json.dumps(layout_json))

            # Make the chart responsive by removing fixed dimensions and adding scaling CSS
            # Remove fixed height/width from SVG tags
            html_content = re.sub(r'(<svg[^>]*)\s+height="[^"]*"', r'\1', html_content)
            html_content = re.sub(r'(<svg[^>]*)\s+width="[^"]*"', r'\1', html_content)
            
            # Inject CSS to force full responsiveness and scaling
            css_injection = f"""
            <style>
                html, body {{
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                .main-svg, .plotly-graph-div {{
                    height: 100% !important;
                    width: 100% !important;
                    max-height: {height}px !important;  /* Cap at container height */
                    max-width: {width}px !important;    /* Cap at container width */
                }}
                svg {{
                    height: auto !important;
                    width: auto !important;
                    max-height: 100% !important;
                    max-width: 100% !important;
                }}
            </style>
            """
            full_html = css_injection + html_content
            
            components.html(full_html, height=height, width=width, scrolling=scrolling)
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to section:", 
    ["Overview & Trends", "Neighborhood Vibe", "Risk & Quality", "Value Hunter", "Host Strategy"]
)

# --- 4. MAIN CONTENT ---

if page == "Overview & Trends":
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
        
    st.subheader("Growth Forecast (Borough Level)")
    st.markdown("Projected growth trends for each borough (Log Scale).")
    # If you saved the static image for this one
    if os.path.exists(os.path.join(FIGS_DIR, "borough_forecast_log.png")):
        st.image(os.path.join(FIGS_DIR, "borough_forecast_log.png"))

elif page == "Neighborhood Vibe":
    st.header("vibes ✨ Neighborhood Experience")
    st.markdown("Going beyond price to understand the *feeling* of each area.")
    
    st.subheader("Safety")
    st.markdown("Mentions concerning negatove perceptions of saftey")
    display_html_file(os.path.join(MAPS_DIR, "safety_map.html"), height=600)
    
    with col1:
        st.subheader("The Truth Map: Overrated vs. Underrated")
        st.markdown("**Red:** Star Ratings > Text Sentiment (Inflated)\n**Blue:** Text Sentiment > Star Ratings (Tough Critics)")
        display_html_file(os.path.join(FIGS_DIR, "sentiment_gap_map.html"), height=600) # Assuming you saved this map name


    st.subheader("The Insomniac Index")
    st.markdown("Mapping Street Noise vs. Building Noise to find 'Silent Sanctuaries'.")
    display_html_file(os.path.join(FIGS_DIR, "noise_scatter.html"), height=700)

elif page == "Risk & Quality":
    st.header("🪳 Risk & Quality Assurance")
    st.markdown("Quantifying the hidden costs of booking: Pests, Dirt, and Scams.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("The Pest Heatmap")
        st.markdown("% of listings with pest/vermin complaints.")
        display_html_file(os.path.join(FIGS_DIR, "pest_heatmap.html"), height=600)
        
    with col2:
        st.subheader("Scam Risk by Host Tier")
        st.markdown("Are professional hosts actually safer?")
        display_html_file(os.path.join(FIGS_DIR, "scam_risk_bar.html"), height=600)
        
    st.subheader("The Dirty Discount")
    st.markdown("Price penalty for listings with cleanliness complaints.")
    display_html_file(os.path.join(FIGS_DIR, "dirty_discount_box.html"), height=500)

elif page == "Value Hunter":
    st.header("💰 The Value Hunter")
    st.markdown("Finding the 'Smart Money' listings using our custom Z-Scores.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Borough Value Gap")
        st.markdown("Which boroughs are 'Rip-offs' (Red) vs 'Steals' (Green) relative to NYC average?")
        display_html_file(os.path.join(FIGS_DIR, "borough_value_bar.html"), height=600)
        
    with col2:
        st.subheader("The Momentum Leaderboard")
        st.markdown("Top 10 Trending vs. Cooling Neighborhoods.")
        display_html_file(os.path.join(FIGS_DIR, "momentum_bar.html"), height=600)
        
    st.subheader("🏆 The Perfect Stay Quadrant")
    st.markdown("The Holy Grail: High Value Score + High Guest Happiness.")
    display_html_file(os.path.join(FIGS_DIR, "perfect_stay_quadrant.html"), height=800)
    
    st.subheader("The Luxury Premium Curve")
    st.markdown("How much is an amenity point worth?")
    display_html_file(os.path.join(FIGS_DIR, "luxury_premium_scatter.html"), height=600)

elif page == "Host Strategy":
    st.header("🏢 Host Strategy & Market Structure")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("The Empire Invasion")
        st.markdown("% of listings managed by Corporate/Multi-unit Hosts.")
        display_html_file(os.path.join(FIGS_DIR, "empire_invasion_map.html"), height=600)
        
    with col2:
        st.subheader("The Service Paradox")
        st.markdown("Do Empires provide better service ratings than Amateurs?")
        display_html_file(os.path.join(FIGS_DIR, "service_paradox_box.html"), height=600)
        
    st.subheader("The Money Map")
    st.markdown("Revenue Efficiency: Which room types generate the most cash?")
    display_html_file(os.path.join(FIGS_DIR, "revenue_efficiency_bar.html"), height=700)