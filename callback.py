from aiogram.filters.callback_data import CallbackData


class CallBackData(CallbackData, prefix='data'):
    callback_model_data: str
