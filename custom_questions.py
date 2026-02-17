"""
Custom Question Set Manager for Med-GPT Evaluation
===================================================
Helper script to create and manage custom evaluation question sets.

Usage:
    python custom_questions.py
"""

import json
from pathlib import Path

# ===============================
# PREDEFINED QUESTION SETS
# ===============================

QUESTION_SETS = {
    "malaria_comprehensive": [
        "What are the diagnostic criteria for severe malaria according to WHO?",
        "What is the recommended first-line treatment for uncomplicated malaria?",
        "What are the symptoms of severe malaria in children?",
        "How is malaria diagnosed in endemic areas?",
        "What are the prevention strategies for malaria recommended by WHO?",
        "What is the dosage of artemisinin-based combination therapy for adults?",
        "What are the complications of untreated severe malaria?",
        "When should parenteral artesunate be administered?",
        "What are the contraindications for antimalarial drugs?",
        "How should malaria in pregnancy be managed according to WHO guidelines?",
        "What is the role of rapid diagnostic tests in malaria diagnosis?",
        "What are the WHO recommendations for malaria chemoprophylaxis?",
        "How should severe anemia in malaria be managed?",
        "What is the treatment for cerebral malaria?",
        "What are the signs of treatment failure in malaria?",
    ],
    "general_medical": [
        "What are the symptoms of diabetes mellitus?",
        "How is hypertension diagnosed?",
        "What is the first-line treatment for type 2 diabetes?",
        "What are the risk factors for cardiovascular disease?",
        "How should acute respiratory infections be managed?",
        "What are the WHO recommendations for tuberculosis treatment?",
        "What is the standard protocol for HIV testing?",
        "How should malnutrition in children be assessed?",
        "What are the vaccination schedules recommended by WHO?",
        "What is the management of severe dehydration?",
    ],
    "diagnostic_focused": [
        "What are the diagnostic criteria for severe malaria?",
        "How is malaria diagnosed using microscopy?",
        "What is the sensitivity of rapid diagnostic tests for malaria?",
        "What laboratory findings indicate severe malaria?",
        "How should malaria be differentiated from other febrile illnesses?",
        "What is the role of PCR in malaria diagnosis?",
        "When should a blood smear be repeated in malaria?",
        "What are the WHO criteria for confirmed malaria?",
        "How should asymptomatic malaria be diagnosed?",
        "What is the diagnostic approach for malaria in pregnancy?",
    ],
    "treatment_focused": [
        "What is the recommended treatment for uncomplicated malaria?",
        "How should severe malaria be treated in adults?",
        "What is the dosage of artesunate for severe malaria?",
        "What are the alternative treatments if ACTs are unavailable?",
        "How should treatment failure be managed?",
        "What is the treatment protocol for malaria in pregnancy?",
        "What supportive care is needed for severe malaria?",
        "How should drug-resistant malaria be treated?",
        "What is the role of primaquine in malaria treatment?",
        "When should blood transfusion be considered in malaria?",
    ],
    "quick_test": [
        "What is malaria?",
        "How is malaria transmitted?",
        "What are the main symptoms of malaria?",
        "How is malaria prevented?",
        "What is the treatment for malaria?",
    ],
}


def save_question_set(name, questions, output_dir="question_sets"):
    """Save a question set to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    filepath = output_path / f"{name}.json"

    data = {"name": name, "num_questions": len(questions), "questions": questions}

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved {len(questions)} questions to: {filepath}")


def load_question_set(name, input_dir="question_sets"):
    """Load a question set from JSON file."""
    filepath = Path(input_dir) / f"{name}.json"

    if not filepath.exists():
        print(f"✗ Question set not found: {filepath}")
        return None

    with open(filepath, "r") as f:
        data = json.load(f)

    print(f"✓ Loaded {data['num_questions']} questions from: {filepath}")
    return data["questions"]


def create_custom_set():
    """Interactive creation of custom question set."""
    print("\n" + "=" * 60)
    print("Create Custom Question Set")
    print("=" * 60)

    name = input("\nEnter question set name: ").strip()

    questions = []
    print("\nEnter questions (one per line, empty line to finish):")

    while True:
        question = input(f"Q{len(questions)+1}: ").strip()
        if not question:
            break
        questions.append(question)

    if questions:
        save_question_set(name, questions)
        print(f"\n✓ Created question set '{name}' with {len(questions)} questions")
    else:
        print("\n✗ No questions entered")


def list_available_sets():
    """List all available question sets."""
    print("\n" + "=" * 60)
    print("Available Question Sets")
    print("=" * 60)

    print("\nPredefined Sets:")
    for name, questions in QUESTION_SETS.items():
        print(f"  • {name}: {len(questions)} questions")

    # Check for custom sets
    custom_dir = Path("question_sets")
    if custom_dir.exists():
        custom_files = list(custom_dir.glob("*.json"))
        if custom_files:
            print("\nCustom Sets:")
            for filepath in custom_files:
                with open(filepath, "r") as f:
                    data = json.load(f)
                print(f"  • {data['name']}: {data['num_questions']} questions")


def export_all_predefined():
    """Export all predefined question sets to JSON files."""
    print("\n" + "=" * 60)
    print("Exporting Predefined Question Sets")
    print("=" * 60 + "\n")

    for name, questions in QUESTION_SETS.items():
        save_question_set(name, questions)

    print(f"\n✓ Exported {len(QUESTION_SETS)} question sets")


def main():
    """Main menu."""
    while True:
        print("\n" + "=" * 60)
        print("Med-GPT Question Set Manager")
        print("=" * 60)
        print("\n1. List available question sets")
        print("2. Export predefined sets to JSON")
        print("3. Create custom question set")
        print("4. Load question set")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            list_available_sets()
        elif choice == "2":
            export_all_predefined()
        elif choice == "3":
            create_custom_set()
        elif choice == "4":
            name = input("Enter question set name: ").strip()
            questions = load_question_set(name)
            if questions:
                print(f"\nQuestions:")
                for i, q in enumerate(questions, 1):
                    print(f"{i}. {q}")
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("\n✗ Invalid option")


if __name__ == "__main__":
    main()
