#!/bin/bash
uvicorn api:app --host 0.0.0.0 --port 8000 & python social_media_automation.py & wait
