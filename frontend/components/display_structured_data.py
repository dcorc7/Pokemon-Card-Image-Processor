import streamlit as st

def render_card_data(result: dict):
    # Header for the uploaded card data
    st.header("Extracted Card Data")

    # Create two columns
    col1, col2 = st.columns(2)

    # Column one filled with name and HP
    with col1:
        st.subheader("Name", result.get("name") or "Not detected")
        st.subheader("HP", result.get("hp") or "Not detected")

    # Column two filled with Pokemon types
    with col2:
        types = result.get("types")
        st.subheader("Types", ", ".join(types) if types else "Not detected")

    # Display moves below above columns
    moves = result.get("moves")

    # Check if moves category exists
    if moves:
        st.subheader("**Moves**")

        # Loop through all resulting moves
        for move in moves:
            # Write the move name, damage done and text
            with st.expander(f"{move.get('name')} — {move.get('damage', '?')} damage"):
                st.write(move.get("text") or "No description available.")

    # Placeholder if no moves detected
    else:
        st.metric("Moves", "Not detected")