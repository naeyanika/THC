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
        
        df1.columns = ['NO.', 'DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS SIMPANAN'] + list(df1.columns[10:])
        
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

            # PIVOT DF4
            def sum_lists(x):
                if isinstance(x, list):
                    return sum(int(value.replace('Rp ', '').replace(',', '')) for value in x)
                return x

            df4_merged['TRANS. DATE'] = pd.to_datetime(df4_merged['TRANS. DATE'], format='%d/%m/%Y').dt.strftime('%d%m%Y')
            df4_merged['DUMMY'] = df4_merged['ID ANGGOTA'] + '' + df4_merged['TRANS. DATE']

            pivot_table4 = pd.pivot_table(df4_merged,
                                          values=['DEBIT', 'CREDIT'],
                                          index=['ID ANGGOTA', 'DUMMY', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'TRANS. DATE'],
                                          columns='JENIS PINJAMAN',
                                          aggfunc={'DEBIT': list, 'CREDIT': list},
                                          fill_value=0)

            pivot_table4 = pivot_table4.applymap(sum_lists)
            pivot_table4.columns = [f'{col[0]}_{col[1]}' for col in pivot_table4.columns]
            pivot_table4.reset_index(inplace=True)
            pivot_table4['TRANS. DATE'] = pd.to_datetime(pivot_table4['TRANS. DATE'], format='%d%m%Y').dt.strftime('%d/%m/%Y')

            new_columns4 = [
                'DEBIT_PINJAMAN UMUM',
                'DEBIT_PINJAMAN RENOVASI RUMAH',
                'DEBIT_PINJAMAN SANITASI',
                'DEBIT_PINJAMAN ARTA',
                'DEBIT_PINJAMAN MIKROBISNIS',
                'DEBIT_PINJAMAN DT. PENDIDIKAN',
                'DEBIT_PINJAMAN PERTANIAN',
                'CREDIT_PINJAMAN UMUM',
                'CREDIT_PINJAMAN RENOVASI RUMAH',
                'CREDIT_PINJAMAN SANITASI',
                'CREDIT_PINJAMAN ARTA',
                'CREDIT_PINJAMAN MIKROBISNIS',
                'CREDIT_PINJAMAN DT. PENDIDIKAN',
                'CREDIT_PINJAMAN PERTANIAN'
            ]

            for col in new_columns4:
                if col not in pivot_table4.columns:
                    pivot_table4[col] = 0

            pivot_table4['DEBIT_TOTAL'] = pivot_table4.filter(like='DEBIT').sum(axis=1)
            pivot_table4['CREDIT_TOTAL'] = pivot_table4.filter(like='CREDIT').sum(axis=1)

            st.write("Pivot Table THC Pinjaman:")
            st.write(pivot_table4)

            # PIVOT DF5
            df5_merged['TRANS. DATE'] = pd.to_datetime(df5_merged['TRANS. DATE'], format='%d/%m/%Y').dt.strftime('%d%m%Y')
            df5_merged['DUMMY'] = df5_merged['ID ANGGOTA'] + '' + df5_merged['TRANS. DATE']

            pivot_table5 = pd.pivot_table(df5_merged,
                                          values=['DEBIT', 'CREDIT'],
                                          index=['ID ANGGOTA', 'DUMMY', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'TRANS. DATE'],
                                          columns='JENIS SIMPANAN',
                                          aggfunc={'DEBIT': list, 'CREDIT': list},
                                          fill_value=0)

            pivot_table5 = pivot_table5.applymap(sum_lists)
            pivot_table5.columns = [f'{col[0]}_{col[1]}' for col in pivot_table5.columns]
            pivot_table5.reset_index(inplace=True)
            pivot_table5['TRANS. DATE'] = pd.to_datetime(pivot_table5['TRANS. DATE'], format='%d%m%Y').dt.strftime('%d/%m/%Y')

            new_columns5 = [
                'DEBIT_Simpanan Pensiun',
                'DEBIT_Simpanan Pokok',
                'DEBIT_Simpanan Sukarela',
                'DEBIT_Simpanan Wajib',
                'DEBIT_Simpanan Hari Raya',
                'DEBIT_Simpanan Qurban',
                'DEBIT_Simpanan Sipadan',
                'DEBIT_Simpanan Khusus',
                'CREDIT_Simpanan Pensiun',
                'CREDIT_Simpanan Pokok',
                'CREDIT_Simpanan Sukarela',
                'CREDIT_Simpanan Wajib',
                'CREDIT_Simpanan Hari Raya',
                'CREDIT_Simpanan Qurban',
                'CREDIT_Simpanan Sipadan',
                'CREDIT_Simpanan Khusus'
            ]

            for col in new_columns5:
                if col not in pivot_table5.columns:
                    pivot_table5[col] = 0

            pivot_table5['DEBIT_TOTAL'] = pivot_table5.filter(like='DEBIT').sum(axis=1)
            pivot_table5['CREDIT_TOTAL'] = pivot_table5.filter(like='CREDIT').sum(axis=1)

            st.write("Pivot Table THC Simpanan:")
            st.write(pivot_table5)

            # Save final result
            final_result = df6_merged.copy()

            final_result['DUMMY'] = final_result['ID ANGGOTA'] + '' + final_result['TRANS. DATE']
            final_result = pd.merge(final_result, pivot_table4, on='DUMMY', how='left')
            final_result = pd.merge(final_result, pivot_table5, on='DUMMY', how='left')

            # Process final result
            final_result['DEBIT_TOTAL'] = final_result[['DEBIT_TOTAL_x', 'DEBIT_TOTAL_y']].sum(axis=1)
            final_result['CREDIT_TOTAL'] = final_result[['CREDIT_TOTAL_x', 'CREDIT_TOTAL_y']].sum(axis=1)
            
            final_result = final_result.fillna(0)
            final_result = final_result.rename(columns=rename_dict)  
            rename_dict = {
    'KELOMPOK': 'KEL',
    'DEBIT_Simpanan Hari Raya': 'Db Sihara',
    'DEBIT_Simpanan Pensiun': 'Db Pensiun',
    'DEBIT_Simpanan Pokok': 'Db Pokok',
    'DEBIT_Simpanan Sukarela': 'Db Sukarela',
    'DEBIT_Simpanan Wajib': 'Db Wajib',
    'DEBIT_Simpanan Qurban': 'Db Qurban',
    'DEBIT_Simpanan Sipadan': 'Db SIPADAN',
    'DEBIT_Simpanan Khusus': 'Db Khusus',
    'Debit_Total_Simpanan': 'Db Total',
    'CREDIT_Simpanan Hari Raya': 'Cr Sihara',
    'CREDIT_Simpanan Pensiun': 'Cr Pensiun',
    'CREDIT_Simpanan Pokok': 'Cr Pokok',
    'CREDIT_Simpanan Sukarela': 'Cr Sukarela',
    'CREDIT_Simpanan Wajib': 'Cr Wajib',
    'CREDIT_Simpanan Qurban': 'Cr Qurban',
    'CREDIT_Simpanan Sipadan': 'Cr SIPADAN',
    'CREDIT_Simpanan Khusus': 'Cr Khusus',
    'Credit_Total_Simpanan': 'Cr Total',
    'DEBIT_PINJAMAN ARTA': 'Db PRT',
    'DEBIT_PINJAMAN DT. PENDIDIKAN': 'Db DTP',
    'DEBIT_PINJAMAN MIKROBISNIS': 'Db PMB',
    'DEBIT_PINJAMAN SANITASI': 'Db PSA',
    'DEBIT_PINJAMAN UMUM': 'Db PU',
    'DEBIT_PINJAMAN RENOVASI RUMAH': 'Db PRR',
    'DEBIT_PINJAMAN PERTANIAN': 'Db PTN',
    'Debit_Total_Pinjaman': 'Db Total2',
    'CREDIT_PINJAMAN ARTA': 'Cr PRT',
    'CREDIT_PINJAMAN DT. PENDIDIKAN': 'Cr DTP',
    'CREDIT_PINJAMAN MIKROBISNIS': 'Cr PMB',
    'CREDIT_PINJAMAN SANITASI': 'Cr PSA',
    'CREDIT_PINJAMAN UMUM': 'Cr PU',
    'CREDIT_PINJAMAN RENOVASI RUMAH': 'Cr PRR',
    'CREDIT_PINJAMAN PERTANIAN': 'Cr PTN',
    'Credit_Total_Pinjaman': 'Cr Total2'
}
            final_result = final_result.rename(columns=rename_dict)
            final_result.to_excel('Final THC.xlsx', index=False)
            
            # Save additional results
            with pd.ExcelWriter('Additional_Files.xlsx') as writer:
                pivot_table4.to_excel(writer, sheet_name='pivot_pinjaman', index=False)
                pivot_table5.to_excel(writer, sheet_name='pivot_simpanan', index=False)
                df_pinjaman_na.to_excel(writer, sheet_name='Pinjaman_NA', index=False)
                df_simpanan_na.to_excel(writer, sheet_name='Simpanan_NA', index=False)
                
            st.download_button(label='Unduh Final THC.xlsx', data=open('Final THC.xlsx', 'rb').read(), file_name='Final THC.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.download_button(label='Unduh Additional Files.xlsx', data=open('Additional_Files.xlsx', 'rb').read(), file_name='Additional_Files.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
