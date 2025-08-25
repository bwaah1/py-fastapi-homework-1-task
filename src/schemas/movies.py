from pydantic import BaseModel
import datetime


class MovieDetailResponseSchema(BaseModel):
    id: int
    name: str
    date: datetime.date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str


class MovieListResponseSchema(BaseModel):
    id: int
    movies: list[MovieDetailResponseSchema]
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int
