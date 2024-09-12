# Answer Scripts

This dataset contains images of annotated MCQ answer scripts. The dataset contains answers for 3 question papers A, B, and C. Each question in the three papers has 4 choices. Answer scripts has an additional slot for a 5th answer, which should be ignored. Images are provided in the JPG format with approximate pixel size 3000x2000.

# Marking Scheme

All three marking schemes have their own CSV file. Each scheme has the following column names

1. Question ID: Integers with the range [1,50]
2. Answer ID: Integers or sets of integers from the range [1,4]
3. Condition: "-", "Any", or "All" indicates how selections should be collated to make the score.

Each question carries a weight of 1. Total attainable score is 50. A specific question might have more than one valid answer. If selecting atleast one answer is sufficient, such records are annotated as "Any" while if all mentioned answers are required, such records are annotated as "All" under the "Condition" column. Grading criteria for questions with "All" is

$\frac{\lvert V_s\rvert}{\lvert V_r\rvert}-\frac{\lvert I_s\rvert}{\lvert I_r\rvert}$

where $V_r$ is the set of valid answers, $V_s$ is the set of selected valid answers, $I_r$ is the set of invalid answers, $I_s$ is the set of selected invalid answers, and $\lvert .\rvert$ is the cardinality operator.
