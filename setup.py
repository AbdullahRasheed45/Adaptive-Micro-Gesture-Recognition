from setuptools import find_packages, setup

setup(
    name="adaptive_microgesture",
    version="0.0.1",
    author="Muhammad Abdullah Rasheed",
    author_email="abdullahrasheed45@gmail.com",
    description="Adaptive Micro-Gesture Recognition system for accessibility with digital whiteboard integration",
    packages=find_packages(),
    install_requires=[
        "mediapipe",
        "torch",
        "numpy",
        "pandas",
        "scikit-learn",
        "opencv-python",
        "torchmetrics",
        "matplotlib",
    ],
    python_requires='>=3.9',
)
