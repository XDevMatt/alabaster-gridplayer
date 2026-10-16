"""What one cell keeps for itself, saved with the playlist under the
cell's own id (`Video.id`). A field left None means the app setting."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from gridplayer.params.static import VideoEndAction


class CellSource(BaseModel):
    path: Path
    weight: float = 1.0


class CellProfile(BaseModel):
    sources: list[CellSource] = Field(default_factory=list)
    upscale: str | None = None
    downscale: str | None = None
    deband: bool | None = None
    end_action: VideoEndAction | None = None
    loop: bool | None = None


def effective(profile: CellProfile | None, name: str, default: Any) -> Any:
    """The cell's own value where it has set one, else the default."""

    if profile is None:
        return default
    value = getattr(profile, name)
    return default if value is None else value
