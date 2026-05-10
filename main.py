import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import kagglehub

# Download latest version
path = kagglehub.dataset_download("lalit7881/warehouse-and-retail-sales")

print("Path to dataset files:", path)
df = pd.read_csv("data.csv")

st.write(df.head())

fig, ax = plt.subplots()
sns.scatterplot(data=df, x="age", y="income", ax=ax)

st.pyplot(fig)