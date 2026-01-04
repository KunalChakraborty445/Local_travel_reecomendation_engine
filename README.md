Local Travel Recommendation Engine
📌 Project Overview

This project is a simple travel recommendation engine built using Python and Pandas.
It recommends top weekend travel destinations in India based on:

📏 Distance

⭐ Rating

🔥 Popularity

The user provides a Source City, and the system ranks nearby destinations accordingly.

🛠️ Technologies Used

Python

Pandas

📂 Project Structure
travel-recommendation/
│
├── india_must_see_places.csv
├── travel_recommender.py
├── requirements.txt
├── sample_output.txt
├── screenshots/
│   ├── output_delhi.png
│   ├── output_mumbai.png
│   └── output_bangalore.png
└── README.md

⚙️ How the Recommendation Works

Takes Source City as input

Removes the source city from destination list

Calculates distance using latitude & longitude difference

Normalizes:

Distance

Rating

Popularity

Calculates a final weighted score

Sorts and displays top weekend destinations

▶️ How to Run the Project
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Run the program
python travel_recommender.py

🧪 Sample Cities Tested

Delhi

Mumbai

Bangalore

📊 Sample Output Screenshots
🔹 Output for Delhi

🔹 Output for Mumbai

🔹 Output for Bangalore

📌 Note:
Take screenshots of your terminal output and save them inside the screenshots/ folder with the same names.
