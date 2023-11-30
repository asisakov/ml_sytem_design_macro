import logging
from fastapi import FastAPI
import history
import forecast

logging.basicConfig(level='INFO',
                    format='%(asctime)s\t%(levelname)s\t%(message)s')

app = FastAPI()
app.include_router(history.router)
app.include_router(forecast.router)
