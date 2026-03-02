"""
Spectra — CORS Middleware Configuration

Exports the CORS settings used in main.py.
CORS (Cross-Origin Resource Sharing) controls which frontend domains
are allowed to make API requests to the backend.

In development: http://localhost:5173 (Vite default)
In production:  add your Vercel/Railway domain here via settings.cors_origins
"""

from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Re-export for use in main.py:
#
#   from app.middleware.cors import CORSMiddleware, cors_kwargs
#   app.add_middleware(CORSMiddleware, **cors_kwargs)
#
cors_kwargs = dict(
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

__all__ = ["CORSMiddleware", "cors_kwargs"]
