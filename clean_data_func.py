import pandas as pd
import dateutil.parser

def clean_data(data, acct_col_names):
    cleaned_data = data.copy()
    
    # Remove any rows with missing values
    cleaned_data.dropna(inplace=True)

    # Check if any of the common account number column names are present
    acct_cols = []
    for col in cleaned_data.columns:
        if col.lower() in acct_col_names:
            acct_cols.append(col)
    
    # Remove duplicates from the account number column, if it exists
    if len(acct_cols) > 0:
        cleaned_data.drop_duplicates(subset=acct_cols, inplace=True)

        # Check if there are any duplicate account numbers after removing duplicates
        acct_counts = cleaned_data[acct_cols].value_counts()
        duplicates = acct_counts[acct_counts > 1].reset_index()[acct_cols]
        if len(duplicates) > 0:
            print("Warning: Duplicate account numbers found in the following rows and will be removed:")
            print(duplicates.to_string(index=False))
            cleaned_data.drop_duplicates(subset=acct_cols, keep=False, inplace=True)
    
    # Remove any rows with negative values in numerical columns
    for col in cleaned_data.select_dtypes(include=["int", "float"]).columns:
        neg_rows = cleaned_data[col] < 0
        if neg_rows.any():
            print(f"Warning: Negative values found in column '{col}' and will be removed:")
            print(cleaned_data.loc[neg_rows, [col]])
            cleaned_data.drop(index=cleaned_data.loc[neg_rows].index, inplace=True)
    
    # Remove any rows with invalid dates in date columns
    for col in cleaned_data.select_dtypes(include=["datetime64"]).columns:
        invalid_dates = cleaned_data[col].isna() | (cleaned_data[col] < "1900-01-01")
        if invalid_dates.any():
            print(f"Warning: Invalid dates found in column '{col}' and will be removed:")
            print(cleaned_data.loc[invalid_dates, [col]])
            cleaned_data.drop(index=cleaned_data.loc[invalid_dates].index, inplace=True)

    for col in cleaned_data.select_dtypes(include=["object"]).columns:
        if "date" in col.lower():
            try:
                cleaned_data[col] = cleaned_data[col].apply(dateutil.parser.parse)
            except ValueError:
                print(f"Warning: Invalid dates found in column '{col}' and will be removed:")
                invalid_dates = pd.to_datetime(cleaned_data[col], errors="coerce").isna()
                print(cleaned_data.loc[invalid_dates, [col]])
                cleaned_data.drop(index=cleaned_data.loc[invalid_dates].index, inplace=True)
    
    # Reset the index after cleaning
    cleaned_data.reset_index(drop=True, inplace=True)
    
    return cleaned_data

# Example usage
data = pd.read_excel("QR Code project - Adenta 20230209.xlsx")
acct_col_names = ["ACCT#", "ac_no", "Account_Number", "ACCOUNT_NUMBER", "ACCT_NO", "ACC_NO"]
cleaned_data = clean_data(data, acct_col_names)
cleaned_data.to_csv("cleaned_filename.csv", index=False)
print(cleaned_data.head())
