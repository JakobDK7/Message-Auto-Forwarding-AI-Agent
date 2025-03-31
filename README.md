# Message Auto-Forwarding System

An automated Python-based message forwarding system leveraging Selenium for web automation, designed to connect and manage multiple messaging platforms efficiently.

## Key Features

- **Multi-Platform Support**: Connect to Telegram, WhatsApp, Slack, and Discord
- **Automated Forwarding**: Set up rules to automatically forward messages between platforms
- **Customizable Filters**: Filter messages based on keywords, senders, and more
- **Scheduling**: Configure when and how often messages are forwarded
- **Web Interface**: Easy-to-use web interface for managing platforms and rules
- **Detailed Logging**: Track all forwarded messages and any errors

## Technology Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Web Automation**: Selenium WebDriver
- **Scheduling**: Python Schedule library
- **Frontend**: Bootstrap CSS, JavaScript

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Chrome/Firefox browser for Selenium

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/message-forwarder.git
   cd message-forwarder
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```
   export DATABASE_URL="postgresql://username:password@localhost/database_name"
   export SESSION_SECRET="your_secret_key"
   ```

4. Run the application
   ```
   python main.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## License

[MIT License](LICENSE)