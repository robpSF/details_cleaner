import streamlit as st
import pandas as pd
import re
from io import BytesIO
from collections import defaultdict

def clean_text(text: str) -> str:
    """Remove links, @mentions, and email addresses from a string."""
    # Remove "https://t.co/..." links
    text = re.sub(r'https://t\.co/\S+', '', text)
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    # Remove email addresses
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
    return text.strip()

def main():
    st.title("Excel Cleaner: Remove Links, Mentions, and Emails")

    # Step 1: Upload Excel file
    uploaded_file = st.file_uploader("Upload an Excel (.xlsx) file", type=["xlsx"])
    if uploaded_file is not None:
        # Step 2: Read Excel into DataFrame
        df = pd.read_excel(uploaded_file)
        st.write("### Original Data (first 5 rows):")
        st.dataframe(df.head())

        # Step 3: Prepare to track modifications and warnings
        # We'll store a list of (Name, Handle, Column) when the cell changes
        modifications = []
        # We'll store a list of (Name, Handle, Column) if we find ",,"
        warnings = []

        # Step 4: Clean Data
        for i in range(len(df)):
            # Safely get Name and Handle if they exist
            name = df.at[i, 'Name'] if 'Name' in df.columns else None
            handle = df.at[i, 'Handle'] if 'Handle' in df.columns else None

            for col in df.columns:
                old_val = str(df.at[i, col])
                new_val = clean_text(old_val)

                # If the text changed, record the replacement details
                if new_val != old_val:
                    modifications.append((name, handle, col))

                # Check if the cleaned text contains ",,"
                if ",," in new_val:
                    warnings.append((name, handle, col))

                # Update the DataFrame with the cleaned text
                df.at[i, col] = new_val

        # Step 5: Replace literal "nan" strings with empty strings
        df.replace("nan", "", inplace=True)

        # Step 6: Show Cleaned Data
        st.write("### Cleaned Data (first 5 rows):")
        st.dataframe(df.head())

        # Step 7a: Display Replacements (columns that changed)
        if modifications:
            st.write("### Columns Where Replacements Occurred")
            # Group changes by (Name, Handle)
            changes_by_person = defaultdict(set)
            for (person_name, person_handle, col_name) in modifications:
                changes_by_person[(person_name, person_handle)].add(col_name)

            for (person_name, person_handle), columns_changed in changes_by_person.items():
                st.markdown(f"**Name**: {person_name}, **Handle**: {person_handle}")
                for col in columns_changed:
                    st.markdown(f"&emsp;• **Column**: `{col}`")
        else:
            st.write("No replacements were necessary.")

        # Step 7b: Display Warnings (if ",," found)
        if warnings:
            st.write("### Warnings: Found Double Commas (',,')")
            # Group warnings by (Name, Handle)
            warnings_by_person = defaultdict(set)
            for (person_name, person_handle, col_name) in warnings:
                warnings_by_person[(person_name, person_handle)].add(col_name)

            for (person_name, person_handle), columns_with_double_commas in warnings_by_person.items():
                st.markdown(f"**Name**: {person_name}, **Handle**: {person_handle}")
                for col in columns_with_double_commas:
                    st.markdown(f"&emsp;• **Column**: `{col}` possible empty content after cleaning")
        else:
            st.write("No warnings found.")

        # Step 8: Allow Download of Cleaned File
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            # The context manager handles saving automatically.

        cleaned_data = output.getvalue()

        st.download_button(
            label="Download cleaned Excel",
            data=cleaned_data,
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
