import streamlit as st
import pandas as pd
import re
from io import BytesIO


def scan_data_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scans the DataFrame for cells that might cause a .toLowerCase() or .lower() 
    crash in JavaScript/Python (i.e., non-string values, NaNs, or None).
    
    Returns a DataFrame with rows describing each potential issue:
    - row_index
    - column_name
    - value
    - reason
    """
    issues = []
    
    for row_idx in range(len(df)):
        for col_name in df.columns:
            val = df.iloc[row_idx][col_name]
            
            # 1) Check for None/NaN
            if pd.isna(val):
                # If it’s genuinely NaN or None, that can cause a crash
                issues.append({
                    "row_index": row_idx,
                    "column_name": col_name,
                    "value": val,
                    "reason": "Value is NaN/None"
                })
            else:
                # 2) Attempt to call lower() in a try-except
                #    This is what might fail if val is not a string-like object
                try:
                    str_val = str(val).lower()
                except Exception as e:
                    # If we fail to convert to string or lower, log the issue
                    issues.append({
                        "row_index": row_idx,
                        "column_name": col_name,
                        "value": val,
                        "reason": f"Failed to lower() -> {e}"
                    })
    
    return pd.DataFrame(issues)

# Utility function to remove URLs, mentions
def clean_text(text):
    # If the text is literally 'nan', return an empty string
    if text.lower() == "nan":
        return ""

    # Remove "https://t.co/..." links
    text = re.sub(r'https://t\.co/\S+', '', text)

    # Remove "https://t.me/..." links
    text = re.sub(r't\.me/\S+', '', text)

    # Remove .@mentions (e.g., ".@username")
    text = re.sub(r'\.@\w+', '', text)

    # Remove @mentions (where they are not preceded by alphanumeric, underscore, period, or hyphen)
    text = re.sub(r'(?<![\w\.-])@\w+', '', text)

    # Replace '|' with 'I'
    text = text.replace('|', 'I')

    return text.strip()

def main():
    st.title("Excel Cleaner: Remove Twitter Links (t.co), Mentions, and converts | pipe to I capital i ")

    uploaded_file = st.file_uploader("Upload an Excel (.xlsx) file", type=["xlsx"])
    if uploaded_file is not None:
        # Read the uploaded Excel file into a DataFrame
        df = pd.read_excel(uploaded_file)
        st.write("Original Data:")
        st.dataframe(df.head())


        # Scan for potential .toLowerCase() / .lower() issues
        issues_df = scan_data_issues(df)
        if issues_df.empty:
            st.success("No issues found! Your data should be safe to use.")
        else:
            st.error("Potential issues found in your data!")
            st.dataframe(issues_df)


        
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

