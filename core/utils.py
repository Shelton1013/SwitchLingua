import yaml
from pprint import pprint
from node_models import AgentRunningState
import jsonlines as jsl

def load_config(config_path: str):
    # Each config file will generate a different scenarios ~1440
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config


import itertools


def generate_scenarios(config: dict) -> list[AgentRunningState]:
    """
    Given a config dict, produce all possible scenario combinations
    by taking the Cartesian product of relevant lists:
      - topics
      - tense
      - perspective
      - gender
      - age
      - education_level
    """
    # For quick reference
    topics = config["topics"]
    tenses = config["tense"]
    perspectives = config["perspective"]
    genders = config["character_setting"]["gender"]
    ages = config["character_setting"]["age"]
    edu_levels = config["character_setting"]["education_level"]
    cs_ratios = config["cs_ratio"]
    conversation_types = config["conversation_type"]
    cs_functions = config["cs_function"]
    cs_types = config["cs_type"]

    # Use itertools.product to combine them
    all_scenarios = []
    for (
        topic,
        tense,
        perspective,
        gender,
        age,
        edu_level,
        cs_ratio,
        conversation_type,
        cs_function,
        cs_type,
    ) in itertools.product(
        topics,
        tenses,
        perspectives,
        genders,
        ages,
        edu_levels,
        cs_ratios,
        conversation_types,
        cs_functions,
        cs_types,
    ):
        scenario = {
            "topic": topic,
            "tense": tense,
            "perspective": perspective,
            "gender": gender,
            "age": age,
            "education_level": edu_level,
            "cs_ratio": cs_ratio,
            "use_tools": config["use_tools"],
            "conversation_type": conversation_type,
            "first_language": config["character_setting"]["nationality"][
                "first_language"
            ],
            "second_language": config["character_setting"]["nationality"][
                "second_language"
            ],
            "cs_function": cs_function,
            "cs_type": cs_type,
        }
        all_scenarios.append(scenario)

    return all_scenarios





def weighting_scheme(state):
    fluency = state["fluency_result"]["fluency_score"]
    naturalness = state["naturalness_result"]["naturalness_score"]
    csratio = state["cs_ratio_result"]["ratio_score"]
    socio = state["social_cultural_result"]["socio_cultural_score"]
    return fluency * 0.3 + naturalness * 0.25 + csratio * 0.2 + socio * 0.25


if __name__ == "__main__":
    # Here is your config dictionary (simplified for the example):
    config = {
        "character_setting": {
            "age": ["8-17", "18-25", "26-35", "56-65", "66+"],
            "education_level": ["High School", "College", "Master", "Doctor"],
            "gender": ["Male", "Female"],
            "nationality": {
                "first_language": "Cantonese",
                "second_language": "English",
            },
        },
        "cs_function": [
            "Directive",
            "Expressive",
            "Referential",
            "Phatic",
            "Metalinguistic",
            "Poetic",
        ],
        "cs_type": [
            "Intersentential",
            "Intrasentential",
            "Extra-sentential / Tag switching",
        ],
        "cs_ratio": ["Low", "Medium", "High"],
        "output_format": "json",
        "output_type": "single_turn",
        "perspective": ["First Person", "Third Person"],
        "tense": ["Past", "Present", "Future"],
        "topics": ["Tourism", "Weather", "Shopping", "Food", "Exam", "Politics"],
        "use_tools": True,
        "conversation_type": ["single_turn", "multi-turn"],
    }

    scenarios = generate_scenarios(config)
    print(f"Generated {len(scenarios)} scenario combinations.")
    # For a quick peek, let's print the first few
    for i, sc in enumerate(scenarios[:10]):
        print(f"Scenario #{i+1}:", sc)
        print("\n")
