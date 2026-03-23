import streamlit as st

def render_card_data(result: dict):
    st.subheader("Extracted Card Data")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Name", result.get("name") or "Not detected")
        st.metric("HP", result.get("hp") or "Not detected")

    with col2:
        types = result.get("types")
        st.metric("Types", ", ".join(types) if types else "Not detected")

    # Moves
    moves = result.get("moves")
    if moves:
        st.markdown("**Moves**")
        for move in moves:
            with st.expander(f"{move.get('name')} — {move.get('damage', '?')} damage"):
                st.write(move.get("text") or "No description available.")
    else:
        st.metric("Moves", "Not detected")