# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Application settings."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class IGDBSettings(BaseModel):
    """Settings for the IGDB API."""

    client_id: str
    client_secret: str


class Settings(BaseSettings):
    """Application-wide settings."""

    igdb: IGDBSettings

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter=".")


settings = Settings()
