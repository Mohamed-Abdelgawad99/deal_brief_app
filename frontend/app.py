# frontend/app.py
import streamlit as st
import httpx
import pandas as pd
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Deal Flow", layout="wide")
st.title("🚀 Deal Brief Pipeline")

# --- SIDEBAR: Ingest ---
with st.sidebar:
    st.header("📥 Ingest New Deal")
    
    # Input size limit configuration
    MAX_CHARS = 10000  # 10K character limit
    
    deal_text = st.text_area(
        "Paste Deal Text / Email", 
        height=300, 
        placeholder="Paste the unstructured deal text here...",
        max_chars=MAX_CHARS,
        help=f"Maximum {MAX_CHARS:,} characters allowed"
    )
    
    # Character counter with visual feedback
    char_count = len(deal_text)
    remaining_chars = MAX_CHARS - char_count
    
    # Color coding based on usage
    if char_count == 0:
        counter_color = "gray"
        counter_text = f"0 / {MAX_CHARS:,} characters"
    elif remaining_chars > 1000:  # More than 1000 chars remaining
        counter_color = "green"
        counter_text = f"{char_count:,} / {MAX_CHARS:,} characters ({remaining_chars:,} remaining)"
    elif remaining_chars > 500:   # 500-1000 chars remaining
        counter_color = "orange"
        counter_text = f"{char_count:,} / {MAX_CHARS:,} characters ({remaining_chars:,} remaining)"
    else:  # Less than 500 chars remaining
        counter_color = "red"
        counter_text = f"{char_count:,} / {MAX_CHARS:,} characters ({remaining_chars:,} remaining)"
    
    # Display the counter with appropriate color
    st.markdown(f"<p style='color: {counter_color}; font-size: 14px; margin-top: -10px;'>{counter_text}</p>", unsafe_allow_html=True)
    
    # Warning when approaching limit
    if remaining_chars <= 500 and char_count > 0:
        st.warning(f"⚠️ Approaching character limit! Only {remaining_chars} characters remaining.")
    
    # Process button with validation
    process_button_disabled = char_count == 0 or char_count > MAX_CHARS
    
    if st.button("Process Deal", disabled=process_button_disabled):
        if not deal_text.strip():
            st.error("Please paste some text.")
        elif char_count > MAX_CHARS:
            st.error(f"❌ Text too long! Maximum {MAX_CHARS:,} characters allowed. Current: {char_count:,} characters.")
        else:
            with st.spinner("Analyzing with LLM..."):
                try:
                    response = httpx.post(f"{BACKEND_URL}/deals/", json={"text": deal_text}, timeout=60.0)
                    if response.status_code == 200:
                        st.success("Deal processed!")
                        st.json(response.json())
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

# --- MAIN PAGE: Dashboard ---
st.subheader("Recent Deals")

# Fetch Data
try:
    response = httpx.get(f"{BACKEND_URL}/deals/history")
    if response.status_code == 200:
        deals = response.json()
        
        if deals:
            # Convert to DataFrame for a nice table
            df = pd.DataFrame(deals)
            
            # Extract company_name from brief_data JSON column
            df['company_name'] = df['brief_data'].apply(
                lambda x: x.get('company_name', 'N/A') if isinstance(x, dict) and x else 'N/A'
            )

            df['tags'] = df['brief_data'].apply(
                lambda x: ", ".join(x.get('tags', [])) if isinstance(x, dict) and x and x.get('tags') else 'N/A'
            )
            
            # Columns to display
            display_df = df[["id","company_name", "status", "tags","error_message"]].rename(columns={
                "id": "Deal ID",
                "company_name": "Company Name",
                "status": "Status",
                "tags": "Tags",
                "error_message": "Error Message"
            })

            # Apply styling to show error messages in red
            def highlight_errors(row):
                if row['Status'] == 'FAILED':
                    return ['color: red'] * len(row)
                return [''] * len(row)

            display_df = display_df.style.apply(highlight_errors, axis=1)
            
            # Interactive Table
            selection = st.dataframe(
                display_df, 
                use_container_width=True,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun" # Allows clicking a row
            )
            # ----------------------------------------------------------------------------------#
            # Deals delete functionality section
            st.markdown("---")
            st.subheader("🗑️ Deal Management")
            
            # Create columns for delete functionality
            del_col1, del_col2, del_col3 = st.columns([2, 1, 1])
            
            with del_col1:
                # Dropdown to select deal to delete
                deal_options = {}
                for i, deal in enumerate(deals):
                    company_name = deal.get('brief_data', {}).get('company_name', 'N/A') if deal.get('brief_data') else 'N/A'
                    deal_options[f"ID {deal['id']} - {company_name} ({deal['status']})"] = deal['id']
                
                if deal_options:
                    selected_deal_label = st.selectbox(
                        "Select Deal to Delete:",
                        options=list(deal_options.keys()),
                        help="Choose a deal to delete from the database"
                    )
                    selected_deal_id = deal_options[selected_deal_label]
                else:
                    st.info("No deals available to delete")
                    selected_deal_id = None
            
            with del_col2:
                st.write("")  # Spacer
                st.write("")  # Spacer
                delete_button_disabled = selected_deal_id is None
                
                if st.button(
                    "🗑️ Delete Deal", 
                    disabled=delete_button_disabled,
                    type="secondary",
                    help="Permanently delete the selected deal"
                ):
                    # Show confirmation dialog
                    if 'confirm_delete' not in st.session_state:
                        st.session_state.confirm_delete = False
                    
                    st.session_state.confirm_delete = True
                    st.session_state.deal_to_delete = selected_deal_id
            
            with del_col3:
                st.write("")  # Spacer
                st.write("")  # Spacer
                
                # Confirmation and actual deletion
                if st.session_state.get('confirm_delete', False):
                    if st.button(
                        "✅ Confirm Delete", 
                        type="primary",
                        help="Confirm deletion - this cannot be undone!"
                    ):
                        try:
                            deal_id_to_delete = st.session_state.get('deal_to_delete')
                            with st.spinner(f"Deleting deal ID {deal_id_to_delete}..."):
                                delete_response = httpx.delete(f"{BACKEND_URL}/deals/{deal_id_to_delete}", timeout=10.0)
                                
                                if delete_response.status_code == 200:
                                    result = delete_response.json()
                                    if "message" in result:
                                        st.success(f"✅ {result['message']}")
                                    else:
                                        st.error(f"❌ {result.get('error', 'Unknown error occurred')}")
                                else:
                                    st.error(f"❌ Failed to delete deal. Status: {delete_response.status_code}")
                                
                                # Reset confirmation state and refresh
                                st.session_state.confirm_delete = False
                                if 'deal_to_delete' in st.session_state:
                                    del st.session_state.deal_to_delete
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"❌ Connection failed: {e}")
                            st.session_state.confirm_delete = False
                    
                    if st.button("❌ Cancel", help="Cancel deletion"):
                        st.session_state.confirm_delete = False
                        if 'deal_to_delete' in st.session_state:
                            del st.session_state.deal_to_delete
                        st.rerun()
            #----------------------------------------------------#
            
            # --- DETAIL VIEW (triggered by selection) ---
            # Streamlit's new selection API (st.dataframe selection)
            if selection and len(selection.selection.rows) > 0:
                selected_index = selection.selection.rows[0]
                selected_deal = deals[selected_index]
                
                st.divider()
                
                # Check if the deal processing failed
                if selected_deal.get("status") == "FAILED":
                    st.error("❌ Deal Brief Processing Failed")
                    st.header(f"� Deal Brief for Company: {selected_deal.get('brief_data', {}).get('company_name', 'Name not Mentioned') if selected_deal.get('brief_data') else 'Name not Mentioned'}")
                    st.warning("⚠️ The deal brief for this record failed to process. Please try again later.")
                    
                    # Show error message if available
                    if selected_deal.get("error_message"):
                        st.error(f"Error Details: {selected_deal['error_message']}")
                    
                    # Still allow viewing raw text
                    with st.expander("View Raw Source Text"):
                        st.text(selected_deal["raw_text"])
                        
                else:
                    # Normal view for successful processing
                    st.header(f"📄 Deal Brief for Company: {selected_deal.get('brief_data', {}).get('company_name', 'Name not Mentioned') if selected_deal.get('brief_data') else 'Name not Mentioned'}")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("### 📝 10-Bullet Brief")
                        # Check if brief_data exists
                        if selected_deal.get("brief_data"):
                            for bullet in selected_deal["brief_data"].get("summary", []):
                                st.write(f"- {bullet}")
                        else:
                            st.warning("No brief data available yet.")

                        st.markdown("### 🏷️ Tags")
                        if selected_deal.get("brief_data"):
                             st.write(", ".join(selected_deal["brief_data"].get("tags", [])))

                    with col2:
                        st.markdown("### 📊 Key Metrics")
                        metrics = {
                            "Company Name": selected_deal["brief_data"].get("company_name") if selected_deal.get("brief_data") else "-",
                            "Founders": ", ".join(selected_deal["brief_data"]["founders"]) if selected_deal.get("brief_data") and selected_deal["brief_data"].get("founders") else "-",
                            "Geography": selected_deal["brief_data"].get("geography") if selected_deal.get("brief_data") else "-",
                            "Sector": selected_deal["brief_data"].get("sector") if selected_deal.get("brief_data") else "-",
                            "Stage": selected_deal["brief_data"].get("stage") if selected_deal.get("brief_data") else "-",
                            "Round Size": selected_deal["brief_data"].get("round_size") if selected_deal.get("brief_data") else "-",
                            "Metrics": "; ".join(selected_deal["brief_data"]["notable_metrics"]) if selected_deal.get("brief_data") and selected_deal["brief_data"].get("notable_metrics") else "-",
                        }
                        st.table(metrics)

                        with st.expander("View Raw Source Text"):
                            st.text(selected_deal["raw_text"])

        else:
            st.info("No deals found. Ingest one via the sidebar!")
    else:
        st.error("Failed to fetch deals from backend.")
except Exception as e:
    st.error(f"Could not connect to backend: {e}")