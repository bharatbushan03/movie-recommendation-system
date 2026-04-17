from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data.csv"
MODEL_PATH = ROOT_DIR / "model.joblib"

app = FastAPI(title="Movie Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"],
)

class MovieRequest(BaseModel):
    title: str
    top_k: int = Field(default=5, ge=1, le=20)

class MovieResponse(BaseModel):
    input_title: str
    recommendations: list[str]

@lru_cache
def load_assets() -> tuple[pd.DataFrame, object]:
    if not DATA_PATH.exists():
        raise RuntimeError(f'Missing data file: {DATA_PATH}')
    if not MODEL_PATH.exists():
        raise RuntimeError(f'Missing model file: {MODEL_PATH}')
    
    df = pd.read_csv(DATA_PATH)
    model = joblib.load(MODEL_PATH)
    return df, model

def recommend_titles(title: str, top_k: int) -> list[str]:
    df, model = load_assets()
    title_series = df['title'].astype(str)
    matches = df[title_series.str.lower() == title.lower()]
    if matches.empty:
        raise HTTPException(status_code = 404, detail = f"Movie '{title}' not found in DataBase")
    idx = int(matches.index[0])
    distances = model[idx]
    ranked = sorted(enumerate(distances), key = lambda x: x[1], reverse=True)
    rec_indexes = [i for i, _ in ranked if i != idx][:top_k]
    return [str(df.iloc[i]["title"]) for i in rec_indexes]

@app.get('/')
def root() -> dict[str, str]:
    return {"message": "Welcome to the Movie Recommendation API"}

@app.get('/health')
def health() -> dict[str, str]:
    try:
        load_assets()
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    
@app.get("/movies")
def movies() -> list[str]:
    df, _ = load_assets()
    return df['title'].dropna().astype(str).tolist()

@app.post("/recommend", response_model=MovieResponse)
def recommend(movie: MovieRequest) -> MovieResponse:
    rec = recommend_titles(movie.title, movie.top_k)
    return MovieResponse(input_title=movie.title, recommendations=rec)

