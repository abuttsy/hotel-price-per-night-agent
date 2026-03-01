# Hotel Price Monitoring Automation (MCP)

This automation monitors a Notion database for hotel prices, scrapes official websites for the lowest family rates (2 adults + 1 child, age 2), converts the rates to EUR, and updates the database. It also sends email alerts for significant price swings (±20%).

## 🚀 Features
- **Notion Integration**: Automatically scans your "View All Hotels" database and handles pagination.
- **Regional Search Logic**: Automatically determines search dates based on hotel location (Europe, Caribbean/Mexico, Southeast Asia, Middle East).
- **Playwright Scraping**: Uses `playwright-stealth` to bypass bot detection.
- **Currency Conversion**: Converts all prices to EUR using a public API.
- **Email Alerts**: Notifies you of price changes ≥ 20%.
- **MCP Tool**: Can be triggered by a Notion Agent or other MCP clients.

---

## 🛠️ Setup Prerequisites

### 1. Notion Integration
1. Go to [Notion My Integrations](https://www.notion.so/my-integrations).
2. Create a new "Internal Integration" and copy the **Internal Integration Token**.
3. Open your "View All Hotels" database in Notion.
4. Click the three dots `...` in the top right -> `Connect to` -> Select your integration.
5. Copy the **Database ID** from the URL: `notion.so/username/DATABASE_ID?v=...`

### 2. Gmail App Password (for Alerts)
1. Go to your Google Account settings.
2. Enable **2-Step Verification**.
3. Search for **App Passwords**.
4. Create an app password (e.g., "Hotel Price Bot") and copy the 16-character code.

---

## 📦 Deployment (Railway.app)

1. **Connect Repository**: Point Railway to your GitHub repository.
2. **Set Environment Variables**: In the Railway "Variables" tab, add:
   - `NOTION_TOKEN`: Your Notion Integration Token.
   - `DATABASE_ID`: Your Notion Database ID.
   - `EMAIL_SENDER`: Your Gmail address.
   - `EMAIL_PASSWORD`: Your 16-character Gmail App Password.
   - `CUSTOM_AUTH_TOKEN`: A secret token of your choice to secure the MCP server.
   - `MCP_TRANSPORT`: `sse`
   - `PORT`: `8080` (or Railway's default)
3. **Public URL**: Your MCP server will be live at `https://your-app-name.up.railway.app/sse`.

---

## 🤖 Using with a Notion Agent

To trigger the automation, provide the public URL to your Notion Agent. You can then use the following tool:

**Tool Name**: `run_jules_script`

**Arguments**:
- `hotel_name` (optional): "Quellenhof"
- `hotel_url` (optional): "https://www.quellenhof.it/en"

If no arguments are provided, it will check all hotels in the database that haven't been updated in the last 365 days.

---

## 💻 Local Development

1. **Clone the repo**:
   ```bash
   git clone <repo-url>
   cd hotel-price-per-night-agent
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Set up .env**:
   Create a `.env` file with the variables listed in the Deployment section.
4. **Run the script**:
   ```bash
   python main.py
   ```

## 📂 Project Structure
- `main.py`: Main orchestration script.
- `mcp_server.py`: MCP server implementation (SSE/Stdio).
- `notion_manager.py`: Notion API interactions.
- `scraper.py`: Playwright scraping logic.
- `currency_converter.py`: Currency conversion logic.
- `email_manager.py`: SMTP email alerting logic.
- `Dockerfile`: Container configuration for deployment.
