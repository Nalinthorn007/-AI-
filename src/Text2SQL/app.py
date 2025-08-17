import streamlit as st 
import os
from dotenv import load_dotenv

# Import our modules
from sql_generator import SQLGenerator
from chart_generator import ChartGenerator
from db_operations import DatabaseOperations

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Text2SQL Assistant",
    page_icon="🗄️",
    layout="wide"
)

# Custom CSS for better styling and Lao language support
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .query-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    .result-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #dee2e6;
        margin-top: 1rem;
    }
    .sql-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #007bff;
        font-family: 'Courier New', monospace;
    }
    .lao-text {
        font-family: 'Noto Sans Lao', 'Saysettha OT', 'Phetsarath OT', sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🗄️ Text2SQL Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #666;">ຖາມຄໍາຖາມກ່ຽວກັບຂໍ້ມູນຂອງທ່ານເປັນພາສາທໍາມະຊາດ</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ ການຕັ້ງຄ່າ")
        
        # Anthropic API Key
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="ປ້ອນ API key ຂອງ Anthropic"
        )
        
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        
        # Database connection test
        st.subheader("📊 ສະຖານະຖານຂໍ້ມູນ")
        if st.button("ທົດສອບການເຊື່ອມຕໍ່"):
            try:
                db_ops = DatabaseOperations()
                if db_ops.test_connection():
                    st.success("✅ ເຊື່ອມຕໍ່ກັບຖານຂໍ້ມູນສໍາເລັດແລ້ວ")
                else:
                    st.error("❌ ການເຊື່ອມຕໍ່ກັບຖານຂໍ້ມູນລົ້ມເຫລວ")
            except Exception as e:
                st.error(f"❌ ຂໍ້ຜິດພາດ: {str(e)}")
        
        # Show database schema
        if st.button("ສະແດງ Schema"):
            try:
                db_ops = DatabaseOperations()
                if db_ops.connect():
                    schema = db_ops.get_table_schema()
                    st.text_area("ສະແດງຖານຂໍ້ມູນ Schema", schema, height=300)
            except Exception as e:
                st.error(f"ຂໍ້ຜິດພາດ: {str(e)}")
    
    # Main query interface
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    st.subheader("💬 ຖາມຄໍາຖາມກ່ຽວກັບຂໍ້ມູນຂອງທ່ານ")
    
    # Query input
    query = st.text_area(
        "ອະທິບາຍສິ່ງທີ່ທ່ານຕ້ອງການຮູ້:",
        placeholder="ຕົວຢ່າງ: ສະແດງລູກຄ້າທີ່ດີທີ່ສຸດ 10 ຄົນຕາມຍອດຂາຍ, ຫຼື ຊອກຫາຄໍາສັ່ງທັງໝົດຈາກເດືອນທີ່ແລ້ວ",
        height=100,
        key="query_input"
    )
    
    # Generate button
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_button = st.button("🚀 ສ້າງ", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process query when button is clicked
    if generate_button and query:
        if not anthropic_key:
            st.error("❌ ກະລຸນາປ້ອນ Anthropic API key ໃນ sidebar")
        else:
            try:
                with st.spinner("🤖 ກໍາລັງສ້າງຄໍາສັ່ງ SQL..."):
                    # Get database schema
                    db_ops = DatabaseOperations()
                    if db_ops.connect():
                        schema = db_ops.get_table_schema()
                        
                        # Generate SQL
                        sql_gen = SQLGenerator(anthropic_key)
                        result = sql_gen.generate_sql(query, schema)
                        
                        if "sql" in result:
                            # Store results in session state
                            st.session_state.sql_query = result["sql"]
                            st.session_state.description = result.get("description", "")
                            st.session_state.user_query = query
                            st.success("✅ ສ້າງ SQL ສໍາເລັດແລ້ວ!")
                        else:
                            st.error("❌ ການສ້າງ SQL ລົ້ມເຫລວ")
                    else:
                        st.error("❌ ການເຊື່ອມຕໍ່ກັບຖານຂໍ້ມູນລົ້ມເຫລວ")
                        
            except Exception as e:
                st.error(f"❌ ຂໍ້ຜິດພາດ: {str(e)}")
    
    # Display results if available
    if hasattr(st.session_state, 'sql_query'):
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        
        # Display the original query
        st.subheader("📝 ຄໍາຖາມຂອງທ່ານ")
        st.info(st.session_state.user_query)
        
        # Display generated SQL
        st.subheader("🔍 SQL ທີ່ສ້າງໄດ້")
        st.markdown(f'<div class="sql-box">{st.session_state.sql_query}</div>', unsafe_allow_html=True)
        
        # Display description in Lao
        if st.session_state.description:
            st.subheader("💡 ຄໍາອະທິບາຍ")
            st.markdown(f'<div class="lao-text">{st.session_state.description}</div>', unsafe_allow_html=True)
        
        # Execute query button
        if st.button("▶️ ປະຕິບັດຄໍາສັ່ງ", type="secondary"):
            try:
                with st.spinner("🔄 ກໍາລັງປະຕິບັດຄໍາສັ່ງ..."):
                    db_ops = DatabaseOperations()
                    if db_ops.connect():
                        result = db_ops.execute_query(st.session_state.sql_query)
                        
                        if "error" not in result:
                            st.session_state.query_result = result
                            st.success("✅ ປະຕິບັດຄໍາສັ່ງສໍາເລັດແລ້ວ!")
                        else:
                            st.error(f"❌ ການປະຕິບັດຄໍາສັ່ງລົ້ມເຫລວ: {result['error']}")
                    else:
                        st.error("❌ ການເຊື່ອມຕໍ່ກັບຖານຂໍ້ມູນລົ້ມເຫລວ")
                        
            except Exception as e:
                st.error(f"❌ ຂໍ້ຜິດພາດ: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display query results
    if hasattr(st.session_state, 'query_result'):
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("📊 ຜົນລັບຄໍາສັ່ງ")
        
        result = st.session_state.query_result
        
        if result.get("success") and "data" in result:
            df = result["data"]
            
            # Results summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ແຖວ", f"{result.get('row_count', 0):,}")
            with col2:
                st.metric("ຖັນ", len(result.get('columns', [])))
            with col3:
                st.metric("ຂະໜາດຂໍ້ມູນ", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Data preview
            st.subheader("📋 ຕົວຢ່າງຂໍ້ມູນ")
            st.dataframe(df, use_container_width=True)
            
            # Generate chart
            if not df.empty:
                st.subheader("📈 ການສະແດງຜົນ")
                
                try:
                    chart_gen = ChartGenerator()
                    fig = chart_gen.create_chart(df)
                    st.plotly_chart(fig, use_container_width=True)                    
                        
                except Exception as e:
                    st.error(f"❌ ການສ້າງການສະແດງຜົນລົ້ມເຫລວ: {str(e)}")
        else:
            st.error("ບໍ່ມີຜົນລັບໃຫ້ສະແດງ")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>ສ້າງດ້ວຍ ❤️ ໃຊ້ Streamlit, Anthropic Claude, ແລະ MariaDB</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 