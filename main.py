from fastapi import FastAPI, Response, Header, HTTPException, Path
from fastapi.responses import StreamingResponse
from pathlib import Path as SysPath
from typing import Optional

app = FastAPI()

BASE_DIR = SysPath("file")  # Folder for downloadable files
BASE_DIR.mkdir(exist_ok=True)

@app.head("/download/{filename}")
async def head_download(filename: str = Path(...)):
    file_path = BASE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    file_size = file_path.stat().st_size
    return Response(headers={"Content-Length": str(file_size)})

@app.get("/download/{filename}")
async def download(filename: str = Path(...), range: Optional[str] = Header(None)):
    file_path = BASE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_size = file_path.stat().st_size
    start = 0
    end = file_size - 1

    if range:
        units, _, range_spec = range.partition("=")
        if units != "bytes":
            raise HTTPException(status_code=416, detail="Unsupported range unit")

        range_parts = range_spec.strip().split("-")
        start = int(range_parts[0]) if range_parts[0] else start
        end = int(range_parts[1]) if len(range_parts) > 1 and range_parts[1] else end

        if start > end or end >= file_size:
            raise HTTPException(status_code=416, detail="Invalid range")

    chunk_size = end - start + 1

    def file_iterator(start_pos: int, end_pos: int):
        with open(file_path, "rb") as f:
            f.seek(start_pos)
            bytes_left = end_pos - start_pos + 1
            while bytes_left > 0:
                chunk = f.read(min(8192, bytes_left))
                if not chunk:
                    break
                yield chunk
                bytes_left -= len(chunk)

    headers = {
        "Content-Length": str(chunk_size),
        "Accept-Ranges": "bytes",
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    if range:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        return StreamingResponse(file_iterator(start, end), status_code=206, headers=headers)
    else:
        return StreamingResponse(file_iterator(start, end), headers=headers)


# Optional: allow direct execution with `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3300, reload=False)
