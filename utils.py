import yaml

def generate_initial_state():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config

if __name__ == "__main__":
    print(generate_initial_state())