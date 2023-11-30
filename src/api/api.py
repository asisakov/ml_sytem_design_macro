import logging
from fastapi import FastAPI
import history
import forecast

PREFIX = '/api'

logging.basicConfig(level='INFO',
                    format='%(asctime)s\t%(levelname)s\t%(message)s')

app = FastAPI()
app.include_router(history.router, prefix=PREFIX)
app.include_router(forecast.router, prefix=PREFIX)
