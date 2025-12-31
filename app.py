import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import os
from dotenv import load_dotenv
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Load environment variables
load_dotenv()

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    # Check Streamlit secrets first, then environment variables
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Please set OPENAI_API_KEY in your .streamlit/secrets.toml file, .env file, or environment variables")
        return None
    return OpenAI(api_key=api_key)

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Analysis Assistant")
st.markdown("Upload a CSV file and ask questions about your data. The AI will generate and execute pandas code to answer your questions.")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'code_history' not in st.session_state:
    st.session_state.code_history = []

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to analyze"
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success(f"✅ File loaded successfully! ({len(st.session_state.df)} rows, {len(st.session_state.df.columns)} columns)")
            
            # Show basic info
            st.subheader("📋 Data Info")
            st.write(f"**Shape:** {st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} columns")
            st.write(f"**Columns:** {', '.join(st.session_state.df.columns.tolist())}")
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.session_state.df = None

# Main content area
if st.session_state.df is not None:
    # Data preview section
    st.header("👀 Data Preview")
    st.dataframe(st.session_state.df.head(10), use_container_width=True)
    
    # Question input section
    st.header("💬 Ask a Question")
    
    # Example questions
    example_questions = [
        "What are the top 5 products by revenue?",
        "Show me a trend chart of sales over time",
        "What is the average sales per region?",
        "Create a bar chart showing total sales by category",
        "What are the summary statistics for numeric columns?",
        "Show me a correlation heatmap of numeric columns"
    ]
    
    st.markdown("**Example questions:**")
    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        with cols[i % 3]:
            if st.button(question, key=f"example_{i}", use_container_width=True):
                st.session_state.question = question
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        value=st.session_state.get('question', ''),
        placeholder="e.g., What are the top 5 products by revenue?",
        key="question_input"
    )
    
    if st.button("🔍 Analyze", type="primary", use_container_width=True) or st.session_state.get('question'):
        if question or st.session_state.get('question'):
            query = question or st.session_state.get('question', '')
            st.session_state.question = None  # Reset
            
            with st.spinner("🤖 Generating code and analyzing data..."):
                # Generate code using OpenAI
                client = get_openai_client()
                if client:
                    try:
                        # Create prompt for code generation
                        prompt = f"""You are a data analysis assistant. Given a pandas DataFrame called 'df' with the following columns: {', '.join(st.session_state.df.columns.tolist())}

The user asks: "{query}"

Generate Python code using pandas and plotly to answer this question. Follow these rules:
1. Use the DataFrame 'df' that is already loaded
2. Import only what you need (pandas as pd, plotly.express as px, plotly.graph_objects as go)
3. For visualizations, use plotly and store the figure in a variable called 'fig'
4. For text results, store in a variable called 'result'
5. For tables, store in a variable called 'result_table'
6. Do NOT use plt.show() or st functions - just create the objects
7. Make sure the code is safe and only uses pandas/plotly operations
8. If creating a chart, use appropriate chart types (bar, line, scatter, etc.)
9. Return ONLY the Python code, no explanations or markdown

Example for "top 5 products by revenue":
```python
result_table = df.nlargest(5, 'revenue')
```

Example for "trend chart of sales over time":
```python
fig = px.line(df, x='date', y='sales', title='Sales Trend Over Time')
```

Now generate the code:"""

                        response = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You are a helpful data analysis assistant that generates clean, safe pandas and plotly code."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.3,
                            max_tokens=1000
                        )
                        
                        generated_code = response.choices[0].message.content.strip()
                        
                        # Clean up the code (remove markdown code blocks if present)
                        if generated_code.startswith("```python"):
                            generated_code = generated_code[9:]
                        elif generated_code.startswith("```"):
                            generated_code = generated_code[3:]
                        if generated_code.endswith("```"):
                            generated_code = generated_code[:-3]
                        generated_code = generated_code.strip()
                        
                        # Store in history
                        st.session_state.code_history.append({
                            'question': query,
                            'code': generated_code
                        })
                        
                        # Display the generated code
                        st.header("💻 Generated Code")
                        st.code(generated_code, language="python")
                        
                        # Execute the code safely
                        st.header("📊 Results")
                        
                        # Create a safe execution environment
                        safe_globals = {
                            'pd': pd,
                            'px': px,
                            'go': go,
                            'df': st.session_state.df.copy(),
                            'fig': None,
                            'result': None,
                            'result_table': None
                        }
                        
                        try:
                            # Capture stdout/stderr
                            f = io.StringIO()
                            with redirect_stdout(f), redirect_stderr(f):
                                exec(generated_code, safe_globals)
                            
                            output = f.getvalue()
                            if output:
                                st.text("Execution output:")
                                st.text(output)
                            
                            # Display results
                            if safe_globals.get('fig') is not None:
                                st.plotly_chart(safe_globals['fig'], use_container_width=True)
                            
                            if safe_globals.get('result_table') is not None:
                                st.dataframe(safe_globals['result_table'], use_container_width=True)
                            
                            if safe_globals.get('result') is not None:
                                result = safe_globals['result']
                                if isinstance(result, (pd.Series, pd.DataFrame)):
                                    st.dataframe(result, use_container_width=True)
                                else:
                                    st.write(result)
                            
                            # If no specific result variables were set, check if anything was printed
                            if (safe_globals.get('fig') is None and 
                                safe_globals.get('result_table') is None and 
                                safe_globals.get('result') is None and 
                                not output):
                                st.info("Code executed successfully, but no output was generated. Make sure the code sets 'fig', 'result', or 'result_table' variables.")
                        
                        except Exception as e:
                            st.error(f"Error executing code: {str(e)}")
                            st.code(generated_code, language="python")
                    
                    except Exception as e:
                        st.error(f"Error generating code: {str(e)}")
                        st.info("Make sure you have set your OPENAI_API_KEY in a .env file or as an environment variable.")
        else:
            st.warning("Please enter a question to analyze the data.")
    
    # Code history section
    if st.session_state.code_history:
        st.header("📚 Code History")
        for i, item in enumerate(reversed(st.session_state.code_history[-5:])):  # Show last 5
            with st.expander(f"Q: {item['question']}"):
                st.code(item['code'], language="python")

else:
    st.info("👈 Please upload a CSV file using the sidebar to get started.")
    st.markdown("""
    ### How to use:
    1. **Upload a CSV file** using the sidebar
    2. **Review the data preview** to see your data
    3. **Ask questions** about your data in natural language
    4. **View the generated code** to learn pandas and plotly
    5. **See the results** as tables or interactive charts
    
    ### Example Questions:
    - "What are the top 5 products by revenue?"
    - "Show me a trend chart of sales over time"
    - "What is the average sales per region?"
    - "Create a bar chart showing total sales by category"
    """)




