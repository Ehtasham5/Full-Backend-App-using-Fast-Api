from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, hash_password, verify_password
from app.database import Base, engine, get_db
from app.dependencies import get_active_user, require_admin
from app.models import User
from app.schemas import Token, UserCreate, UserRead


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple FastAPI Auth Backend")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Simple FastAPI backend is running"}


@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    if user_data.role not in {"user", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either user or admin",
        )

    existing_user = db.scalar(
        select(User).where(
            or_(User.email == user_data.email, User.username == user_data.username)
        )
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already exists",
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = db.scalar(select(User).where(User.username == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


@app.get("/users/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_active_user)) -> User:
    return current_user


@app.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    return list(db.scalars(select(User)).all())


@app.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_admin)) -> dict[str, str]:
    return {
        "message": f"Welcome admin {current_user.username}",
        "authorization": "You can see this because your role is admin",
    }
