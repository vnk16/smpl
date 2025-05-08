from flask import Flask, jsonify
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Dummy Data
data = {
    "total_users": [
        { "month": "Jan", "count": 500 },
        { "month": "Feb", "count": 1000 },
        { "month": "Mar", "count": 1500 },
        { "month": "Apr", "count": 2000 },
        { "month": "May", "count": 2500 },
        { "month": "Jun", "count": 3000 },
        { "month": "Jul", "count": 3500 },
        { "month": "Aug", "count": 4000 },
        { "month": "Sep", "count": 4500 },
        { "month": "Oct", "count": 5000 },
        { "month": "Nov", "count": 5500 },
        { "month": "Dec", "count": 6000 }
    ],
    "active_users": [
        { "month": "Jan", "count": 200 },
        { "month": "Feb", "count": 220 },
        { "month": "Mar", "count": 250 },
        { "month": "Apr", "count": 300 },
        { "month": "May", "count": 320 },
        { "month": "Jun", "count": 350 },
        { "month": "Jul", "count": 400 },
        { "month": "Aug", "count": 420 },
        { "month": "Sep", "count": 450 },
        { "month": "Oct", "count": 480 },
        { "month": "Nov", "count": 500 },
        { "month": "Dec", "count": 550 }
    ]
}

# Function to generate graph for total users
def generate_total_users_graph():
    months = [entry['month'] for entry in data['total_users']]
    total_users = [entry['count'] for entry in data['total_users']]

    fig, ax = plt.subplots()
    ax.plot(months, total_users, label="Total Users", color='b')
    ax.set(xlabel='Month', ylabel='Total User Count',
           title='Total Users Over Time')
    ax.legend()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)  # Rewind the image file pointer to the beginning
    return img

# Function to generate graph for active users
def generate_active_users_graph():
    months = [entry['month'] for entry in data['active_users']]
    active_users = [entry['count'] for entry in data['active_users']]

    fig, ax = plt.subplots()
    ax.plot(months, active_users, label="Active Users", color='g')
    ax.set(xlabel='Month', ylabel='Active User Count',
           title='Active Users Over Time')
    ax.legend()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)  # Rewind the image file pointer to the beginning
    return img

# API Route to get user data and separate graphs
@app.route('/api/user_data', methods=['GET','POST'])
def get_user_data():
    # Generate graphs for total users and active users
    total_users_img = generate_total_users_graph()
    active_users_img = generate_active_users_graph()

    # Convert both images to base64
    total_users_img_base64 = base64.b64encode(total_users_img.getvalue()).decode('utf-8')
    active_users_img_base64 = base64.b64encode(active_users_img.getvalue()).decode('utf-8')

    return jsonify({
        "total_users": data["total_users"],
        "active_users": data["active_users"],
        "total_users_graph": total_users_img_base64,  # Base64 encoded image for total users
        "active_users_graph": active_users_img_base64  # Base64 encoded image for active users
    })

if __name__ == '__main__':
    app.run(debug=True)
