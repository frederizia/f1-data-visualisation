from fastapi import FastAPI

from f1_data_visualisation.interfaces.api import seasons


app = FastAPI(title="F1 data visualisation API")
app.include_router(seasons.router, prefix="/seasons")
