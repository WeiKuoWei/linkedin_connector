from fastapi import HTTPException
import pandas as pd
import io

def validate_csv_file(file, content: bytes):
    """Validate uploaded CSV file format and required columns"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Parse CSV (skip first 3 rows like LinkedIn export format)
    df = pd.read_csv(io.StringIO(content.decode('utf-8')), skiprows=3)
    
    # Validate required columns
    required_columns = ["First Name", "Last Name", "URL", "Company", "Position"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required columns: {missing_columns}"
        )
    
    return df

def process_connections_from_df(df):
    """Process connections from DataFrame and return valid connections"""
    new_connections = []
    for _, row in df.iterrows():
        connection = {
            "first_name": str(row.get("First Name", "")).strip(),
            "last_name": str(row.get("Last Name", "")).strip(),
            "url": str(row.get("URL", "")).strip(),
            "email": str(row.get("Email Address", "")).strip(),
            "company": str(row.get("Company", "")).strip(),
            "position": str(row.get("Position", "")).strip(),
            "connected_on": str(row.get("Connected On", "")).strip(),
            "enriched": False
        }
        # Only add if has name and valid URL
        if (connection["first_name"] and connection["last_name"] and 
            connection["url"] and connection["url"].startswith("https://www.linkedin.com/in/")):
            new_connections.append(connection)
    
    return new_connections