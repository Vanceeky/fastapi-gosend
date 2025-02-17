from pydantic import BaseModel



class RewardInput(BaseModel):
    id: str
    reference_id: str
    reward_source_type: str
    reward_points: float
    reward_from: str
    receiver: str
    reward_type: str
    description: str
    #updated_at: str
    #created_at: str
