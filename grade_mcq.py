import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import pandas as pd
import argparse

def load_image(image_path):
    return cv2.imread(image_path)

def find_sheet_corners(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    perimeter = cv2.arcLength(largest_contour, True)
    corners = cv2.approxPolyDP(largest_contour, 0.02 * perimeter, True)
    if len(corners) == 4:
        return corners.reshape(4, 2)
    else:
        raise ValueError("Could not find the corners of the sheet")

def warp_perspective(image, corners):
    top_left, top_right, bottom_right, bottom_left = corners
    width = max(np.linalg.norm(top_right - top_left), np.linalg.norm(bottom_right - bottom_left))
    height = max(np.linalg.norm(top_right - bottom_right), np.linalg.norm(top_left - bottom_left))
    destination_corners = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(corners.astype(np.float32), destination_corners)
    warped = cv2.warpPerspective(image, M, (int(width), int(height)))
    return cv2.flip(cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE), 1)

def create_grid(image, num_questions=10, num_options=5):
    height, width = image.shape[:2]
    cell_height, cell_width = height // num_questions, width // num_options
    grid = [[((j * cell_width, i * cell_height), ((j + 1) * cell_width, (i + 1) * cell_height)) for j in range(num_options)] for i in range(num_questions)]
    return grid

def extract_question_boxes(image, num_columns=5, num_rows=10):
    height, width = image.shape[:2]
    box_width, box_height = width // num_columns, height // num_rows
    question_boxes = []
    
    # Process in column-wise order
    for j in range(num_columns):         # Iterate over columns first
        for i in range(num_rows):        # Then iterate over rows
            top_left = (j * box_width, i * box_height)
            bottom_right = ((j + 1) * box_width, (i + 1) * box_height)
            question_box = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            question_boxes.append(question_box)
    
    return question_boxes


def detect_colored_bubble(question_box):
    gray_box = cv2.cvtColor(question_box, cv2.COLOR_BGR2GRAY)
    _, thresh_box = cv2.threshold(gray_box, 150, 255, cv2.THRESH_BINARY_INV)
    bubble_width = question_box.shape[1] // 6
    filled_bubbles = [np.sum(thresh_box[:, i * bubble_width:(i + 1) * bubble_width] == 255) / float(thresh_box.size) for i in range(1, 6)]
    return np.argmax(filled_bubbles) + 1

def process_answer_sheet(image_path, marking_scheme):
    image = load_image(image_path)
    corners = find_sheet_corners(image)
    warped_image = warp_perspective(image, corners)
    question_boxes = extract_question_boxes(warped_image)
    results = [(i + 1, detect_colored_bubble(question_box)) for i, question_box in enumerate(question_boxes)]
    return pd.DataFrame(results, columns=["q_no", "option"])

def load_marking_scheme(marking_scheme_path):
    with open(marking_scheme_path, 'r') as file:
        reader = csv.DictReader(file)
        return {int(row['Question ID']): {'correct_answers': [int(ans) for ans in row['Answer ID'].split(',')], 'condition': row['Condition']} for row in reader}

def grade(detected_answers_df, marking_scheme):
    total_marks = 0
    results = []
    for index, row in detected_answers_df.iterrows():
        q_no = row['q_no']
        detected_answer = row['option']
        correct_data = marking_scheme[q_no]
        correct_answers, condition = correct_data['correct_answers'], correct_data['condition']
        is_correct = detected_answer in correct_answers if condition in ['-', 'Any'] else set(correct_answers) == {detected_answer}
        if is_correct:
            total_marks += 1
        results.append({'Question': q_no, 'Correct': is_correct})
    print(f"Total Marks: {total_marks}/50")
    return pd.DataFrame(results)

def save_results(df, output_path):
    df.to_csv(output_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="Grading MCQ Answer Sheets")
    parser.add_argument("--marking-scheme-path", required=True, help="Path to marking scheme CSV")
    parser.add_argument("--answer-sheet-folder", required=True, help="Folder containing answer sheet images")
    parser.add_argument("--output-folder", required=True, help="Folder to save output CSVs")
    args = parser.parse_args()
    
    marking_scheme = load_marking_scheme(args.marking_scheme_path)
    
    os.makedirs(args.output_folder, exist_ok=True)
    for image_file in os.listdir(args.answer_sheet_folder):
        if image_file.endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(args.answer_sheet_folder, image_file)
            detected_answers_df = process_answer_sheet(image_path, marking_scheme)
            results_df = grade(detected_answers_df, marking_scheme)
            output_file = os.path.join(args.output_folder, f"{os.path.splitext(image_file)[0]}_graded.csv")
            save_results(results_df, output_file)
            print(f"Processed {image_file} and saved results to {output_file}")

if __name__ == "__main__":
    main()
