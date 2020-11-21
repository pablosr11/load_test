from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.messages import msg_router

app = FastAPI()
main_router = APIRouter()
main_router.include_router(router=msg_router, prefix="/sms", tags=["Messages"])
app.include_router(main_router, prefix="/api")

origins = [
    "*",  # to be modified for added security once we have static urls/other way of adding known origins
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## queries profiling
# import sqltap
# @app.middleware("http")
# async def add_sql_tap(request: Request, call_next):
#     profiler = sqltap.start()
#     response = await call_next(request)
#     statistics = profiler.collect()
#     sqltap.report(statistics, "report.txt", report_format="text")
#     return response

# import yappi
# import sqlalchemy
# import fastapi
# @app.middleware("http")
# async def yappi_metrics(request: Request, call_next):
#     yappi.set_clock_type("wall")
#     yappi.start()
#     response = await call_next(request)
#     yappi.stop()
#     # endpoint_func = yappi.get_func_stats(filter_callback=lambda x: fastapi.routing.run_endpoint_function)
#     # deps = yappi.get_func_stats(filter_callback=lambda x: fastapi.routing.solve_dependencies)
#     # db_exec_time = yappi.get_func_stats(filter_callback=lambda x: sqlalchemy.engine.base.Engine.execute.__qualname__)
#     # db_fetch_time = yappi.get_func_stats(filter_callback=lambda x: (
# 	# 	sqlalchemy.engine.ResultProxy.fetchone,
# 	# 	sqlalchemy.engine.ResultProxy.fetchmany,
# 	# 	sqlalchemy.engine.ResultProxy.fetchall,
# 	# ))
#     # pydantic_time = yappi.get_func_stats(filter_callback=lambda x: fastapi.routing.serialize_response.__qualname__)
#     # render_time = yappi.get_func_stats(filter_callback=lambda x: response.render.__qualname__)

#     yappi.get_func_stats().sort('ttot', sort_order="desc").print_all() # All time
#     return response
