import pandas as pd
import joblib
import streamlit as st

st.title('Movie Recommendation System')
df = pd.read_csv('data.csv')

def recommend(movie):
    idx = df[df['title'] == movie].index[0]
    distances = similarity[idx]
    movies_list = sorted(list(enumerate(distances)), reverse = True, key = lambda x: x[1])[1:6]
    suggestions = []
    for i in movies_list:
        suggestions.append(df.iloc[i[0]].title)
    
    return suggestions

recommend = joblib.load(open('recommend.joblib', 'rb'))
similarity = joblib.load(open('model.joblib', 'rb'))

movie = st.selectbox('Movie', df['title'].unique())

suggestions = recommend(movie)

for i in suggestions:
    st.write(i)