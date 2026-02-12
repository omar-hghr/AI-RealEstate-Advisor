# AI Real Estate Advisor

Smart Desktop App to Analyze Egyptian Real Estate Listings & Make Data-Driven Investment Decisions

AI Real Estate Advisor helps you rank properties based on expected ROI, risk level, budget, and personal preferences. It includes a lightweight adaptive learning agent that remembers your choices and personalizes recommendations over time.

100% Offline — No accounts, no internet required.

Features:

* ROI Calculation: Estimate rental yield and expected price growth.
* Risk Scoring: Assigns risk scores for properties and neighborhoods.
* Smart Ranking: Automatically ranks properties according to your preferences.
* Adaptive Learning: Learns from your activity and saves locally in learning.json.
* User-Friendly GUI: Simple, clean interface built with Tkinter.
* Flexible Data Input: Load property listings from Excel or CSV files.
* Export Recommendations: Save top options to Excel for further analysis.

How It Works:

1. Load property listings (Excel or CSV).
2. Preprocess and clean the data.
3. Calculate ROI and risk scores.
4. Rank properties based on your selected preferences: ROI, risk, budget, or a mix.
5. Save user behavior and preferences in learning.json.
6. Recommendations improve as the app learns your choices.

learning.json Explained:
Stores your activity locally:

* Properties you viewed or shortlisted
* Your preference for ROI vs. low risk
* Helps the app adjust future rankings according to your style

Example:
{
  "users": {
    "omar": {
      "w_roi": 0.4752475247524752,
      "w_risk": 0.297029702970297,
      "w_budget": 0.22772277227722773,
      "interactions": 1
    }
  }
}

Installation & Setup:

1. Clone the repository:
   git clone https://github.com/omar-hghr/Al-RealEstate-Advisor.git
   cd Al-RealEstate-Advisor
2. Create a virtual environment:
   python -m venv venv
3. Activate it:
   Windows: venv\Scripts\activate
   Linux/macOS: source venv/bin/activate
4. Install required packages:
   pip install -r requirements.txt
5. Run the application:
   python main.py

Important Notes:

* Not financial advice — for personal research and learning only.
* Real estate prices change fast — always verify current data.
* ROI and risk scores are estimates, not guarantees.

Project Type:
Decision Support System (DSS) with an Adaptive Learning Agent tailored for the Egyptian real estate market.

Benefits:

* Make faster, data-driven investment decisions
* Identify high-ROI and low-risk properties easily
* Get smarter, personalized recommendations the more you use it
* Offline, private, and secure — all data stays on your computer

## License

MIT License

See the [LICENSE](LICENSE) file for full details.

Author:
Omar Haitham
GitHub: @omar-hghr

If you find this project useful, please Star the repo!
