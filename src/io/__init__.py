"""
src.io 模块
数据输入/输出层，包含数据模型、加载器和适配器。
"""

from .schema import (
    OHLCData,
    COL_DATETIME, COL_OPEN, COL_HIGH, COL_LOW, COL_CLOSE, COL_VOLUME,
    REQUIRED_COLUMNS
)
from .loader import load_ohlc, list_adapters, register_adapter

__all__ = [
    "OHLCData",
    "COL_DATETIME", "COL_OPEN", "COL_HIGH", "COL_LOW", "COL_CLOSE", "COL_VOLUME",
    "REQUIRED_COLUMNS",
    "load_ohlc", "list_adapters", "register_adapter",
]
