from aiogram import Dispatcher

from src.middlewares import ClearStateOnBackMiddleware, DeleteOldMessageOnCallbackMiddleware


dp = Dispatcher()

dp.callback_query.middleware(ClearStateOnBackMiddleware())
dp.callback_query.middleware(DeleteOldMessageOnCallbackMiddleware())
