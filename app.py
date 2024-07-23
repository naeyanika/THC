import streamlit as st
import pandas as pd
import numpy as np
import io

st.title('Aplikasi Pengolahan THC')

# Function to format numbers
def format_no(no):
    try:
        if pd.notna(no):
            return f'{int(no):02d}.'
        else:
            return ''
    except (ValueError, TypeError):
        return str(no)

def format_center(center):
    try:
        if pd.notna(center):
            return f'{int(center):03d}'
        else:
            return ''
    except (ValueError, TypeError):
        return str(center)

def format_kelompok(kelompok):
    try:
        if pd.notna(kelompok):
            return f'{int(kelompok):02d}'
        else:
            return ''
    except (ValueError, TypeError):
        return str(kelompok)

# File upload
uploaded_files = st.file_uploader("Unggah file CSV", accept_multiple_files=True)

if uploaded_files:
    # Read CSV files
    dfs = {}
    for file in uploaded_files:
        df = pd.read_csv(file, delimiter=';', low_memory=False)
        dfs[file.name] = df

    # Process DbSimpanan
    if 'DbSimpanan.csv' in dfs:
        df1 = dfs['DbSimpanan.csv']
        df1.columns = df1.columns.str.strip()
        
        temp_client_id = df1['Client ID'].copy()
        df1['Client ID'] = df1['Account No']
        df1['Account No'] = temp_client_id
        
        df1.columns = ['NO.', 'DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL','JENIS SIMPANAN'] + list(df1.columns[10:])
        
        df1['NO.'] = df1['NO.'].apply(format_no)
        df1['CENTER'] = df1['CENTER'].apply(format_center)
        df1['KELOMPOK'] = df1['KELOMPOK'].apply(format_kelompok)
        
        st.write("DbSimpanan setelah diproses:")
        st.write(df1)

    # Process DbPinjaman
    if 'DbPinjaman.csv' in dfs:
        df2 = dfs['DbPinjaman.csv']
        df2.columns = df2.columns.str.strip()
        
        temp_client_id = df2['Client ID'].copy()
        df2['Client ID'] = df2['Loan No.']
        df2['Loan No.'] = temp_client_id
        
        df2.columns = ['NO.', 'DOCUMENT NO.', 'ID ANGGOTA', 'DISBURSE', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS PINJAMAN'] + list(df2.columns[11:])
        
        df2['NO.'] = df2['NO.'].apply(format_no)
        df2['CENTER'] = df2['CENTER'].apply(format_center)
        df2['KELOMPOK'] = df2['KELOMPOK'].apply(format_kelompok)
        
        st.write("DbPinjaman setelah diproses:")
        st.write(df2)

    # Process THC
    if 'THC.csv' in dfs:
        df3 = dfs['THC.csv']
        df3.columns = df3.columns.str.strip()
        
        df3['TRANS. DATE'] = pd.to_datetime(df3['TRANS. DATE'], format='%d/%m/%Y', errors='coerce')
        df3['ENTRY DATE'] = pd.to_datetime(df3['ENTRY DATE'], format='%d/%m/%Y', errors='coerce')
        
        st.write("THC setelah diproses:")
        st.write(df3)

        # Filter Pinjaman
        df3_cleaned = df3.dropna(subset=['DOCUMENT NO.'])
        df4 = df3_cleaned[df3_cleaned['DOCUMENT NO.'].str.startswith('P')].copy()
        
        df4['TRANS. DATE'] = df4['TRANS. DATE'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df4['ENTRY DATE'] = df4['ENTRY DATE'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df4['DEBIT'] = df4['DEBIT'].apply(lambda x: f'Rp {float(x):,.0f}')
        df4['CREDIT'] = df4['CREDIT'].apply(lambda x: f'Rp {float(x):,.0f}')
        
        st.write("THC Pinjaman:")
        st.write(df4)

        # Filter Simpanan
        prefixes = ['SWA-', 'SSU-', 'SPE-', 'SHR-', 'SPO-', 'SQB-', 'SPD-', 'TAB/', 'SKH-']
        prefix_pattern = '|'.join([f'^{prefix}' for prefix in prefixes])
        df5 = df3_cleaned[df3_cleaned['DOCUMENT NO.'].str.contains(prefix_pattern)].copy()
        
        df5['TRANS. DATE'] = df5['TRANS. DATE'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df5['ENTRY DATE'] = df5['ENTRY DATE'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df5['DEBIT'] = df5['DEBIT'].apply(lambda x: f'Rp {float(x):,.0f}')
        df5['CREDIT'] = df5['CREDIT'].apply(lambda x: f'Rp {float(x):,.0f}')
        
        st.write("THC Simpanan:")
        st.write(df5)

        # VLOOKUP dan Filter N/A
        if 'DbSimpanan.csv' in dfs and 'DbPinjaman.csv' in dfs:
            # Merge untuk pinjaman
            df4_merged = pd.merge(df4, df2[['DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS PINJAMAN']], on='DOCUMENT NO.', how='left')
            
            # Merge untuk simpanan
            df5_merged = pd.merge(df5, df1[['DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS SIMPANAN']], on='DOCUMENT NO.', how='left')
            
            # Filter N/A untuk pinjaman
            df_pinjaman_na = df4_merged[pd.isna(df4_merged['NAMA'])]
            
            # Filter N/A untuk simpanan
            df_simpanan_na = df5_merged[pd.isna(df5_merged['NAMA'])]
            
            st.write("THC Pinjaman setelah VLOOKUP:")
            st.write(df4_merged)
            
            st.write("THC Simpanan setelah VLOOKUP:")
            st.write(df5_merged)
            
            st.write("Pinjaman N/A:")
            st.write(df_pinjaman_na)
            
            st.write("Simpanan N/A:")
            st.write(df_simpanan_na)

            # Download links
            for name, df in {
                'THC_Pinjaman.xlsx': df4_merged,
                'THC_Simpanan.xlsx': df5_merged,
                'Pinjaman_NA.xlsx': df_pinjaman_na,
                'Simpanan_NA.xlsx': df_simpanan_na
            }.items():
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                st.download_button(label=f"Unduh {name}", data=buffer.getvalue(), file_name=name, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
