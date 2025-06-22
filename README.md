# Message Auto-Forwarding AI Agent

A sophisticated AI-powered message forwarding system that intelligently automates cross-platform communication using advanced web automation and machine learning capabilities.

## Overview

The Message Auto-Forwarding AI Agent is an enterprise-grade solution designed to streamline communication workflows across multiple messaging platforms. By leveraging Selenium-based web automation and intelligent filtering algorithms, this system provides seamless message routing with minimal manual intervention.

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Web Dashboard │    REST API     │  CLI Interface  │    WebSocket Server     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                     │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│ Authentication  │   Rule Engine   │ Task Scheduler  │  AI Processing Engine   │
│    Service      │                 │                 │                         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            CORE SERVICES                                       │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│ Message Handler │ Filter Engine   │ Message Router  │   Health Monitor        │
│                 │                 │                 │                         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        PLATFORM CONNECTORS                                     │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│    Telegram     │    WhatsApp     │     Slack       │       Discord           │
│   Connector     │   Connector     │   Connector     │     Connector           │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                          │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │   Redis Cache   │   Log Storage   │   File Storage          │
│   Database      │                 │                 │                         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL PLATFORMS                                      │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│    Telegram     │  WhatsApp Web   │ Slack Workspace │   Discord Server        │
│     API         │                 │                 │                         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

### Message Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Source Platform│    │ Platform        │    │ AI Content      │
│                 │───▶│ Connector       │───▶│ Analyzer        │
│ • Telegram      │    │                 │    │                 │
│ • WhatsApp      │    │ • Extract       │    │ • Classification│
│ • Slack         │    │ • Parse         │    │ • Sentiment     │
│ • Discord       │    │ • Normalize     │    │ • Priority      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Target Platform │    │ Message         │    │ Filter Engine   │
│                 │◀───│ Router          │◀───│                 │
│ • Telegram      │    │                 │    │ • Keyword Match │
│ • WhatsApp      │    │ • Queue         │    │ • Sender Rules  │
│ • Slack         │    │ • Retry         │    │ • Time Windows  │
│ • Discord       │    │ • Track         │    │ • Custom Logic  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & LOGGING                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Delivery Status │ Performance     │ Error Tracking & Analytics  │
│ • Success/Fail  │ • Latency       │ • Failed Messages           │
│ • Retry Count   │ • Throughput    │ • System Health             │
│ • Timestamps    │ • Queue Size    │ • Usage Statistics          │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Data Processing Pipeline

```
INPUT SOURCES                PROCESSING PIPELINE               OUTPUT DESTINATIONS
┌─────────────┐             ┌─────────────────────┐            ┌─────────────┐
│ Telegram    │────────────▶│                     │───────────▶│ Telegram    │
│ Messages    │             │   Message           │            │ Channels    │
└─────────────┘             │   Ingestion         │            └─────────────┘
                            │                     │
┌─────────────┐             │ ┌─────────────────┐ │            ┌─────────────┐
│ WhatsApp    │────────────▶│ │ AI Analysis     │ │───────────▶│ WhatsApp    │
│ Messages    │             │ │ • NLP           │ │            │ Contacts    │
└─────────────┘             │ │ • Classification│ │            └─────────────┘
                            │ │ • Sentiment     │ │
┌─────────────┐             │ └─────────────────┘ │            ┌─────────────┐
│ Slack       │────────────▶│                     │───────────▶│ Slack       │
│ Messages    │             │ ┌─────────────────┐ │            │ Channels    │
└─────────────┘             │ │ Rule Engine     │ │            └─────────────┘
                            │ │ • Conditions    │ │
┌─────────────┐             │ │ • Filters       │ │            ┌─────────────┐
│ Discord     │────────────▶│ │ • Routing Logic │ │───────────▶│ Discord     │
│ Messages    │             │ └─────────────────┘ │            │ Servers     │
└─────────────┘             │                     │            └─────────────┘
                            │ ┌─────────────────┐ │
                            │ │ Priority Queue  │ │
                            │ │ • High Priority │ │
                            │ │ • Normal Queue  │ │
                            │ │ • Retry Queue   │ │
                            │ └─────────────────┘ │
                            └─────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │ STORAGE & ANALYTICS │
                            ├─────────────────────┤
                            │ • Message Logs      │
                            │ • Performance Data  │
                            │ • Error Reports     │
                            │ • Usage Statistics  │
                            └─────────────────────┘
```

### Component Interaction Flow

```
WEB INTERFACE                API LAYER                 BUSINESS LOGIC
┌─────────────┐             ┌─────────────┐            ┌─────────────┐
│ Dashboard   │◀───────────▶│ REST API    │◀──────────▶│ Rule Engine │
│ UI          │             │ Endpoints   │            │             │
└─────────────┘             └─────────────┘            └─────────────┘
                                   │                           │
┌─────────────┐             ┌─────────────┐            ┌─────────────┐
│ Config      │◀───────────▶│ WebSocket   │◀──────────▶│ AI          │
│ Panel       │             │ Handler     │            │ Processor   │
└─────────────┘             └─────────────┘            └─────────────┘
                                   │                           │
┌─────────────┐             ┌─────────────┐            ┌─────────────┐
│ Analytics   │◀───────────▶│ Webhook     │◀──────────▶│ Job         │
│ View        │             │ Receiver    │            │ Scheduler   │
└─────────────┘             └─────────────┘            └─────────────┘
                                                               │
                                                               ▼
INTEGRATION LAYER                                      STORAGE LAYER
┌─────────────┐  ┌─────────────┐  ┌─────────────┐    ┌─────────────┐
│ Selenium    │  │ Telegram    │  │ Slack API   │    │ PostgreSQL  │
│ WebDriver   │  │ Bot API     │  │ Client      │    │ Database    │
└─────────────┘  └─────────────┘  └─────────────┘    └─────────────┘
       │                │                │                    │
       └────────────────┼────────────────┘                    │
                        │                                     │
                ┌─────────────┐                       ┌─────────────┐
                │ Discord API │                       │ Redis       │
                │ Client      │                       │ Cache       │
                └─────────────┘                       └─────────────┘
                                                             │
                                                     ┌─────────────┐
                                                     │ File        │
                                                     │ Storage     │
                                                     └─────────────┘
```


## Key Features

### 🤖 AI-Powered Intelligence
- **Smart Content Analysis**: AI-driven message classification and routing
- **Context-Aware Filtering**: Intelligent message prioritization based on content and sender patterns
- **Adaptive Learning**: System improves forwarding accuracy over time

### 🔗 Multi-Platform Integration
- **Telegram**: Full API integration with bot support
- **WhatsApp**: Web-based automation with message parsing
- **Slack**: Workspace integration with channel management
- **Discord**: Server and DM forwarding capabilities

### ⚙️ Advanced Automation
- **Rule-Based Forwarding**: Create complex forwarding rules with conditional logic
- **Keyword Filtering**: Advanced pattern matching and regex support
- **Sender Whitelisting/Blacklisting**: Granular control over message sources
- **Time-Based Scheduling**: Configure forwarding windows and frequency limits

### 🎛️ Management & Monitoring
- **Web Dashboard**: Intuitive interface for configuration and monitoring
- **Real-Time Analytics**: Message flow statistics and performance metrics
- **Comprehensive Logging**: Detailed audit trails with error tracking
- **Health Monitoring**: System status and platform connectivity checks

## Architecture

### Technology Stack
- **Backend Framework**: Flask (Python 3.8+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Web Automation**: Selenium WebDriver with Chrome/Firefox support
- **Task Scheduling**: APScheduler for robust job management
- **Frontend**: Bootstrap 5, Chart.js for analytics
- **Security**: JWT authentication, encrypted credential storage

### System Requirements
- **Python**: 3.8 or higher
- **Database**: PostgreSQL 12+
- **Browser**: Chrome 90+ or Firefox 88+
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: 1GB free space for logs and temporary files

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/danieladdisonorg/Message-Auto-Forwarding-AI-Agent.git
   ```

2. **Navigate to project directory**
   ```bash
   cd Message-Auto-Forwarding-AI-Agent
   ```

3. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Set up environment variables**
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/message_forwarder"
   export SESSION_SECRET="your-secure-session-key-here"
   export FLASK_ENV="production"
   export LOG_LEVEL="INFO"
   ```

2. **Initialize database**
   ```bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

3. **Configure WebDriver**
   - Download ChromeDriver or GeckoDriver
   - Add driver executable to PATH or specify path in configuration

### Running the Application

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Access the web interface**
   - Open your browser and navigate to `http://localhost:5000`
   - Complete the initial setup wizard
   - Configure your messaging platforms

## Usage Guide

### Setting Up Platforms

1. **Navigate to Platform Configuration**
2. **Add New Platform**: Select from supported platforms
3. **Authentication**: Follow platform-specific authentication steps
4. **Test Connection**: Verify connectivity before proceeding

### Creating Forwarding Rules

1. **Access Rules Management**
2. **Define Source and Destination**: Select platforms and channels
3. **Set Filters**: Configure keyword filters, sender rules, and conditions
4. **Schedule**: Set forwarding frequency and time windows
5. **Activate Rule**: Enable the forwarding rule

### Monitoring and Analytics

- **Dashboard**: Real-time message flow statistics
- **Logs**: Detailed forwarding history and error reports
- **Performance**: System health and response time metrics

## API Documentation

The system provides RESTful APIs for programmatic access:

- `GET /api/platforms` - List configured platforms
- `POST /api/rules` - Create forwarding rules
- `GET /api/logs` - Retrieve forwarding logs
- `GET /api/health` - System health check

Full API documentation available at `/api/docs` when running.

## Security Considerations

- **Credential Encryption**: All platform credentials are encrypted at rest
- **Secure Sessions**: JWT-based authentication with configurable expiration
- **Rate Limiting**: Built-in protection against API abuse
- **Audit Logging**: Comprehensive security event logging

## Troubleshooting

### Common Issues

**WebDriver Connection Errors**
- Ensure browser and driver versions are compatible
- Check that the driver executable is in PATH

**Database Connection Issues**
- Verify PostgreSQL service is running
- Check DATABASE_URL format and credentials

**Platform Authentication Failures**
- Review platform-specific authentication requirements
- Check for expired tokens or changed credentials

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code style and standards
- Pull request process
- Issue reporting
- Development setup

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Wiki](https://github.com/danieladdisonorg/Message-Auto-Forwarding-AI-Agent/wiki)
- **Issues**: [GitHub Issues](https://github.com/danieladdisonorg/Message-Auto-Forwarding-AI-Agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/danieladdisonorg/Message-Auto-Forwarding-AI-Agent/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and updates.

---

**⚠️ Disclaimer**: This tool is designed for legitimate automation purposes. Users are responsible for complying with the terms of service of all connected platforms and applicable laws and regulations.
