import asyncio
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from models import init_db, User, Post, engine
from sqlalchemy.future import select
from jsonplaceholder_requests import fetch_users_data, fetch_posts_data
from typing import List

app = FastAPI()

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/users")
async def read_users(skip: int = 0, limit: int = 10):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [user.dict() for user in users]

@app.get("/posts")
async def read_posts(skip: int = 0, limit: int = 10):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Post).offset(skip).limit(limit)
        )
        posts = result.scalars().all()
        return [post.dict() for post in posts]

async def add_users_to_db(users_data):
    async with AsyncSession(engine) as session:
        users_to_add = [User(name=user['name'], username=user['username'], email=user['email']) for user in users_data]
        session.add_all(users_to_add)
        await session.commit()

async def add_posts_to_db(posts_data):
    async with AsyncSession(engine) as session:
        posts_to_add = [Post(user_id=post['userId'], title=post['title'], body=post['body']) for post in posts_data]
        session.add_all(posts_to_add)
        await session.commit()

async def async_main():
    users_data, posts_data = await asyncio.gather(
        fetch_users_data(),
        fetch_posts_data(),
    )

    await add_users_to_db(users_data)
    await add_posts_to_db(posts_data)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()