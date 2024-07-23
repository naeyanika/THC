import streamlit as st
import pandas as pd
import numpy as np
import io
import os
print(os.getcwd()) 


df1 = pd.read_csv("data/DbSimpanan.csv", delimiter=";", low_memory=False)
df2 = pd.read_csv("data/DbPinjaman.csv", delimiter=";", low_memory=False)
df3 = pd.read_csv("data/THC.csv", delimiter=";", low_memory=False)

#DF 1 DB SIMPANAN

df1.columns = df1.columns.str.strip()
temp_client_id = df1['Client ID'].copy()
df1['Client ID'] = df1['Account No']
df1['Account No'] = temp_client_id
df1.columns = ['NO.', 'DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL','JENIS SIMPANAN'] + list(df1.columns[10:])
df1.head(14)
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

df1['NO.'] = df1['NO.'].apply(format_no)
df1['CENTER'] = df1['CENTER'].apply(format_center)
df1['KELOMPOK'] = df1['KELOMPOK'].apply(format_kelompok)
df1.head(10)
df1.to_csv("/content/DbSimpanan_updated.csv", index=False, sep=';')

"""#DF2 DB PINJAMAN"""
df2.head(10)
df2.columns = df2.columns.str.strip()
temp_client_id = df2['Client ID'].copy()
df2['Client ID'] = df2['Loan No.']
df2['Loan No.'] = temp_client_id
print("\nSetelah perubahan:")
df2.columns = ['NO.', 'DOCUMENT NO.', 'ID ANGGOTA', 'DISBURSE', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS PINJAMAN'] + list(df2.columns[11:])

def format_no(no):
    return f'{int(no):02d}'

def format_center(center):
    return f'{int(center):03d}'

def format_kelompok(kelompok):
    return f'{int(kelompok):02d}'

def format_jam(jam):
    return pd.to_datetime(jam).strftime('%H:%M:%S')

def format_no(no):
    if pd.notna(no):
        return f'{int(no):02d}'
    else:
        return '00'

def format_center(center):
    if pd.notna(center):
        return f'{int(center):03d}'
    else:
        return '000'

def format_kelompok(kelompok):
    return kelompok

df2['NO.'] = df2['NO.'].apply(lambda x: format_no(x))
df2['CENTER'] = df2['CENTER'].apply(lambda x: format_center(x))
df2['KELOMPOK'] = df2['KELOMPOK'].apply(lambda x: format_kelompok(x))
df2.to_csv("/content/DbPinjaman_updated.csv", index=False, sep=';')
print(df2)

"""#DF3 THC"""

print(df3.columns)
df3.columns = df3.columns.str.strip()
print(df3['TRANS. DATE'].dtype)
print(df3['ENTRY DATE'].dtype)
df3['TRANS. DATE'] = pd.to_datetime(df3['TRANS. DATE'], format='%d/%m/%Y', errors='coerce')
df3['ENTRY DATE'] = pd.to_datetime(df3['ENTRY DATE'], format='%d/%m/%Y', errors='coerce')

"""#FILTER PINJAMAN"""
df3_cleaned = df3.dropna(subset=['DOCUMENT NO.'])
df3_filtered = df3_cleaned[df3_cleaned['DOCUMENT NO.'].str.startswith('P')]
print("DataFrame df3 setelah filter:")

df4 = df3_filtered.copy()
print("DataFrame df4:")


def format_date(date_str):
    return pd.to_datetime(date_str).strftime('%d/%m/%Y')

def format_currency(value):
    try:
        float_value = float(value)
        return f'Rp {float_value:,.0f}'
    except ValueError:
        return value

df4['TRANS. DATE'] = df4['TRANS. DATE'].apply(format_date)
df4['ENTRY DATE'] = df4['ENTRY DATE'].apply(format_date)
df4['DEBIT'] = df4['DEBIT'].apply(format_currency)
df4['CREDIT'] = df4['CREDIT'].apply(format_currency)
df4.to_csv("/content/THC Pinjaman.csv", index=False, sep=';')

"""#FILTER SIMPANAN"""

print(df3.columns)
df3.columns = df3.columns.str.strip()
df3_cleaned = df3.dropna(subset=['DOCUMENT NO.'])
prefixes = ['SWA-', 'SSU-', 'SPE-', 'SHR-', 'SPO-', 'SQB-', 'SPD-', 'TAB/', 'SKH-']
prefix_pattern = '|'.join([f'^{prefix}' for prefix in prefixes])
df3_filtered = df3_cleaned[df3_cleaned['DOCUMENT NO.'].str.contains(prefix_pattern)]
print("DataFrame df3 setelah filter:")

df5 = df3_filtered.copy()

print("DataFrame df5:")
print(df5)

def format_date(date_str):
    return pd.to_datetime(date_str).strftime('%d/%m/%Y')

def format_currency(value):
    try:
        float_value = float(value)
        return f'Rp {float_value:,.0f}'
    except ValueError:
        return value

df5['TRANS. DATE'] = df5['TRANS. DATE'].apply(format_date)
df5['ENTRY DATE'] = df5['ENTRY DATE'].apply(format_date)
df5['DEBIT'] = df5['DEBIT'].apply(format_currency)
df5['CREDIT'] = df5['CREDIT'].apply(format_currency)
df5.to_csv("/content/THC Simpanan.csv", index=False, sep=';')

#VLOOKUP DATA
# 1.   df1 Simpanan
# 2.   df2 Pinjaman
# 3.   df3 THC
# 4.   df4 THC Pinjaman
# 5.   df5 THC Simpanan

df4_merged = pd.merge(df4, df2[['DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS PINJAMAN']], on='DOCUMENT NO.', how='left')
df4_merged

df5_merged = pd.merge(df5, df1[['DOCUMENT NO.', 'ID ANGGOTA', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'JENIS SIMPANAN']], on='DOCUMENT NO.', how='left')
df5_merged

df_nan_only = df4_merged[pd.isna(df4_merged['NAMA'])]
df_nan_only.to_excel('Filter_Pinjaman_NaN.xlsx')

df_nan = df5_merged[pd.isna(df5_merged['NAMA'])]
df_nan.to_excel('Filter_Simpanan_NaN.xlsx')

#PIVOT DF4

import pandas as pd
def sum_lists(x):
    if isinstance(x, list):
        return sum(int(value.replace('Rp ', '').replace(',', '')) for value in x)
    return x
df4_merged['TRANS. DATE'] = pd.to_datetime(df4_merged['TRANS. DATE'], format='%d/%m/%Y').dt.strftime('%d%m%Y')
df4_merged['DUMMY'] = df4_merged['ID ANGGOTA'] + '' + df4_merged['TRANS. DATE']

pivot_table = pd.pivot_table(df4_merged,
                              values=['DEBIT', 'CREDIT'],
                              index=['ID ANGGOTA', 'DUMMY', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'TRANS. DATE'],
                              columns='JENIS PINJAMAN',
                              aggfunc={'DEBIT': list, 'CREDIT': list},
                              fill_value=0)

df4_merged = pd.DataFrame(df4_merged)

pivot_table = pivot_table.applymap(sum_lists)
pivot_table.columns = [f'{col[0]}_{col[1]}' for col in pivot_table.columns]
pivot_table.reset_index(inplace=True)
pivot_table['TRANS. DATE'] = pd.to_datetime(pivot_table['TRANS. DATE'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
pivot_table

new_columns = [
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

for col in new_columns:
    if col not in pivot_table.columns:
        pivot_table[col] = 0

columns = pivot_table.columns
pivot_table = pd.concat([pivot_table[col] for col in columns], axis=1)

pivot_table['DEBIT_TOTAL'] = pivot_table.filter(like='DEBIT').sum(axis=1)
pivot_table['CREDIT_TOTAL'] = pivot_table.filter(like='CREDIT').sum(axis=1)

debit_columns = pivot_table.filter(like='DEBIT_').columns
credit_columns = pivot_table.filter(like='CREDIT_').columns


pivot_table = pd.concat([pivot_table[['ID ANGGOTA', 'DUMMY', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'TRANS. DATE']], pivot_table[debit_columns],pivot_table[credit_columns]], axis=1)
pivot_table.to_excel('pivot_pinjaman.xlsx', index=False)
pivot_table

#PIVOT DF5
import pandas as pd
def sum_lists(x):
    if isinstance(x, list):
        return sum(int(value.replace('Rp ', '').replace(',', '')) for value in x)
    return x

df5_merged['TRANS. DATE'] = pd.to_datetime(df5_merged['TRANS. DATE'], format='%d/%m/%Y').dt.strftime('%d%m%Y')
df5_merged['DUMMY'] = df5_merged['ID ANGGOTA'] + '' + df5_merged['TRANS. DATE']

pivot_table = pd.pivot_table(df5_merged,
                              values=['DEBIT', 'CREDIT'],
                              index=['ID ANGGOTA', 'DUMMY', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'TRANS. DATE'],
                              columns='JENIS SIMPANAN',
                              aggfunc={'DEBIT': list, 'CREDIT': list},
                              fill_value=0)

pivot_table = pivot_table.applymap(sum_lists)

pivot_table.columns = [f'{col[0]}_{col[1]}' for col in pivot_table.columns]

pivot_table.reset_index(inplace=True)

pivot_table['TRANS. DATE'] = pd.to_datetime(pivot_table['TRANS. DATE'], format='%d%m%Y').dt.strftime('%d/%m/%Y')

new_columns = [
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

for col in new_columns:
    if col not in pivot_table.columns:
        pivot_table[col] = 0

columns = pivot_table.columns
pivot_table = pd.concat([pivot_table[col] for col in columns], axis=1)

pivot_table['DEBIT_TOTAL'] = pivot_table.filter(like='DEBIT').sum(axis=1)
pivot_table['CREDIT_TOTAL'] = pivot_table.filter(like='CREDIT').sum(axis=1)

debit_columns = pivot_table.filter(like='DEBIT_').columns
credit_columns = pivot_table.filter(like='CREDIT_').columns


pivot_table = pd.concat([pivot_table[['ID ANGGOTA', 'DUMMY', 'NAMA', 'CENTER', 'KELOMPOK', 'HARI', 'JAM', 'SL', 'TRANS. DATE']], pivot_table[debit_columns],pivot_table[credit_columns]], axis=1)

pivot_table.to_excel('pivot_simpanan.xlsx', index=False)
pivot_table

pd.read_excel('pivot_pinjaman.xlsx')

pd.read_excel('pivot_simpanan.xlsx')

df6 = pd.read_excel('pivot_simpanan.xlsx')
df7 = pd.read_excel('pivot_pinjaman.xlsx')

"""#Pivot Simpanan Dan Pinjaman"""

print(df7.head(0))

df6_merged = pd.merge(df6, df7[['DUMMY','DEBIT_PINJAMAN ARTA', 'DEBIT_PINJAMAN DT. PENDIDIKAN', 'DEBIT_PINJAMAN MIKROBISNIS', 'DEBIT_PINJAMAN SANITASI', 'DEBIT_PINJAMAN UMUM', 'DEBIT_PINJAMAN RENOVASI RUMAH', 'DEBIT_PINJAMAN PERTANIAN', 'DEBIT_TOTAL', 'CREDIT_PINJAMAN ARTA', 'CREDIT_PINJAMAN DT. PENDIDIKAN', 'CREDIT_PINJAMAN MIKROBISNIS', 'CREDIT_PINJAMAN SANITASI', 'CREDIT_PINJAMAN UMUM', 'CREDIT_PINJAMAN RENOVASI RUMAH', 'CREDIT_PINJAMAN PERTANIAN', 'CREDIT_TOTAL']], on='DUMMY', how='left')
df6_merged = df6_merged.fillna(0)

df6_merged['CENTER'] = df6_merged['CENTER'].astype(str).str.zfill(3)
df6_merged['KELOMPOK'] = df6_merged['KELOMPOK'].astype(str).str.zfill(2)

df6_merged

print(df6_merged.head(0))

kolom_rupiah = [
    'DEBIT_Simpanan Pensiun',
    'DEBIT_Simpanan Pokok',
    'DEBIT_Simpanan Sukarela',
    'DEBIT_Simpanan Wajib',
    'DEBIT_Simpanan Hari Raya',
    'DEBIT_Simpanan Qurban',
    'DEBIT_Simpanan Sipadan',
    'DEBIT_Simpanan Khusus',
    'DEBIT_TOTAL_x',
    'CREDIT_Simpanan Pensiun',
    'CREDIT_Simpanan Pokok',
    'CREDIT_Simpanan Sukarela',
    'CREDIT_Simpanan Wajib',
    'CREDIT_Simpanan Hari Raya',
    'CREDIT_Simpanan Qurban',
    'CREDIT_Simpanan Sipadan',
    'CREDIT_Simpanan Khusus',
    'CREDIT_TOTAL_x',
    'DEBIT_PINJAMAN UMUM',
    'DEBIT_PINJAMAN RENOVASI RUMAH',
    'DEBIT_PINJAMAN SANITASI',
    'DEBIT_PINJAMAN ARTA',
    'DEBIT_PINJAMAN MIKROBISNIS',
    'DEBIT_PINJAMAN DT. PENDIDIKAN',
    'DEBIT_PINJAMAN PERTANIAN',
    'DEBIT_TOTAL_y',
    'CREDIT_PINJAMAN UMUM',
    'CREDIT_PINJAMAN RENOVASI RUMAH',
    'CREDIT_PINJAMAN SANITASI',
    'CREDIT_PINJAMAN ARTA',
    'CREDIT_PINJAMAN MIKROBISNIS',
    'CREDIT_PINJAMAN DT. PENDIDIKAN',
    'CREDIT_PINJAMAN PERTANIAN',
    'CREDIT_TOTAL_y'
]

for kolom in kolom_rupiah:

    if df6_merged[kolom].dtype == 'object' and 'Rp' in df6_merged[kolom].iloc[0]:
       df6_merged[kolom] = df6_merged[kolom].replace('[Rp,]', '', regex=True).astype(int)
    else:
       df6_merged[kolom] = df6_merged[kolom].apply(lambda x: 0 if pd.isna(x) else x)

print(df6_merged)

print(df6_merged.head(0))
df6_merged = df6_merged.rename(columns={'DEBIT_TOTAL_x': 'Debit_Total_Simpanan', 'CREDIT_TOTAL_x': 'Credit_Total_Simpanan', 'DEBIT_TOTAL_y': 'Debit_Total_Pinjaman', 'CREDIT_TOTAL_y': 'Credit_Total_Pinjaman'})

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
df6_merged.rename(columns=rename_dict, inplace=True)
print(df6_merged.columns)
df6_merged.to_excel('Final THC.xlsx', index=False)

#Merapikan Dataframe THC Final
dffinal = pd.read_excel('Final THC.xlsx')

st.title('Analisis Transaksi THC')

#Sidebar untuk Pilihan Dataframe dan Fitur
st.sidebar.header('Navigasi')
selected_df = st.sidebar.selectbox("Pilih DataFrame:", ["Final THC", "Pivot Pinjaman", "Pivot Simpanan", "Filter Pinjaman NaN", "Filter Simpanan NaN"])

#Menampilkan DataFrame yang Dipilih
if selected_df == "Final THC":
    st.dataframe(df6_merged)
elif selected_df == "Pivot Pinjaman":
    st.dataframe(pd.read_excel('pivot_pinjaman.xlsx'))
elif selected_df == "Pivot Simpanan":
    st.dataframe(pd.read_excel('pivot_simpanan.xlsx'))
elif selected_df == "Filter Pinjaman NaN":
    st.dataframe(pd.read_excel('Filter_Pinjaman_NaN.xlsx'))
elif selected_df == "Filter Simpanan NaN":
    st.dataframe(pd.read_excel('Filter_Simpanan_NaN.xlsx'))

#Pencarian ID Anggota
st.sidebar.header('Pencarian')
search_id = st.sidebar.text_input("Cari ID Anggota:")
if search_id:
    if selected_df in ["Final THC", "Pivot Pinjaman", "Pivot Simpanan"]:
        filtered_df = df6_merged[df6_merged['ID ANGGOTA'] == search_id]
    elif selected_df == "Filter Pinjaman NaN":
        filtered_df = pd.read_excel('Filter_Pinjaman_NaN.xlsx')[pd.read_excel('Filter_Pinjaman_NaN.xlsx')['ID ANGGOTA'] == search_id]
    elif selected_df == "Filter Simpanan NaN":
        filtered_df = pd.read_excel('Filter_Simpanan_NaN.xlsx')[pd.read_excel('Filter_Simpanan_NaN.xlsx')['ID ANGGOTA'] == search_id]
    if not filtered_df.empty:
        st.dataframe(filtered_df)
    else:
        st.warning("ID Anggota tidak ditemukan.")
