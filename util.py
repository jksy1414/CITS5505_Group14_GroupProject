#util.py for computing radar scores

def normalize_score(value, target, max_value):
    if value <= target:
        return round((value / target) * 100)
    elif value >= max_value:
        return 100
    else:
        return round(100 - ((value - target) / (max_value - target)) * 100)
    

def calculate_health_score(data):
    weights = {
        'calories_intake': 0.2,
        'sleep_hours': 0.2,
        'workout_duration': 0.2,
        'calories_burned': 0.2,
        'steps': 0.2
    }
    targets = {
        'calories_intake': 2000,
        'sleep_hours': 8,
        'workout_duration': 30,
        'calories_burned': 300,
        'steps': 8000
    }
    max_value = {
        'calories_intake': 2500,
        'sleep_hours': 8,
        'workout_duration': 30,
        'calories_burned': 300,
        'steps': 8000
    }

    scores= {}
    total = 0

    for key in weights:
        score = normalize_score(data[key], targets[key], max_value[key])
        scores[key] =score
        total += score * weights[key]

    return round(total, 1), scores


def aggregate_week_data(week_data_list):
    if not week_data_list:
        return None

    total = {
        'calories_intake': 0,
        'sleep_hours': 0,
        'workout_duration': 0,
        'calories_burned': 0,
        'steps': 0
    }
    count = 0

    for data in week_data_list:
        total['calories_intake'] += data.calories_intake or 0
        total['sleep_hours'] += data.sleep_hours or 0
        total['workout_duration'] += data.workout_duration or 0
        total['calories_burned'] += data.calories_burned or 0
        total['steps'] += data.steps or 0
        count += 1

    return {
        key: round(total[key] / count, 2) for key in total
    }