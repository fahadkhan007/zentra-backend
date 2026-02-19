from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID


# -----------------------------
# CREATE PROFILE REQUEST
# (all fields required)
# -----------------------------
class ProfileCreateRequest(BaseModel):
    gender: Literal["Male", "Female"] = "Male"

    age: float=21
    height_m: float=1.70
    weight_kg: float=70

    family_overweight_history: Literal["yes", "no"]="no"
    high_calorie_food: Literal["yes", "no"]="no"

    vegetable_intake_freq: float=2
    main_meals_per_day: float=3

    snack_frequency: Literal["no", "Sometimes", "Frequently"]="Sometimes"
    smokes: Literal["yes", "no"]="no"

    water_intake_liters: float=2
    calorie_tracking: Literal["yes", "no"]="no"

    physical_activity_hours: float=2
    screentime_hours: float=2

    alcohol_consumption: Literal["no", "Sometimes", "Frequently"]="no"

    travel_mode: Literal[
        "Car",
        "Walking",
        "Bike",
        "Motorbike",
        "Public_Transportation"
    ]="Public_Transportation"


# -----------------------------
# UPDATE PROFILE REQUEST
# (all fields optional)
# -----------------------------
class ProfileUpdateRequest(BaseModel):
    gender: Optional[Literal["Male", "Female"]] = None

    age: Optional[float] = None
    height_m: Optional[float] = None
    weight_kg: Optional[float] = None

    family_overweight_history: Optional[Literal["yes", "no"]] = None
    high_calorie_food: Optional[Literal["yes", "no"]] = None

    vegetable_intake_freq: Optional[float] = None
    main_meals_per_day: Optional[float] = None

    snack_frequency: Optional[Literal["no", "Sometimes", "Frequently"]] = None
    smokes: Optional[Literal["yes", "no"]] = None

    water_intake_liters: Optional[float] = None
    calorie_tracking: Optional[Literal["yes", "no"]] = None

    physical_activity_hours: Optional[float] = None
    screentime_hours: Optional[float] = None

    alcohol_consumption: Optional[Literal["no", "Sometimes", "Frequently"]] = None

    travel_mode: Optional[
        Literal[
            "Car",
            "Walking",
            "Bike",
            "Motorbike",
            "Public_Transportation"
        ]
    ] = None


# -----------------------------
# RESPONSE MODEL
# -----------------------------
class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID

    gender: str
    age: float
    height_m: float
    weight_kg: float
    bmi: float

    family_overweight_history: str
    high_calorie_food: str
    vegetable_intake_freq: float
    main_meals_per_day: float
    snack_frequency: str
    smokes: str
    water_intake_liters: float
    calorie_tracking: str
    physical_activity_hours: float
    screentime_hours: float
    alcohol_consumption: str
    travel_mode: str

    class Config:
        from_attributes = True
