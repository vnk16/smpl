from fastapi import APIRouter
from models.models import DurationRequest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

router = APIRouter()

# Generate dummy data for 12 months
months = pd.date_range(start='2024-01-01', periods=12, freq='MS')
user_data = []
for month in months:
    total_users = np.random.randint(400, 1001)  # 400 to 1000
    active_users = np.random.randint(0, total_users + 1)
    user_data.append({
        'month': month.strftime('%Y-%m'),
        'total_users': total_users,
        'active_users': active_users
    })
df = pd.DataFrame(user_data)

def plot_graph(y, title, filename):
    plt.figure(figsize=(10,5))
    plt.plot(df['month'], y, marker='o')
    plt.title(title)
    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

@router.post("/user-graph")
async def user_graph(request: DurationRequest):
    if request.duration != "monthly":
        return {"error": "Only 'monthly' duration is supported."}

    # Graph plotting
    plot_graph(df['total_users'], "Total Users per Month", "total_users.png")
    plot_graph(df['active_users'], "Active Users per Month", "active_users.png")

    total_users_list = [
        {
            "month": row['month'],
            "count": row['total_users']
        }
        for _, row in df.iterrows()
    ]
    active_users_list = [
        {
            "month": row['month'],
            "count": row['active_users']
        }
        for _, row in df.iterrows()
    ]
    return {
        "total_users": total_users_list,
        "active_users": active_users_list
    }
