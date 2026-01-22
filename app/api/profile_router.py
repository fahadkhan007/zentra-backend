from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db import models
from app.schemas.profile import ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse

router = APIRouter(prefix="/profile", tags=["User Profile"])


# -----------------------------
# Utility — BMI Calculator
# -----------------------------
def calculate_bmi(weight_kg: float, height_m: float):
    if height_m <= 0:
        return 0
    return round(weight_kg / (height_m ** 2), 2)


# -----------------------------
# CREATE USER PROFILE
# -----------------------------
@router.post("/create", response_model=ProfileResponse)
async def create_profile(
    data: ProfileCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Check if profile already exists
    result = await db.execute(
        select(models.UserHealthProfile).filter(
            models.UserHealthProfile.user_id == current_user.id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists. Use update endpoint."
        )

    # Compute BMI
    bmi_value = calculate_bmi(data.weight_kg, data.height_m)

    # Create basic user profile
    basic_profile = models.UserProfile(
        user_id=current_user.id,
        gender=data.gender,
        height_m=data.height_m,
        weight_kg=data.weight_kg,
        bmi=bmi_value
    )

    # Create detailed health profile
    health_profile = models.UserHealthProfile(
        user_id=current_user.id,
        gender=data.gender,
        age=data.age,
        height_m=data.height_m,
        weight_kg=data.weight_kg,
        bmi=bmi_value,

        family_overweight_history=data.family_overweight_history,
        high_calorie_food=data.high_calorie_food,
        vegetable_intake_freq=data.vegetable_intake_freq,
        main_meals_per_day=data.main_meals_per_day,
        snack_frequency=data.snack_frequency,
        smokes=data.smokes,
        water_intake_liters=data.water_intake_liters,
        calorie_tracking=data.calorie_tracking,
        physical_activity_hours=data.physical_activity_hours,
        screentime_hours=data.screentime_hours,
        alcohol_consumption=data.alcohol_consumption,
        travel_mode=data.travel_mode
    )

    db.add(basic_profile)
    db.add(health_profile)
    await db.commit()
    await db.refresh(health_profile)

    return health_profile


# -----------------------------
# UPDATE USER PROFILE
# -----------------------------
@router.put("/update", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    result = await db.execute(
        select(models.UserHealthProfile).filter(
            models.UserHealthProfile.user_id == current_user.id
        )
    )
    health_profile = result.scalar_one_or_none()

    if not health_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Get basic profile
    basic_result = await db.execute(
        select(models.UserProfile).filter(
            models.UserProfile.user_id == current_user.id
        )
    )
    basic_profile = basic_result.scalar_one_or_none()

    # Update only the fields provided by user
    update_data = data.dict(exclude_unset=True)

    # Fields that exist in both tables
    basic_fields = {"gender", "height_m", "weight_kg", "bmi"}

    for field, value in update_data.items():
        setattr(health_profile, field, value)
        # Also update basic profile if field exists there
        if basic_profile and field in basic_fields:
            setattr(basic_profile, field, value)

    # Recalculate BMI if height or weight changed
    if "weight_kg" in update_data or "height_m" in update_data:
        new_bmi = calculate_bmi(health_profile.weight_kg, health_profile.height_m)
        health_profile.bmi = new_bmi
        if basic_profile:
            basic_profile.bmi = new_bmi

    await db.commit()
    await db.refresh(health_profile)

    return health_profile


# -----------------------------
# GET CURRENT USER PROFILE
# -----------------------------
@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.UserHealthProfile).filter(
            models.UserHealthProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not created yet")

    return profile

