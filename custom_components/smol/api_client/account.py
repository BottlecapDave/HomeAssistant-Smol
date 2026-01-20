from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SmolProduct(BaseModel):
  typeId: str
  name: str
  packSize: int

class SmolSubscription(BaseModel):
  nextChargeScheduledAt: Optional[datetime]
  product: SmolProduct

class SmolHolidyModeConfig(BaseModel):
  endDate: Optional[datetime]

class SmolHolidyMode(BaseModel):
  config: Optional[SmolHolidyModeConfig]

class SmolAccount(BaseModel):
  holidayMode: SmolHolidyMode
  subscriptions: list[SmolSubscription]

