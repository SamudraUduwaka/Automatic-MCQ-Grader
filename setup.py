from setuptools import setup, find_packages

setup(
    name="grade_mcq",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "grade_mcq=grade_mcq:main",
        ],
    },
    # install_requires=[
    #     "opencv-python",
    #     "numpy",
    #     "matplotlib",
    #     "pandas"
    # ],
)
