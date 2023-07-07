import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(
    page_title="Sentiment Analysis Comparison Bobobox vs Bobocabin",
    layout='wide'
)

st.title('Sentiment Analysis Comparison Bobobox vs Bobocabin')
url_editor = "https://www.linkedin.com/in/marselius-agus-dhion-374106226/"
st.markdown(f'Streamlit App by [Marselius Agus Dhion]({url_editor})', unsafe_allow_html=True)

# Membaca dataset
df = pd.read_csv('merged_file.csv')

with st.sidebar:
    st.write('Filter Based on pod_type & source')
    # Mendapatkan nilai unik dari kolom 'pod_type' dan 'source'
    pod_types = df['pod_type'].unique()
    sources = df['source'].unique()

    # Multiselect filtering dengan nilai default
    selected_pod_types = st.multiselect('Select pod types', pod_types, default=pod_types)
    selected_sources = st.multiselect('Select sources', sources, default=sources)

# Melakukan filtering berdasarkan nilai yang dipilih
filtered_df = df[df['pod_type'].isin(selected_pod_types) & df['source'].isin(selected_sources)]

# Menghitung jumlah nilai sentiment berdasarkan hotel_type pada data yang telah difilter
bobobox_sentiment_count = filtered_df[filtered_df['hotel_type'] == 'Bobobox']['Sentiment'].value_counts()
bobocabin_sentiment_count = filtered_df[filtered_df['hotel_type'] == 'Bobocabin']['Sentiment'].value_counts()

# Membuat DataFrame baru dari hasil perhitungan
sentiment_df = pd.DataFrame({
    'Sentiment': ['Positive', 'Negative', 'Neutral'],
    'Bobobox': [bobobox_sentiment_count.get('Positive', 0), bobobox_sentiment_count.get('Negative', 0),
                bobobox_sentiment_count.get('Neutral', 0)],
    'Bobocabin': [bobocabin_sentiment_count.get('Positive', 0), bobocabin_sentiment_count.get('Negative', 0),
                  bobocabin_sentiment_count.get('Neutral', 0)]
})

# Melt DataFrame untuk mengubah struktur data
melted_df = pd.melt(sentiment_df, id_vars='Sentiment', var_name='Hotel Type', value_name='Count')

# Menghitung persentase untuk setiap kategori 'hotel_type' dan membulatkannya menjadi 2 angka desimal terakhir
total_counts = melted_df.groupby('Hotel Type')['Count'].sum()
melted_df['Percentage'] = melted_df.apply(lambda row: round(row['Count'] / total_counts[row['Hotel Type']] * 100, 2), axis=1)

# Menambahkan kolom 'Symbol' dengan emotikon yang sesuai
melted_df['Symbol'] = melted_df.apply(
    lambda row: '👍' if (row['Sentiment'] == 'Positive' and row['Percentage'] > 70) else '👌' if (
            row['Sentiment'] == 'Positive' and row['Percentage'] > 50) else '👍' if (
            row['Sentiment'] == 'Negative' and row['Percentage'] < 30) else '👌' if (
            row['Sentiment'] == 'Negative' and row['Percentage'] <= 50) else '👎' if (
            row['Sentiment'] == 'Negative' and row['Percentage'] > 50) else '👌', axis=1)

# Membuat barplot menggunakan Altair dengan skema warna yang lebih enak dipandang
color_scale = alt.Scale(domain=['Positive', 'Negative', 'Neutral'], range=['#4CAF50', '#F44336', '#2196F3'])
barplot = alt.Chart(melted_df).mark_bar().encode(
    y='Hotel Type',
    x='Count',
    color=alt.Color('Sentiment', scale=color_scale),
    row='Sentiment',
    tooltip=['Sentiment', 'Hotel Type', 'Count', alt.Tooltip('Percentage:Q', format='.2f'), 'Symbol']
).properties(
    title='Perbandingan Sentimen Berdasarkan Tipe Hotel',
    width=800,  # Mengatur lebar barplot
    height=400  # Mengatur tinggi barplot
)

# Menampilkan barplot menggunakan Streamlit
st.write(barplot)
