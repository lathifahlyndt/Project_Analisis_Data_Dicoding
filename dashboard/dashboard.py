import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def get_total_count_by_hour_df(hour_df):
    hour_count_df = hour_df.groupby(by="hr").agg({"count": "sum"})
    return hour_count_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query('datetime >= "2011-01-01" and datetime < "2012-12-31"')
    return day_df_count_2011

def total_registered_df(day_df):
    reg_df = day_df.groupby(by="datetime").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual_df(day_df):
    cas_df = day_df.groupby(by="datetime").agg({"casual": "sum"}).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def sum_order(hour_df):
    sum_order_items_df = hour_df.groupby("hr")["count"].sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def macem_season(day_df): 
    season_df = day_df.groupby(by="season")["count"].sum().reset_index() 
    return season_df

# Baca data
days_df = pd.read_csv("dashboard/day_clean_data.csv")
hours_df = pd.read_csv("dashboard/hour_clean_data.csv")

datetime_columns = ["datetime"]
days_df.sort_values(by="datetime", inplace=True)
days_df.reset_index(drop=True, inplace=True)   

hours_df.sort_values(by="datetime", inplace=True)
hours_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["datetime"].min()
max_date_days = days_df["datetime"].max()

min_date_hour = hours_df["datetime"].min()
max_date_hour = hours_df["datetime"].max()

with st.sidebar:
    st.image("dashboard/profile.jpeg")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])

main_df_days = days_df[(days_df["datetime"] >= pd.to_datetime(start_date)) & 
                       (days_df["datetime"] <= pd.to_datetime(end_date))]

main_df_hour = hours_df[(hours_df["datetime"] >= pd.to_datetime(start_date)) & 
                        (hours_df["datetime"] <= pd.to_datetime(end_date))]

hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_hour)

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing :sparkles:')

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)

with col1:
    # Total penyewaan per bulan
    monthly_rentals = main_df_days.groupby(main_df_days['datetime'].dt.to_period("M"))["count"].sum()
    total_monthly_rentals = monthly_rentals.sum()
    st.metric("Total Penyewaan Bulanan", value=total_monthly_rentals)

with col2:
    # Rata-rata penyewaan per hari
    avg_daily_rentals = main_df_days["count"].mean()
    st.metric("Rata-rata Penyewaan per Hari", value=round(avg_daily_rentals, 2))

with col3:
    # Penyewaan tertinggi dalam sehari
    max_daily_rentals = main_df_days["count"].max()
    st.metric("Penyewaan Tertinggi dalam Sehari", value=max_daily_rentals)


# Chart 1: Persentase Penyewaan Saat Libur dan Tidak Libur
st.subheader("Persentase Penyewaan Saat Libur dan Tidak Libur")

holiday_counts = main_df_days.groupby('holiday')['count'].sum()

fig1, ax1 = plt.subplots()
ax1.pie(holiday_counts, labels=['Tidak Libur', 'Libur'], autopct='%1.1f%%', startangle=90)
ax1.set_title('Persentase Penyewaan Saat Libur dan Tidak Libur')

# Tambahkan deskripsi data
total_rental = holiday_counts.sum()
holiday_rental = holiday_counts.get(1, 0)  # Cek jika ada libur
non_holiday_rental = holiday_counts.get(0, 0)  # Cek jika tidak libur
ax1.text(-1.2, -1.5, f"Total penyewaan: {total_rental}", ha='left')
ax1.text(-1.2, -1.6, f"Penyewaan saat libur: {holiday_rental}", ha='left')
ax1.text(-1.2, -1.7, f"Penyewaan saat tidak libur: {non_holiday_rental}", ha='left')

st.pyplot(fig1)

# Chart 2: Jumlah Penyewaan per Hari
st.subheader("Jumlah Penyewaan per Hari")

day_df_sorted = main_df_days.sort_values('count', ascending=False)

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(day_df_sorted['datetime'].dt.day_name(), day_df_sorted['count'])
ax2.set_xlabel('Hari')
ax2.set_ylabel('Jumlah Penyewaan')
ax2.set_title('Jumlah Penyewaan per Hari')

# Menambahkan deskripsi dengan spasi
ax2.text(0, -1500, "Chart ini menampilkan jumlah penyewaan sepeda setiap hari.\n"
                   "Dapat dilihat bahwa hari Sabtu memiliki jumlah penyewaan terbanyak dan Senin jumlah penyewaan terdikit.", ha='left')

st.pyplot(fig2)

# Chart 3: Jumlah Penyewaan untuk Setiap Situasi Cuaca
st.subheader("Jumlah Penyewaan Sepeda Berdasarkan Kondisi Cuaca")

weather_counts = main_df_hour.groupby('weathersit')['count'].sum()

fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.bar(weather_counts.index, weather_counts.values)

# Menambahkan label dan judul
ax3.set_xlabel('Kondisi Cuaca')
ax3.set_ylabel('Jumlah Penyewaan')
ax3.set_title('Jumlah Penyewaan Sepeda Berdasarkan Kondisi Cuaca')

# Mengubah label sumbu x
ax3.set_xticks(weather_counts.index)
ax3.set_xticklabels(['Cerah', 'Berawan', 'Hujan Ringan/Salju Ringan', 'Hujan Lebat/Salju Lebat'])

st.pyplot(fig3)
