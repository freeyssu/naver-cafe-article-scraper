from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=False
    )

    cafe_name: str = Field(default="", alias="CAFE_NAME")
    cafe_id: int = Field(default=0, alias="CAFE_ID")
    menu_id: int = Field(default=0, alias="MENU_ID")

    max_pages: int = Field(default=50, alias="MAX_PAGES")
    output_format: str = Field(default="csv", alias="OUTPUT_FORMAT")
    output_dir: Path = Field(default=Path("./data"), alias="OUTPUT_DIR")
    browser_restart_interval: int = Field(default=100, alias="BROWSER_RESTART_INTERVAL")

    min_delay: float = Field(default=2.0, alias="MIN_DELAY")
    max_delay: float = Field(default=5.0, alias="MAX_DELAY")

    @property
    def cookie_path(self) -> Path:
        return Path("data/naver_cookies.pkl")

    @property
    def board_url(self) -> str:
        return (
            f"https://cafe.naver.com/{self.cafe_name}"
            f"?iframe_url=/ArticleList.nhn%3Fsearch.clubid={self.cafe_id}"
            f"%26search.menuid={self.menu_id}%26search.page={{page}}"
        )


settings = Settings()
