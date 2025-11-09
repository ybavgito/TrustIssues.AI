import streamlit as st
import time

st.set_page_config(page_title="RiskLens AI Submission", layout="wide")


st.markdown("""
<style>
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
body {
    background: linear-gradient(to right, #f0f4f8, #d9e2ec);
}
.navbar {
    background: linear-gradient(90deg, #0FB5A8, #056D63);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin-bottom: 25px;
}
/* A new style for our form, matching the theme */
.form-container {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 25px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="navbar">RiskLens AI - New Vendor Submission</div>', unsafe_allow_html=True)



st.markdown('<div class="form-container">', unsafe_allow_html=True)

st.subheader("Submit New Document for Analysis")
st.write("Select the submission type and upload the corresponding PDF document.")

with st.form(key="submission_form"):
    
    submission_type = st.selectbox(
        "Select Submission Type",
        ("New Vendor Onboarding", "Existing Vendor Audit", "Contract Renewal", "Other")
    )

    uploaded_file = st.file_uploader(
        "Upload Vendor Contract or Document",
        type="pdf"  
    )

    submitted = st.form_submit_button("Submit for Analysis")


if submitted:
    if uploaded_file is not None and submission_type:
        with st.spinner(f"Analyzing '{uploaded_file.name}' for {submission_type}..."):
            time.sleep(3)  
        
        st.success(f"Success! Document '{uploaded_file.name}' has been submitted.")
        st.balloons()
    else:
        st.error("Please select a submission type AND upload a PDF file to submit.")

st.markdown('</div>', unsafe_allow_html=True)