# Automatic-MCQ-Grader
Automatic MCQ Grader using classical algorithms
## Overview

The Automated MCQ Grading System is a computer vision-based application designed to streamline the grading of multiple-choice question (MCQ) exams. This system addresses the challenges of manual grading, such as time consumption and human error, by providing an efficient and reliable method to automatically assess student responses from scanned answer sheets.

## Features

- **Image Preprocessing**: 
  - Loads scanned or photographed answer sheets.
  - Converts images to grayscale and applies edge detection.
  - Warps images to a known aspect ratio for consistent analysis.

- **Question Grid Creation**: 
  - Generates a structured grid layout to isolate each question and its corresponding answer options.

- **Colored Bubble Detection**: 
  - Identifies filled answer bubbles for each question based on predefined conditions.
  
- **Grading Logic**: 
  - Compares detected answers against a provided marking scheme.
  - Supports different grading conditions: single answers, any of the specified answers, and all specified answers must be selected.

- **Output Generation**: 
  - Calculates total scores and grades.
  - Generates individual CSV files for each answer sheet and a summary report.

## Input Requirements

- **Marking Scheme**: Load an answer key from a CSV file.
- **Image Directory**: Provide a directory containing scanned or photographed answer scripts.
- **Output Directory**: Specify a path where the results will be saved.

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SamudraUduwaka/Automatic-MCQ-Grader.git
   cd automated-mcq-grading-system
