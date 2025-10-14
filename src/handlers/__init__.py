from src.handlers.main import router as main_router
from src.handlers.system import router as system_router
from src.handlers.subjects import router as subjects_router
from src.handlers.grades import router as grades_router

routers = [
    main_router,
    system_router,
    subjects_router,
    grades_router,
]
