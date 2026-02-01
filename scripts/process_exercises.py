"""
Process exercises.json into text chunks for embedding
"""
import json
from pathlib import Path


def exercise_to_text(exercise: dict) -> str:
    """Convert exercise JSON to readable text"""
    
    # Build instruction text
    instructions = exercise.get('instructions', [])
    if instructions:
        instruction_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(instructions)])
    else:
        instruction_text = "No instructions available"
    
    # Get muscle information
    primary_muscles = ', '.join(exercise.get('primaryMuscles', [])) or 'N/A'
    secondary_muscles = ', '.join(exercise.get('secondaryMuscles', [])) or 'None'
    
    # Create comprehensive text
    text = f"""Exercise: {exercise.get('name', 'Unknown')}

Category: {exercise.get('category', 'N/A')}
Difficulty Level: {exercise.get('level', 'N/A')}
Equipment Needed: {exercise.get('equipment', 'N/A')}
Exercise Type: {exercise.get('mechanic', 'N/A')}
Force Type: {exercise.get('force', 'N/A')}

Primary Muscles Worked: {primary_muscles}
Secondary Muscles: {secondary_muscles}

How to Perform:
{instruction_text}

Best For: {exercise.get('level', 'all levels')} level training
Suitable for: Building {primary_muscles}"""
    
    return text.strip()


def process_exercises():
    """Process exercises.json and create text chunks"""
    
    # Paths
    input_file = Path("data/raw/exercises.json")
    output_file = Path("data/processed/exercises_processed.json")
    
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load JSON
    print(f"📚 Loading exercises from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found!")
        return
    
    print(f"✅ Loaded {len(exercises)} exercises")
    
    # Process each exercise
    processed = []
    for idx, exercise in enumerate(exercises):
        text = exercise_to_text(exercise)
        
        processed.append({
            "id": f"exercise_{idx}",
            "text": text,
            "metadata": {
                "source": "exercise_database",
                "type": "exercise",
                "exercise_name": exercise.get('name', 'Unknown'),
                "category": exercise.get('category', 'N/A'),
                "level": exercise.get('level', 'N/A'),
                "equipment": exercise.get('equipment', 'N/A'),
                "primary_muscles": exercise.get('primaryMuscles', []),
                "secondary_muscles": exercise.get('secondaryMuscles', [])
            }
        })
    
    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Processed {len(processed)} exercises")
    print(f"💾 Saved to {output_file}")
    
    # Show sample
    if processed:
        print("\n📋 Sample Exercise (first 400 chars):")
        print(processed[0]['text'][:400] + "...")
        print(f"\n📊 Metadata: {processed[0]['metadata']}")


if __name__ == "__main__":
    process_exercises()
