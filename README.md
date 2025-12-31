# AI Data Analysis Assistant

A Streamlit application that uses OpenAI to generate and execute pandas code for data analysis. Upload a CSV file, ask questions in natural language, and get instant analysis with visualizations.

## Features

- 📁 **CSV File Upload** - Easy file upload interface
- 👀 **Data Preview** - View first 10 rows and data statistics
- 💬 **Natural Language Queries** - Ask questions like "What are the top 5 products by revenue?"
- 🤖 **AI-Powered Code Generation** - Uses OpenAI GPT-4 to generate pandas code
- ⚙️ **Safe Code Execution** - Executes generated code in a restricted environment
- 📊 **Multiple Output Formats** - Results displayed as tables, charts, or text
- 💻 **Code Learning** - View generated code to learn pandas techniques
- 📚 **Code History** - Keep track of previous analyses

## Requirements

- Python 3.11+ (or Python 3.12)
- OpenAI API key
- Streamlit
- Pandas
- Plotly

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key:**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   
   Or set it as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Upload a CSV file** using the file uploader

3. **Review the data preview** to understand your dataset

4. **Ask questions** about your data, for example:
   - "What are the top 5 products by revenue?"
   - "Show me a trend chart of sales over time"
   - "What is the average value by category?"
   - "Create a bar chart of total sales by region"

5. **View results** - The app will:
   - Generate pandas code to answer your question
   - Execute the code safely
   - Display results (tables, charts, or text)
   - Show the generated code for learning

## Example Questions

The app can handle various types of data analysis questions:

- **Aggregations**: "What is the total revenue by category?"
- **Rankings**: "Show me the top 10 customers by purchase amount"
- **Time Series**: "Create a line chart showing sales trends over time"
- **Comparisons**: "Compare average sales across different regions"
- **Filtering**: "What are the products with sales above $1000?"

## Safety Features

- Code execution is restricted to safe pandas and plotly operations
- Dangerous built-in functions are blocked
- Only allowed imports (pandas, plotly) are available
- Errors are caught and displayed safely

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
├── .env.example       # Environment variable template
└── LICENSE            # MIT License
```

## Notes

- The app uses GPT-4 for code generation. Make sure you have API credits available.
- Large CSV files may take longer to process.
- The generated code is displayed so you can learn and modify it if needed.

## License

MIT License - see LICENSE file for details.

