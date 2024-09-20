# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Application settings."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class IGDBSettings(BaseModel):
    """Settings for the IGDB API."""

    client_id: str = ""
    client_secret: str = ""


class GeminiSettings(BaseModel):
    """Settings for the Gemini API."""

    api_key: str = ""


class LLMSettings(BaseModel):
    """General settings for all LLMs."""

    retest_target: int = 3
    max_attempts: int = 10


class Settings(BaseSettings):
    """Application-wide settings."""

    igdb: IGDBSettings = IGDBSettings()
    gemini: GeminiSettings = GeminiSettings()
    llm: LLMSettings = LLMSettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter=".")


settings = Settings()
