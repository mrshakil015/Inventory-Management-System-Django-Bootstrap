import pandas as pd
import re

def process_file(input_file, output_file):
    # Read the input file (CSV or XLSX)
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    else:
        df = pd.read_csv(input_file)
    
    # Rename columns
    df.rename(columns={
        'HOMOEOPATHIC  PRODUCTS': 'medicine_name',
        'PACK \nSIZE': 'pack_size',
        'M.R.P. \nincl of GST': 'unit_price'
    }, inplace=True)
    
    # Add new columns
    df['medicine_category'] = 'Homeopathy'
    df['description'] = 'Demo'
    
    # Split pack_size into numeric value and units
    pack_sizes = df['pack_size'].astype(str).apply(lambda x: re.match(r"\s*(\d+)\s*([a-zA-Z]+)", x))
    df['pack_size'] = pack_sizes.apply(lambda x: int(x.group(1)) if x else None)
    df['pack_units'] = pack_sizes.apply(lambda x: x.group(2) if x else None)
    
    # Set medicine_type based on pack_units
    df['medicine_type'] = df['pack_units'].apply(lambda x: 'Liquids' if x == 'ml' else ('Solids' if x in ['gm', 'tabs'] else None))
    # Select and reorder required columns
    df = df[['medicine_name', 'medicine_category', 'medicine_type', 'pack_units', 'pack_size', 'unit_price', 'description']]
    
    # Save the processed DataFrame to an output file
    df.to_excel(output_file, index=False)
    print(f"File saved successfully as {output_file}")
    
    # Return the processed DataFrame
    return df

# Example usage
output_df = process_file('homeo_input.xlsx', 'home_medicine_output2.xlsx')
print(output_df)
