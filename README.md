# Automatic-MCQ-Grader
Automatic MCQ Grader using classical computer vision algorithms

## Overview

The Automated MCQ Grading System is a computer vision-based application designed to streamline the grading of multiple-choice question (MCQ) exams. This system addresses the challenges of manual grading, such as time consumption and human error, by providing an efficient and reliable method to automatically assess student responses from scanned answer sheets.

## Features

- **Image Preprocessing**: 
  - Loads scanned or photographed answer sheets
  - Converts images to grayscale and applies edge detection
  - Automatically detects sheet corners and warps images to a normalized perspective
  - Handles rotated or skewed images

- **Question Grid Creation**: 
  - Generates a structured grid layout to isolate each question and its corresponding answer options
  - Supports 50 questions (10 rows × 5 columns)
  - 5 answer options per question (bubbles 1-5)

- **Colored Bubble Detection**: 
  - Identifies filled answer bubbles using threshold-based detection
  - Processes each question box independently
  - Calculates bubble fill percentage to determine selected answers
  
- **Flexible Grading Logic**: 
  - Compares detected answers against a provided marking scheme
  - Supports multiple grading conditions:
    - **Single answer**: Only one specific answer is correct
    - **Any**: Any of the specified answers is acceptable
    - **All**: All specified answers must be selected

- **Output Generation**: 
  - Calculates total scores and grades
  - Generates individual CSV files for each answer sheet showing question-by-question results
  - Creates a Summary.csv file with overall grades for all students

## Requirements

### Dependencies

- Python 3.7+
- OpenCV (cv2)
- NumPy
- Pandas
- Matplotlib

### Input Requirements

- **Marking Scheme**: CSV file with the following columns:
  - `Question ID`: Question number (1-50)
  - `Answer ID`: Correct answer(s) (single number or comma-separated for multiple)
  - `Condition`: Grading condition (`-`, `Any`, or `All`)
  
- **Answer Sheets**: 
  - Images in JPG, JPEG, or PNG format
  - Must show the complete MCQ answer sheet with visible corners
  - Supports scanned or photographed sheets

- **Output Directory**: Path where graded results will be saved

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SamudraUduwaka/Automatic-MCQ-Grader.git
   cd Automatic-MCQ-Grader
   ```

2. **Install required dependencies**:
   ```bash
   pip install opencv-python numpy pandas matplotlib
   ```

3. **Optional - Install as a package**:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

The main script `grade_mcq.py` accepts three required arguments:

```bash
python grade_mcq.py --marking-scheme-path <path-to-marking-scheme> --answer-sheet-folder <path-to-answer-sheets> --output-folder <path-to-output>
```

### Example Commands

**Grade answer set A:**
```bash
python grade_mcq.py --marking-scheme-path "Data Set/Marking Schemes/Marking Schemes/A.csv" --answer-sheet-folder "Data Set/Answer Scripts/Answer Scripts/A" --output-folder "Graded/A"
```

**Grade answer set B:**
```bash
python grade_mcq.py --marking-scheme-path "Data Set/Marking Schemes/Marking Schemes/B.csv" --answer-sheet-folder "Data Set/Answer Scripts/Answer Scripts/B" --output-folder "Graded/B"
```

**Grade answer set C:**
```bash
python grade_mcq.py --marking-scheme-path "Data Set/Marking Schemes/Marking Schemes/C.csv" --answer-sheet-folder "Data Set/Answer Scripts/Answer Scripts/C" --output-folder "Graded/C"
```

### Marking Scheme Format

Your marking scheme CSV should follow this format:

```csv
Question ID,Answer ID,Condition
1,3,-
2,2,-
3,1,2,Any
4,4,-
5,5,-
...
```

- **Question ID**: Question number (1-50)
- **Answer ID**: Correct answer(s). Use comma-separated values for multiple answers
- **Condition**: 
  - `-`: Single correct answer
  - `Any`: Any of the listed answers is correct
  - `All`: All listed answers must be selected

## Output

The grader produces two types of output:

1. **Individual Result Files**: `{image_name}_graded.csv` for each answer sheet
   - Contains columns: `Question`, `Correct`
   - Shows whether each question was answered correctly (True/False)

2. **Summary File**: `Summary.csv` in the output folder
   - Contains columns: `image_name`, `grade`
   - Shows total marks for each student

## Project Structure

```
Automatic-MCQ-Grader/
├── grade_mcq.py          # Main grading script
├── utils.py              # Utility functions
├── main.py               # Alternative processing script
├── setup.py              # Package installation
├── README.md             # This file
├── Data Set/
│   ├── Answer Scripts/   # Sample answer sheet images
│   └── Marking Schemes/  # Sample marking schemes (A, B, C)
├── Graded/               # Output folder with graded results
└── Output_Images/        # Processed images for visualization
```

## How It Works

1. **Load Image**: Reads the answer sheet image
2. **Find Corners**: Detects the four corners of the answer sheet
3. **Warp Perspective**: Transforms the image to a top-down view
4. **Extract Grid**: Divides the sheet into a 10×5 grid (50 questions)
5. **Detect Bubbles**: For each question, identifies which bubble is filled
6. **Grade**: Compares detected answers with the marking scheme
7. **Save Results**: Outputs individual and summary CSV files

## Troubleshooting

- **"Could not find the corners of the sheet" error**: 
  - Ensure the entire answer sheet is visible in the image
  - Check that there's good contrast between the sheet and background
  - Try improving image quality or lighting

- **Incorrect bubble detection**:
  - Verify the image quality is sufficient
  - Ensure bubbles are filled clearly
  - Check that the sheet is not too skewed or wrinkled

## Contributing

Contributions are welcome! 
