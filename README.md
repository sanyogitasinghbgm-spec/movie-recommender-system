# 🎬 Movie Recommender System

A **content-based movie recommender** built with Python, scikit-learn, and Streamlit — using the TMDB 5000 dataset from Kaggle.

---

## 🧠 How It Works

```
User selects a movie
        ↓
Look up its row in the cosine similarity matrix
        ↓
Sort all other movies by similarity score
        ↓
Return top 5 + fetch their posters from TMDB API
        ↓
Display in Streamlit UI
```

### What makes two movies "similar"?
Each movie is represented as a **bag of words** built from:
- `overview` — plot summary
- `genres` — e.g. Action, Adventure
- `keywords` — e.g. space war, based on novel
- `cast` — top 3 actors (spaces removed → single token)
- `crew` — director name only

These are concatenated into a `tags` string → vectorized with `CountVectorizer` → similarity computed with **cosine similarity**.

---

## 📁 Project Structure

```
movie-recommender/
│
├── model/
│   ├── movie_list.pkl       ← cleaned DataFrame (movie_id, title, tags)
│   └── similarity.pkl       ← precomputed cosine similarity matrix
│
├── movie_recommender_notebook.py   ← data prep + model training (run on Kaggle)
├── app.py                          ← Streamlit web app
├── requirements.txt
└── README.md
```

---

## 🚀 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (make sure model/ folder has the .pkl files)
python -m streamlit run app.py  # --> runs directly
```

---

## 📦 Requirements

```
streamlit
requests
scikit-learn
pandas
numpy
```

---

## 🌐 API

Poster images are fetched from **TMDB API** using each movie's `movie_id`.

---

## 📚 Credits

Tutorial by [CampusX](https://youtube.com/@campusx-official) · Dataset from [Kaggle TMDB 5000](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)