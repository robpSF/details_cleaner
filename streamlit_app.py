import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Utility function to remove URLs, mentions, and emails
def clean_text(text):
    # If the text is literally 'nan', return an empty string
    if text.lower() == "nan":
        return ""

    # Remove "https://t.co/..." links
    text = re.sub(r'https://t\.co/\S+', '', text)
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    # Remove email addresses
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)

    return text.strip()

def main():
    st.title("Excel Cleaner: Remove Links, Mentions, and Emails")

    uploaded_file = st.file_uploader("Upload an Excel (.xlsx) file", type=["xlsx"])
    if uploaded_file is not None:
        # Read the uploaded Excel file into a DataFrame
        df = pd.read_excel(uploaded_file)
        st.write("Original Data:")
        st.dataframe(df.head())

        # Clean all string entries in the DataFrame
        for col in df.columns:
            # Convert column to string to avoid errors on numeric columns, then apply cleaning
            df[col] = df[col].astype(str).apply(clean_text)

        st.write("Cleaned Data:")
        st.dataframe(df.head())

        # Convert the cleaned DataFrame back to an Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            # writer.save()  # Remove this line; it's unnecessary and causes an error in pandas >= 2.x

        processed_data = output.getvalue()

        # Provide a download button for the cleaned XLSX
        st.download_button(
            label="Download cleaned Excel",
            data=processed_data,
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
