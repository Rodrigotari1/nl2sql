# Natural Language SQL Tool 🗃️

Convert natural language questions into PostgreSQL queries using GPT-4o-mini. This tool provides a web interface where users can connect to their PostgreSQL database, ask questions in plain English, and get back SQL queries with explanations and safe execution.

## Features

- 🧠 **Natural Language Processing**: Convert English questions to SQL using GPT-4o-mini
- 🔒 **Safety First**: Query validation, execution limits, and safety warnings
- 📊 **Schema Awareness**: Automatically discovers database structure for accurate queries
- 🌐 **Web Interface**: Clean, modern UI with real-time query generation
- ⚡ **Fast Execution**: Optimized query execution with timeout protection
- 📈 **Result Visualization**: Formatted tables with export capabilities

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key

### Installation

1. **Clone and install dependencies:**
```bash
git clone <your-repo>
cd nl2sql
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "DATABASE_URL=postgresql://username:password@localhost:5432/database_name" >> .env
```

3. **Create demo database (optional):**
```bash
# Create a PostgreSQL database first, then:
python scripts/setup_demo_db.py "postgresql://username:password@localhost:5432/demo_db"
```

4. **Start the server:**
```bash
python main.py
# Or run directly:
python scripts/run.py
# Or with uvicorn:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Open your browser:**
Visit `http://localhost:8000` to use the web interface.

## Usage

### Web Interface

1. **Connect Database**: Enter your PostgreSQL connection string
2. **Ask Questions**: Type natural language queries like:
   - "Show me all users created this month"
   - "What are the top 10 products by sales?"
   - "Which customers haven't ordered in 3 months?"
3. **Review SQL**: Check the generated SQL and explanation
4. **Execute Safely**: Run queries with built-in safety limits

### API Endpoints

- `POST /api/connect` - Test database connection
- `POST /api/schema` - Get database schema information
- `POST /api/generate-query` - Convert natural language to SQL
- `POST /api/execute-query` - Execute SQL queries safely
- `GET /api/health` - Health check

### Example API Usage

```bash
# Test connection
curl -X POST "http://localhost:8000/api/connect" \
  -H "Content-Type: application/json" \
  -d '{"database_url": "postgresql://user:pass@localhost/db"}'

# Generate SQL
curl -X POST "http://localhost:8000/api/generate-query" \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "Show me all users",
    "database_url": "postgresql://user:pass@localhost/db"
  }'
```

## Architecture

### Backend Components

- **`main.py`** - FastAPI application with API endpoints
- **`models.py`** - Pydantic data models and schemas
- **`database_service.py`** - PostgreSQL connection and query execution
- **`llm_service.py`** - OpenAI integration for SQL generation
- **`config.py`** - Configuration management

## Safety Features

- **Query Type Detection**: Only allows SELECT statements by default
- **Execution Limits**: 30-second timeout, 1000-row limit
- **Safety Warnings**: Alerts for potentially expensive operations
- **Connection Validation**: Tests database connectivity before operations
- **Error Handling**: Graceful failure with helpful error messages

## Demo Database Schema

The demo database includes:

- **users** - User accounts with creation dates
- **products** - Product catalog with prices and categories
- **orders** - Customer orders with totals and dates
- **order_items** - Order line items with quantities

Perfect for testing queries like:
- Customer analysis
- Sales reporting
- Product performance
- Order history

## Development

### Running Tests

```bash
# Run basic tests
python tests/test_api.py

# Run with pytest
pytest tests/test_api.py -v
```

### Project Structure

```
nl2sql/
├── app/                      # Main application package
│   ├── api/                  # API endpoints and routing
│   │   └── endpoints.py      # FastAPI route handlers
│   ├── services/             # Business logic services
│   │   ├── database_service.py  # PostgreSQL operations
│   │   └── llm_service.py       # OpenAI integration
│   ├── models/               # Data models and schemas
│   │   └── schemas.py        # Pydantic models
│   ├── core/                 # Core configuration
│   │   └── config.py         # Environment and settings
│   └── main.py               # FastAPI application
├── tests/                    # Test suite
│   └── test_api.py          # API and service tests
├── scripts/                  # Utility scripts
│   ├── setup_demo_db.py     # Demo database creation
│   └── run.py               # Application startup
├── static/                   # Frontend assets
│   └── index.html           # Web interface
├── main.py                  # Main entry point
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Adding New Features

1. **New Models**: Add to `app/models/schemas.py` with Pydantic validation
2. **Database Operations**: Extend `app/services/database_service.py` with new methods
3. **API Endpoints**: Add to `app/api/endpoints.py` following existing patterns
4. **Business Logic**: Create new services in `app/services/`
5. **Configuration**: Update `app/core/config.py` for new settings
6. **Frontend**: Modify `static/index.html` for UI changes

## Configuration

Environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DATABASE_URL` - Default PostgreSQL connection string
- `MAX_QUERY_TIMEOUT` - Query timeout in seconds (default: 30)
- `MAX_RESULT_ROWS` - Maximum rows returned (default: 1000)

## Troubleshooting

### Common Issues

**Connection Failed**
- Check PostgreSQL is running
- Verify connection string format
- Ensure database exists and credentials are correct

**OpenAI API Errors**
- Verify API key is set correctly
- Check API quota and billing
- Ensure internet connectivity

**Query Generation Issues**
- Complex queries might need manual refinement
- Very large schemas may hit token limits
- Try breaking complex questions into simpler parts

### Performance Tips

- Use specific table/column names in questions
- Add time ranges to queries on large tables
- Consider adding indexes for frequently queried columns

## Cost Estimation

- **Development/Testing**: $2-5 per week
- **Light Production**: $10-20 per month
- **Heavy Usage**: Scales with query volume

GPT-4o-mini is cost-effective for most use cases.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding principles
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Create an issue with detailed information

---

Built with ❤️ using FastAPI, PostgreSQL, and OpenAI GPT-4o-mini 