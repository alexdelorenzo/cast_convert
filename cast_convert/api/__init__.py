from pathlib import Path

from fastapi import FastAPI

from ..core.enums import Strategy


app = FastAPI()


@app.get("/inspect")
async def inspect(
  name: str,
  path: Path,
  error: Strategy = Strategy.quit,
  subtitle: Path | None = None,
):
  return {"message": "Hello World"}

