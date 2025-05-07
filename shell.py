from datetime import date, timedelta
from models import HealthData
from extensions import db
from app import app

with app.app_context():
    # 删除 user_id=6 的旧数据
    deleted = HealthData.query.filter(HealthData.user_id == 6).delete()
    db.session.commit()
    print(f"🗑️ Deleted {deleted} old records for user 6")

    # 生成 2025-04-24 至 2025-05-07（14 天）的数据
    start_date = date(2025, 4, 24)
    all_days = [start_date + timedelta(days=i) for i in range(14)]

    records = []
    for d in all_days:
        records.append(HealthData(
            user_id=6,
            date=d,
            calories_intake=2000,
            calories_burned=2400,
            sleep_hours=7,
            workout_duration=35,
            steps=7600
        ))

    db.session.bulk_save_objects(records)
    db.session.commit()
    print("✅ Inserted 14-day dataset for user 6 (2025-04-24 ~ 2025-05-07)")
