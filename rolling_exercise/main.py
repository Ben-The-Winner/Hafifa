from database import init_db
from fastapi import FastAPI, File, HTTPException, UploadFile
from services import process_and_save_csv
import uvicorn

app = FastAPI(
    title="Air Quality API", description="ETL & API service for air pollution"
)


@app.on_event("startup")
def startup_event():
  init_db()


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
  if not file.filename.endswith(".csv"):
    raise HTTPException(
        status_code=400, detail="Only CSV files are supported."
    )

  try:
    inserted_rows, alerts_count = process_and_save_csv(file.file)
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except Exception as e:
    raise HTTPException(
        status_code=500, detail=f"Internal server error: {str(e)}"
    )

  return {
      "message": "File processed and data saved successfully.",
      "rows_inserted": inserted_rows,
      "alerts_generated": alerts_count,
  }


if __name__ == "__main__":

  uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)