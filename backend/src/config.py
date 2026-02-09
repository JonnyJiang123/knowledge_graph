from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Knowledge Graph Platform"
    debug: bool = False

    # Database
    mysql_uri: str = "mysql+asyncmy://root:password@localhost:3306/knowledge_graph"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_uri: str = "redis://localhost:6379"

    # Auth
    secret_key: str = "change-this-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Processing
    sync_file_size_limit: int = 5 * 1024 * 1024  # 5MB
    sync_row_limit: int = 10000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
