# Deploying the Hotel Price Automation MCP Server

To use this automation with a Notion Agent or any MCP-compatible client, you need to host this server and provide its public URL.

## 1. Hosting Options

### Option A: Fly.io (Recommended for Docker)
1. Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/).
2. Run `fly launch` in this directory.
3. When prompted, add your environment variables:
   - `NOTION_TOKEN`
   - `DATABASE_ID`
   - `EMAIL_SENDER`
   - `EMAIL_PASSWORD`
   - `MCP_TRANSPORT=sse`
   - `MCP_PORT=8080`
4. Your public URL will be: `https://<your-app-name>.fly.dev/sse`

### Option B: Railway / Render
1. Connect this GitHub repository to Railway or Render.
2. Set the "Start Command" to: `python mcp_server.py`
3. Add the environment variables listed above.
4. Set `MCP_TRANSPORT=sse`.
5. Your public URL will be: `https://<your-app-url>/sse`

## 2. Environment Variables Required
| Variable | Description |
| --- | --- |
| `NOTION_TOKEN` | Your Notion Integration Token |
| `DATABASE_ID` | The ID of your "View All Hotels" database |
| `EMAIL_SENDER` | Gmail address for alerts |
| `EMAIL_PASSWORD` | Gmail App Password |
| `EMAIL_RECEIVER` | (Optional) Recipient for alerts |
| `MCP_TRANSPORT` | Set to `sse` for web-based MCP access |
| `MCP_PORT` | Port for the server (default: 8000) |

## 3. Tool Details
- **Tool Name**: `run_jules_script`
- **Arguments**:
  - `hotel_name` (string, optional): The name of the hotel to update.
  - `hotel_url` (string, optional): The official website URL of the hotel.
