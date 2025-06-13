# Respira Events Importer for Lu.ma

This project provides a web application to import Facebook events into Lu.ma calendars with enhanced data extraction.

## Features

- **Facebook Event Processing:** Extract event details from Facebook event URLs.
- **Lu.ma Integration:** Import processed event data directly into your Lu.ma calendar.
- **Customizable Host Information:** Configure host name, email, and bio for imported events.
- **Responsive Design:** Accessible on various devices.

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Deployment:** Vercel (Frontend), Railway (Backend)

## Setup and Deployment

### Prerequisites

- Node.js and npm (for frontend development, if running locally)
- Python 3.x and pip (for backend development, if running locally)
- Git
- Vercel CLI (for Vercel deployment)
- Railway CLI (for Railway deployment)

### Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/webmyc/respira-luma.git
    cd respira-luma
    ```

2.  **Frontend Setup (Vercel):**
    - Navigate to the `frontend` directory: `cd frontend`
    - Ensure your `vercel.json` is configured correctly for static file serving. The `outputDirectory` should be `static`.
    - Deploy to Vercel. Remember to set the "Root Directory" in Vercel project settings to `frontend/`.

3.  **Backend Setup (Railway):**
    - Navigate to the `backend` directory: `cd backend`
    - Install Python dependencies: `pip install -r requirements.txt`
    - Deploy to Railway. Ensure you generate a public domain for your Railway service.

4.  **Connect Frontend to Backend:**
    - Update the `API_BASE_URL` in `frontend/static/config.js` to point to your public Railway backend URL (e.g., `https://your-project-name.up.railway.app:8080`).

## Usage

1.  Open the deployed frontend application in your browser.
2.  Enter your Lu.ma API Key, Calendar ID, Host Name, Host Email, and Host Bio in the Configuration section.
3.  Enter a Facebook event URL in the "Facebook URL" field.
4.  Click "Process URL" to extract event details.
5.  Review the extracted event details and click "Import to Lu.ma" to create the event in your calendar.

## Contributing

Feel free to fork this repository and contribute. Pull requests are welcome.

## License

This project is licensed under the MIT License.


