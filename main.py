import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from app.routers import products, categories, combos, orders, upload, admin_products

load_dotenv()

app = FastAPI(
    title="Aridhu Spices Backend API",
    description="Python FastAPI REST Service connected to MongoDB Atlas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ensure uploads directory exists and mount static files
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Enable CORS for Angular Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(combos.router)
app.include_router(orders.router)
app.include_router(upload.router)
app.include_router(admin_products.router)


@app.on_event("startup")
async def sync_r2_images_on_startup():
    try:
        from restore_images import restore
        await restore()
    except Exception as e:
        print(f"R2 Auto-Sync Warning: {e}")

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "OK",
        "message": "Python FastAPI Backend API is live!",
        "framework": "FastAPI",
        "database": "MongoDB Atlas"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
