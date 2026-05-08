# Kerala Election 2026 Dashboard

A real-time, interactive election dashboard for the Kerala Assembly Elections 2026. This project fetches and visualizes real-time election data to provide insights across different views: overall dashboard, constituency-wise, party-wise, and candidate-wise results.

## Features

*   **Real-Time Data:** Fetches live election data from the Open Data Kerala API.
*   **Comprehensive Views:**
    *   Dashboard
    *   Constituency-wise Results
    *   Party-wise Results
    *   Candidate Profiles
*   **Modern UI:** A responsive, high-performance, and visually appealing user interface.

## Tech Stack

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript
*   **Data Source:** [Open Data Kerala API](https://api.opendatakerala.org/api/kla2026/results/all.json)

## Setup Instructions

1.  Clone the repository:
    ```bash
    git clone https://github.com/Salvin-Sebastian/Election-2026.git
    cd Election-2026
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the Flask application:
    ```bash
    python app.py
    ```
4.  Open your browser and navigate to `http://127.0.0.1:5000`.

## Deployment

You can deploy this project to various cloud platforms:

*   **Railway:** Connect your GitHub repository to Railway. It will automatically detect your `requirements.txt` and `Procfile` to deploy the Flask application seamlessly.
*   **Vercel:** To deploy on Vercel, you will need a `vercel.json` file configured for the Python runtime to run the Flask app as a serverless function. Import the repository and deploy.
*   **Netlify:** While Netlify is primarily for static sites, you can deploy the static assets (HTML/CSS/JS) here and use Netlify Functions for the backend, or host the Flask backend separately (e.g., on Railway) and connect them.

## Credits

**Developed by: Salvin Sebastian**
