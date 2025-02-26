import yaml
from pprint import pprint
from node_models import AgentRunningState
def load_config():
    # Each config file will generate a different scenarios ~1440
    with open("config.yaml", "r") as f:
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

    # Use itertools.product to combine them
    all_scenarios = []
    for (topic, tense, perspective, gender, age, edu_level, cs_ratio) in itertools.product(
        topics, tenses, perspectives, genders, ages, edu_levels, cs_ratios
    ):
        scenario = {
            "topic": topic,
            "tense": tense,
            "perspective": perspective,
            "gender": gender,
            "age": age,
            "education_level": edu_level,
            # If needed, you can also include the other single-value config fields:
            "cs_ratio": cs_ratio,
            "use_tools": config["use_tools"],
            # ...
            "first_language": config["character_setting"]["nationality"]["first_language"],
            "second_language": config["character_setting"]["nationality"]["second_language"],
        }
        all_scenarios.append(scenario)

    return all_scenarios

if __name__ == "__main__":
    # Here is your config dictionary (simplified for the example):
    config = {
        'character_setting': {
            'age': ['8-17', '18-25', '26-35', '56-65', '66+'],
            'education_level': ['High School','College','Master','Doctor'],
            'gender': ['Male','Female'],
            'nationality': {
                'first_language': 'Cantonese',
                'second_language': 'English'
            }
        },
        'cs_ratio': 0.5,
        'output_format': 'json',
        'output_type': 'single_turn',
        'perspective': ['First Person','Third Person'],
        'tense': ['Past','Present','Future'],
        'topics': ['Tourism','Weather','Shopping','Food','Exam','Politics'],
        'use_tools': True
    }

    scenarios = generate_scenarios(config)
    print(f"Generated {len(scenarios)} scenario combinations.")
    # For a quick peek, let's print the first few
    for i, sc in enumerate(scenarios[:10]):
        print(f"Scenario #{i+1}:", sc)
        print("\n")
