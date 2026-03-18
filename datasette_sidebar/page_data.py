from pydantic import BaseModel


class StarItem(BaseModel):
    id: str
    star_type: str  # "database", "table", "row"
    database_name: str
    table_name: str | None = None
    row_pks: str | None = None  # JSON-encoded primary key values
    created_at: str


class StarListResponse(BaseModel):
    stars: list[StarItem]


class ToggleStarRequest(BaseModel):
    star_type: str
    database_name: str
    table_name: str | None = None
    row_pks: str | None = None


class ToggleStarResponse(BaseModel):
    starred: bool
    star: StarItem | None = None


__exports__ = [StarListResponse]
