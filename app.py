import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import tempfile
from PIL import Image
import io
import zipfile
from datetime import datetime
from grade_mcq import (
    load_image, find_sheet_corners, warp_perspective, 
    extract_question_boxes, detect_colored_bubble, 
    load_marking_scheme, grade
)

# Page configuration
st.set_page_config(
    page_title="MCQ Grader",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 5px;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'marking_scheme' not in st.session_state:
    st.session_state.marking_scheme = None
if 'marking_scheme_name' not in st.session_state:
    st.session_state.marking_scheme_name = None
if 'results' not in st.session_state:
    st.session_state.results = []
if 'annotated_images' not in st.session_state:
    st.session_state.annotated_images = []

def annotate_image(image, detected_answers, marking_scheme):
    """Annotate image with detected answers and correctness"""
    annotated = image.copy()
    question_boxes_coords = []
    
    # Get image dimensions
    height, width = image.shape[:2]
    num_columns, num_rows = 5, 10
    box_width, box_height = width // num_columns, height // num_rows
    
    # Calculate coordinates for each question
    for j in range(num_columns):
        for i in range(num_rows):
            top_left = (j * box_width, i * box_height)
            bottom_right = ((j + 1) * box_width, (i + 1) * box_height)
            question_boxes_coords.append((top_left, bottom_right))
    
    # Annotate each question
    for idx, (q_no, detected_answer) in enumerate(detected_answers):
        if idx >= len(question_boxes_coords):
            break
            
        top_left, bottom_right = question_boxes_coords[idx]
        
        # Check if answer is correct
        correct_data = marking_scheme.get(q_no, {})
        correct_answers = correct_data.get('correct_answers', [])
        condition = correct_data.get('condition', '-')
        
        is_correct = detected_answer in correct_answers if condition in ['-', 'Any'] else set(correct_answers) == {detected_answer}
        
        # Draw rectangle around the question box
        color = (0, 255, 0) if is_correct else (0, 0, 255)  # Green if correct, Red if wrong
        cv2.rectangle(annotated, top_left, bottom_right, color, 3)
        
        # Add question number and detected answer
        text = f"Q{q_no}: {detected_answer}"
        cv2.putText(annotated, text, (top_left[0] + 5, top_left[1] + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add checkmark or cross
        symbol = "✓" if is_correct else "✗"
        cv2.putText(annotated, symbol, (bottom_right[0] - 30, top_left[1] + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return annotated

def process_single_sheet(image_file, marking_scheme, file_name):
    """Process a single answer sheet"""
    try:
        # Load image
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Process the sheet
        corners = find_sheet_corners(image)
        warped_image = warp_perspective(image, corners)
        question_boxes = extract_question_boxes(warped_image)
        
        # Detect answers
        detected_answers = [(i + 1, detect_colored_bubble(question_box)) 
                          for i, question_box in enumerate(question_boxes)]
        
        # Create DataFrame
        detected_answers_df = pd.DataFrame(detected_answers, columns=["q_no", "option"])
        
        # Grade
        results_df = grade(detected_answers_df, marking_scheme)
        total_marks = results_df['Correct'].sum()
        
        # Annotate image
        annotated_image = annotate_image(warped_image, detected_answers, marking_scheme)
        
        return {
            'file_name': file_name,
            'total_marks': total_marks,
            'results_df': results_df,
            'detected_answers_df': detected_answers_df,
            'annotated_image': annotated_image,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'file_name': file_name,
            'success': False,
            'error': str(e)
        }

def create_download_zip(results):
    """Create a ZIP file with all results"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add individual result CSVs
        for result in results:
            if result['success']:
                csv_buffer = io.StringIO()
                result['results_df'].to_csv(csv_buffer, index=False)
                zip_file.writestr(f"{result['file_name']}_graded.csv", csv_buffer.getvalue())
                
                # Add annotated images
                _, img_encoded = cv2.imencode('.png', result['annotated_image'])
                zip_file.writestr(f"{result['file_name']}_annotated.png", img_encoded.tobytes())
        
        # Add summary CSV
        summary_data = [{'file_name': r['file_name'], 'total_marks': r['total_marks']} 
                       for r in results if r['success']]
        summary_df = pd.DataFrame(summary_data)
        summary_buffer = io.StringIO()
        summary_df.to_csv(summary_buffer, index=False)
        zip_file.writestr('Summary.csv', summary_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

# Main App
st.markdown('<div class="main-header">Automatic MCQ Grader</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for marking scheme upload
with st.sidebar:
    st.header("🎯 Marking Scheme")
    
    if st.session_state.marking_scheme is None:
        st.markdown("""
        <div style='background-color: #ff6b6b; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <h4 style='margin: 0; color: white;'>⚠️ Step 1: Start Here!</h4>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                Upload a marking scheme to begin grading answer sheets
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        marking_scheme_file = st.file_uploader(
            "Upload Marking Scheme CSV",
            type=['csv'],
            help="Upload the answer key CSV file with Question ID, Answer ID, and Condition columns"
        )
        
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 0.8rem; border-radius: 5px; margin-top: 1rem; font-size: 0.85rem;'>
            <p style='margin: 0; color: #DAA520;'><strong> !!! Tip:</strong></p>
            <p style='margin: 0.3rem 0 0 0; color: #666;'>
                Your CSV file should contain the correct answers for all 50 questions. See the main area for format details.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if marking_scheme_file is not None:
            try:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    tmp_file.write(marking_scheme_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Load marking scheme
                st.session_state.marking_scheme = load_marking_scheme(tmp_path)
                st.session_state.marking_scheme_name = marking_scheme_file.name
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                st.success(f"✅ Successfully Loaded: {marking_scheme_file.name}")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading marking scheme: {str(e)}")
    else:
        st.markdown("""
        <div style='background-color: #51cf66; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <h4 style='margin: 0; color: white;'>✅ Marking Scheme Active</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"**File:** {st.session_state.marking_scheme_name}")
        st.metric("Total Questions", len(st.session_state.marking_scheme))
        
        if st.button("🔄 Change Marking Scheme"):
            st.session_state.marking_scheme = None
            st.session_state.marking_scheme_name = None
            st.session_state.results = []
            st.session_state.annotated_images = []
            st.rerun()
        
        st.markdown("---")
        st.subheader("Marking Scheme Preview")
        preview_data = []
        for q_no, data in list(st.session_state.marking_scheme.items())[:5]:
            preview_data.append({
                'Q': q_no,
                'Answers': ','.join(map(str, data['correct_answers'])),
                'Condition': data['condition']
            })
        st.dataframe(pd.DataFrame(preview_data), hide_index=True)
        if len(st.session_state.marking_scheme) > 5:
            st.caption(f"...and {len(st.session_state.marking_scheme) - 5} more questions")

# Main content area
if st.session_state.marking_scheme is None:
    # Welcome section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2.5rem; border-radius: 10px; color: white; margin-bottom: 2.5rem; text-align: center;'>
        <h2 style='margin: 0; color: white;'>🎓 Welcome to Automatic MCQ Grader</h2>
        <p style='font-size: 1.1rem; margin-top: 0.5rem; color: #f0f0f0;'>
            Grade multiple-choice answer sheets automatically using computer vision technology
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centered upload section with better design
    col_spacer1, col_center, col_spacer2 = st.columns([1, 3, 1])
    
    with col_center:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 1.5rem;'>
            <h3 style='color: #333; margin-bottom: 0.5rem;'>📄 Get Started</h3>
            <p style='color: #666; font-size: 1.05rem;'>
                Upload your marking scheme CSV to begin grading answer sheets
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        marking_scheme_quick = st.file_uploader(
            "Upload Marking Scheme CSV",
            type=['csv'],
            key="quick_csv_uploader",
            help="Upload your marking scheme CSV with Question ID, Answer ID, and Condition columns",
            label_visibility="collapsed"
        )
        
        if marking_scheme_quick is not None:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    tmp_file.write(marking_scheme_quick.getvalue())
                    tmp_path = tmp_file.name
                
                st.session_state.marking_scheme = load_marking_scheme(tmp_path)
                st.session_state.marking_scheme_name = marking_scheme_quick.name
                os.unlink(tmp_path)
                
                st.success(f"✅ Successfully Loaded: {marking_scheme_quick.name}")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading marking scheme: {str(e)}")
        
        st.markdown("""
        <div style='text-align: center; margin-top: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 8px;'>
            <p style='margin: 0; color: #666; font-size: 0.9rem;'>
                 <strong>!!! Tip:</strong> You can also upload from the sidebar on the left
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # What you can do section
    st.markdown("### What You Can Do With This App")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background-color: #e3f2fd; padding: 1.5rem; border-radius: 8px; height: 100%;'>
            <h4 style='color: #1976d2; margin-top: 0;'>📤 Batch Processing</h4>
            <p style='color: #555;'>Upload and grade multiple answer sheets simultaneously. Process entire classrooms in minutes, not hours!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #f3e5f5; padding: 1.5rem; border-radius: 8px; height: 100%;'>
            <h4 style='color: #7b1fa2; margin-top: 0;'>🎨 Visual Verification</h4>
            <p style='color: #555;'>Get annotated images showing correct (green) and incorrect (red) answers for easy verification and review.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: #e8f5e9; padding: 1.5rem; border-radius: 8px; height: 100%;'>
            <h4 style='color: #388e3c; margin-top: 0;'>📊 Instant Results</h4>
            <p style='color: #555;'>Get detailed reports with scores, individual results, and summary statistics. Download everything as a ZIP file.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Marking Scheme Format
    st.markdown("### Marking Scheme Format")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style='background-color: #f5f5f5; padding: 1.5rem; border-radius: 8px;'>
            <h4 style='color: #333; margin-top: 0;'>Required CSV Columns:</h4>
            <ul style='color: #666;'>
                <li><code style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px;'>Question ID</code> : Question number (1-50)</li>
                <li><code style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px;'>Answer ID</code> : Correct answer(s)</li>
                <li><code style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px;'>Condition</code> : Grading rule</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #f5f5f5; padding: 1.5rem; border-radius: 8px;'>
            <h4 style='color: #333; margin-top: 0;'>Condition Types:</h4>
            <ul style='color: #666;'>
                <li><code style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px;'>-</code> (single) : Only one specific answer</li>
                <li><code style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px;'>Any</code> : Any of listed answers is correct</li>
                <li><code style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px;'>All</code> : All answers must be selected</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Example table
    st.markdown("#### Example Marking Scheme:")
    example_df = pd.DataFrame({
        'Question ID': [1, 2, 3, 4, 5],
        'Answer ID': ['3', '2', '1,2', '4', '5'],
        'Condition': ['-', '-', 'Any', '-', '-']
    })
    st.dataframe(example_df, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 2rem; border-radius: 10px; text-align: center; color: white;'>
        <h3 style='margin: 0; color: white;'>👈 Ready to Start? Upload Your Marking Scheme!</h3>
        <p style='margin: 0.5rem 0 0 0; color: #f0f0f0; font-size: 1.1rem;'>
            Look at the sidebar on the left and click "Browse files" to begin
        </p>
    </div>
    """, unsafe_allow_html=True)
    
else:
    # Start Over button at the top
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col3:
        if st.button("🔄 Start Over", type="secondary", use_container_width=True):
            st.session_state.marking_scheme = None
            st.session_state.marking_scheme_name = None
            st.session_state.results = []
            st.session_state.annotated_images = []
            st.rerun()
    
    # Success message after marking scheme is loaded
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
        <h3 style='margin: 0; color: white;'>✅ The marking scheme is successfully uploaded</h3>
        <p style='margin: 0.5rem 0 0 0; color: #f0f0f0;'>
            Now you can upload answer sheets and start grading!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.subheader("📤 Step 2: Upload Answer Sheets")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "📁 Choose Answer Sheet Images",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Select one or more answer sheet images. You can Ctrl+Click to select multiple files"
        )
    
    with col2:
        st.metric("📊 Files Selected", len(uploaded_files) if uploaded_files else 0)
        if uploaded_files:
            st.success(f"Ready to grade!")
    
    if uploaded_files:
        if st.button("Grade All Sheets", type="primary", use_container_width=True):
            st.session_state.results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                result = process_single_sheet(
                    uploaded_file, 
                    st.session_state.marking_scheme,
                    uploaded_file.name.rsplit('.', 1)[0]
                )
                st.session_state.results.append(result)
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("✅ All sheets processed!")
            st.success(f"Graded {len(uploaded_files)} answer sheets successfully!")
    
    # Display results
    if st.session_state.results:
        st.markdown("---")
        st.subheader("Grading Results")
        
        # Summary table
        summary_data = []
        for result in st.session_state.results:
            if result['success']:
                summary_data.append({
                    'Student': result['file_name'],
                    'Total Marks': f"{result['total_marks']}/50",
                    'Percentage': f"{(result['total_marks']/50)*100:.1f}%",
                    'Status': 'Successfully Graded'
                })
            else:
                summary_data.append({
                    'Student': result['file_name'],
                    'Total Marks': 'Error',
                    'Percentage': '-',
                    'Status': f"Error: {result['error']}"
                })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Download button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            zip_buffer = create_download_zip(st.session_state.results)
            st.download_button(
                label="Download All Results (ZIP)",
                data=zip_buffer,
                file_name=f"grading_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
        
        # Detailed view
        st.markdown("---")
        st.subheader("Detailed View")
        
        for result in st.session_state.results:
            if result['success']:
                with st.expander(f"{result['file_name']} - Score: {result['total_marks']}/50"):
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        st.markdown("**Annotated Answer Sheet:**")
                        # Convert BGR to RGB for display
                        annotated_rgb = cv2.cvtColor(result['annotated_image'], cv2.COLOR_BGR2RGB)
                        st.image(annotated_rgb, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Detected Answers:**")
                        display_df = result['detected_answers_df'].copy()
                        display_df.columns = ['Question', 'Answer']
                        st.dataframe(display_df, height=400, hide_index=True)

                    with col3:    
                        st.markdown("**Question-wise Results:**")
                        results_display = result['results_df'].copy()
                        results_display['Correct'] = results_display['Correct'].map({True: '✅', False: '❌'})
                        st.dataframe(results_display, height=400, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with ❤️ using Streamlit | Automatic MCQ Grader v1.0</p>
</div>
""", unsafe_allow_html=True)
