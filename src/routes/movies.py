# router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, MovieModel
from schemas import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_list_of_movies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
):
    total_items = (await db.execute(select(func.count()).select_from(MovieModel))).scalar()
    total_pages = (total_items + per_page - 1) // per_page

    if page > total_pages > 0:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["query", "page"],
                "msg": "ensure this value is greater than or equal to 1",
                "type": "value_error.number.not_ge"
            }
        ])

    result = await db.execute(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    movies = result.scalars().all()

    movie_list = [
        MovieDetailResponseSchema(
            id=m.id,
            name=m.name,
            date=m.date,
            score=m.score,
            genre=m.genre,
            overview=m.overview,
            crew=m.crew,
            orig_title=m.orig_title,
            status=m.status,
            orig_lang=m.orig_lang,
            budget=m.budget,
            revenue=m.revenue,
            country=m.country,
        )
        for m in movies
    ]

    if not movie_list:
        raise HTTPException(status_code=404, detail="No movies found.")

    return MovieListResponseSchema(
        id=page,
        movies=movie_list,
        prev_page=f"/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        next_page=f"/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_details(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")

    return MovieDetailResponseSchema(
        id=movie.id,
        name=movie.name,
        date=movie.date,
        score=movie.score,
        genre=movie.genre,
        overview=movie.overview,
        crew=movie.crew,
        orig_title=movie.orig_title,
        status=movie.status,
        orig_lang=movie.orig_lang,
        budget=movie.budget,
        revenue=movie.revenue,
        country=movie.country,
    )
