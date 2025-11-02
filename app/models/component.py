from sqlalchemy import Column, String, Integer, Enum, Text
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class ComponentCategory(str, enum.Enum):
    """Категории компонентов"""
    PROCESSORY = "PROCESSORY"
    MATERINSKIE_PLATY = "MATERINSKIE_PLATY"
    VIDEOKARTY = "VIDEOKARTY"
    OPERATIVNAYA_PAMYAT = "OPERATIVNAYA_PAMYAT"
    KORPUSA = "KORPUSA"
    BLOKI_PITANIYA = "BLOKI_PITANIYA"
    ZHESTKIE_DISKI = "ZHESTKIE_DISKI"
    OHLAZHDENIE = "OHLAZHDENIE"
    SSD_NAKOPITELI = "SSD_NAKOPITELI"


class Component(BaseModel):
    """Модель компонента"""
    __tablename__ = "components"

    name = Column(String, nullable=False, index=True)
    link = Column(String, nullable=False)
    price = Column(Integer, nullable=True)
    image = Column(Text, nullable=True)
    category = Column(Enum(ComponentCategory), nullable=False, index=True)

