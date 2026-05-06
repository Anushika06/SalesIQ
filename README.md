# SalesIQ 🚀
**Making AI-Powered Sales Outreach Smarter, Personal, and Human.**

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Firebase](https://img.shields.io/badge/firebase-%23039BE5.svg?style=for-the-badge&logo=firebase)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

---

## 🛑 The Problem
Modern sales pipelines are polluted with generic, mass-blast cold messages. This spray-and-pray approach yields abysmal conversion rates because the outreach feels robotic, thoughtless, and completely disconnected from the prospect's actual needs. Traditional tools focus on volume over quality, leaving potential leads annoyed and alienated.

## 💡 The Solution: SalesIQ
**SalesIQ** flips the script on traditional cold outreach. Instead of treating prospects like numbers on a spreadsheet, SalesIQ leverages the reasoning capabilities of generative AI to deeply research leads, understand their pain points, and craft genuinely personalized communications. It brings the "human" element back to sales by empowering reps with the intelligence and context they need to build real relationships.

## Key Features
*   **Prospect Research Engine (Overview):** Powered by Gemini 2.5, this engine instantly synthesizes available data into highly actionable, personalized talking points, comprehensive company summaries, and tailored value propositions.
*   **AI Message Optimizer:** Say goodbye to generic templates. Paste a rough draft, and the AI Message Optimizer rewrites it on the fly—injecting specific personalization, emotional hooks, and tailored value propositions designed to resonate with the recipient.
*   **Real-Time Data Sync:** The application utilizes Firebase Firestore `onSnapshot` listeners to provide a lightning-fast, reactive user experience. Any updates to a lead's history or call briefs are instantly reflected in the UI without a page refresh.

## 🛠 Tech Stack
*   **Frontend:** React, Vite, Tailwind CSS
*   **Backend & Database:** Firebase (Firestore)
*   **AI Integration:** Google Gemini 2.5 API


## 🚀 Getting Started

Follow these steps to run SalesIQ locally:

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd SalesIQ/apps/web
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Create a `.env` file in the root of the `web` directory and add your Firebase configurations:
```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
# Add any other required keys
```

### 4. Run the Development Server
```bash
npm run dev
```
Navigate to `http://localhost:5173` (or the port specified by Vite) in your browser to view the application.
