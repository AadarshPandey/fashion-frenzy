import streamlit as st
import os
from PIL import Image
from modules import wardrobe, chatbot, vton
import time

def render_left_column():
    st.header("👗 Your Wardrobe")
    st.caption("Upload & Categorize")

    # 1. Upload Interface
    uploaded_file = st.file_uploader("Upload Cloth Image", type=["jpg", "png", "jpeg"])
    
    # 2. Categorization Dropdown
    category = st.selectbox(
        "Select Category", 
        options=list(wardrobe.CATEGORIES.keys()),
        index=3 # Default to Upper Body
    )

    if uploaded_file and st.button("Add to Wardrobe"):
        path = wardrobe.save_uploaded_item(uploaded_file, category)
        st.success(f"Saved to {category}!")
        # Refresh context for LLM
        st.session_state['wardrobe_updated'] = True
        st.rerun() # Rerun to show the new image immediately

    st.divider()
    
    # 3. Visual Display of Folders
    st.subheader("Inventory")
    
    # Iterate through categories
    for cat_name, folder in wardrobe.CATEGORIES.items():
        path = os.path.join(wardrobe.WARDROBE_ROOT, folder)
        
        if os.path.exists(path):
            files = os.listdir(path)
            if files:
                with st.expander(f"{cat_name} ({len(files)})"):
                    # Create columns for grid layout
                    cols = st.columns(3)
                    for i, file_name in enumerate(files):
                        img_path = os.path.join(path, file_name)
                        
                        # Use a container for each grid item (image + delete button)
                        with cols[i % 3].container(border=True):
                            try:
                                img = Image.open(img_path)
                                st.image(img, use_container_width=True)
                                st.caption(file_name)
                                
                                # Add Delete Button (Trash Icon)
                                if st.button("🗑️", key=f"del_{img_path}", help=f"Delete {file_name}"):
                                    success, msg = wardrobe.delete_item(img_path)
                                    if success:
                                        st.toast(msg, icon="🗑️")
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                        
                            except Exception as e:
                                st.error(f"Error loading image: {e}")

def render_middle_column():
    st.header("💬 Style Assistant")
    
    # Gender Selection - above chat
    col_gender, col_spacer = st.columns([1, 2])
    with col_gender:
        gender = st.selectbox(
            "🚻 Select Gender",
            options=["Male", "Female"],
            index=0 if st.session_state.get('user_gender', 'Male') == 'Male' else 1,
            key="gender_selector",
            help="Select gender for personalized recommendations"
        )
        # Update session state when changed
        st.session_state.user_gender = gender
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    chat_container = st.container(height=450)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    # Chat Input
    if prompt := st.chat_input("Ask about your outfit..."):
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt, unsafe_allow_html=True)

        # 2. Get Wardrobe Context
        current_inventory = wardrobe.get_wardrobe_inventory()

        # 3. Generate AI Response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Use synchronous wrapper
                    response = chatbot.run_chat_tool(
                        prompt, 
                        st.session_state.messages[:-1], 
                        current_inventory
                    )
                    st.markdown(response, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def render_right_column():
    st.header("🪄 Virtual Try-On")
    
    col1, col2 = st.columns(2)
    
    with col1:
        person = st.file_uploader("1. Upload Person", type=["jpg", "png"], key="vton_person")
        if person:
            st.image(person, caption="You", use_container_width=True)
            
    with col2:
        garment = st.file_uploader("2. Upload Dress", type=["jpg", "png"], key="vton_cloth")
        if garment:
            st.image(garment, caption="Dress", use_container_width=True)

    if person and garment:
        if st.button("Generate Try-On", type="primary", use_container_width=True):
            with st.status("Generating look...", expanded=True) as status:
                st.write("Identifying body keypoints...")
                time.sleep(0.5)
                st.write("Warping garment...")
                time.sleep(0.5)
                st.write("Blending textures...")
                
                # Call the VTON module
                try:
                    # UPDATED: Now returns just the image
                    result_img = vton.process_virtual_tryon(Image.open(person), Image.open(garment))
                    status.update(label="Complete!", state="complete", expanded=False)
                    
                    # Display the result
                    st.image(result_img, caption="Virtual Try-On Result (Nano Banana)", use_container_width=True)
                    
                except Exception as e:
                    status.update(label="Failed", state="error", expanded=False)
                    st.error(f"Generation failed: {str(e)}")

            st.info("Powered by Google's experimental Nano Banana model.")
