#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
import json
import os

DBHOST = "ds2022.cqee4iwdcaph.us-east-1.rds.amazonaws.com"
DBUSER = "admin"
DBPASS = os.getenv('DBPASS')
DB = "ega9cw"

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")  # zone apex
def zone_apex():
    return {"Hello": "Hello API!"}

@app.get("/sum/{a}/{b}")
def add(a: int, b: int):
    return {"sum": a + b}

@app.get("/multiply/{c}/{d}")
def multiply(c: int, d: int):
    return {"product": c * d}

@app.get("/square/{a}")
def square(a: int):
    return {"square": a ** 2}

@app.get("/divide/{c}/{d}")
def divide(c: int, d: int):
    return {"divide": c / d}

db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DB)
cur=db.cursor()
