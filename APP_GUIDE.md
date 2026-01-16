# MCQ Grader Web Application Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

**Option A: Using batch file (Windows)**
```bash
run_app.bat
```

**Option B: Using command line**
```bash
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

## How to Use

### Step 1: Upload Marking Scheme
1. Look at the **left sidebar**
2. Click **"Browse files"** under "Upload Marking Scheme CSV"
3. Select your marking scheme file (e.g., `A.csv`, `B.csv`, or `C.csv`)
4. The scheme will be loaded and displayed in the sidebar

### Step 2: Upload Answer Sheets
1. In the main area, click **"Browse files"** under "Upload Answer Sheet Images"
2. Select one or multiple answer sheet images
3. You can select multiple files at once (Ctrl+Click or Shift+Click)
4. Supported formats: JPG, JPEG, PNG

### Step 3: Grade Sheets
1. Click the **"Grade All Sheets"** button
2. Wait for processing (you'll see a progress bar)
3. Results will appear automatically

### Step 4: View Results
The results section shows:
- **Summary Table**: Quick overview with total marks for each student
- **Annotated Images**: Visual display of answers with green (correct) or red (incorrect) boxes
- **Detailed Results**: Question-by-question breakdown

### Step 5: Download Results
Click **"Download All Results (ZIP)"** to get:
- Individual CSV files for each student
- Annotated images showing marked answers
- Summary CSV with all grades

## Features

### Session Management
- Upload marking scheme once, grade multiple batches
- Click "Change Marking Scheme" to switch answer keys

### Batch Processing
- Upload and grade multiple sheets at once
- Progress tracking for large batches
- All results processed in one session

### Visual Annotations
- ✅ Green boxes: Correct answers
- ❌ Red boxes: Incorrect answers
- Question numbers and detected answers displayed
- Easy visual verification

### Detailed Results
- Question-by-question breakdown
- Detected answers vs. correct answers
- Total score and percentage
- Export-ready format

## Troubleshooting

### App won't start
```bash
# Make sure Streamlit is installed
pip install streamlit

# Try running with Python explicitly
python -m streamlit run app.py
```

### "Module not found" errors
```bash
# Install all requirements
pip install -r requirements.txt
```

### Images not processing
- Ensure images show the complete answer sheet
- Check that corners of the sheet are visible
- Verify image quality is clear
- Make sure bubbles are filled clearly

### Wrong results
- Verify the correct marking scheme is uploaded
- Check that the image orientation is correct
- Ensure good lighting in the original photo

## Tips

1. **Best Image Quality**: Take photos with good lighting, minimal shadows
2. **Sheet Visibility**: Ensure all 4 corners of the sheet are visible
3. **Batch Processing**: Upload all sheets at once for faster processing
4. **Save Results**: Download the ZIP file to keep all graded results
5. **Marking Scheme**: You can switch between different marking schemes in one session

## Marking Scheme Format

Your CSV file should have these columns:

| Question ID | Answer ID | Condition |
|------------|-----------|-----------|
| 1          | 3         | -         |
| 2          | 2         | -         |
| 3          | 1,2       | Any       |
| 4          | 4         | -         |

**Conditions:**
- `-`: Only one specific answer is correct
- `Any`: Any of the listed answers is acceptable
- `All`: All listed answers must be selected

## Accessing from Other Devices

If you want to access the app from other devices on your local network:

```bash
streamlit run app.py --server.address=0.0.0.0
```

Then access from other devices using: `http://YOUR_IP_ADDRESS:8501`

## Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

## Output Files Structure

When you download results, you'll get:

```
grading_results_YYYYMMDD_HHMMSS.zip
├── student1_graded.csv          # Individual results
├── student1_annotated.png       # Annotated image
├── student2_graded.csv
├── student2_annotated.png
├── ...
└── Summary.csv                  # Overall summary
```

## Example Workflow

1. Start app: `streamlit run app.py`
2. Upload marking scheme from sidebar
3. Upload 10 answer sheet images
4. Click "Grade All Sheets"
5. Review annotated images for accuracy
6. Download ZIP with all results
7. Upload different marking scheme for next batch
8. Repeat!

---

**Need help?** Check the main README.md for more information about the project.
