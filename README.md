# Smart Traffic Light Fuzzy Logic Controller

This project simulates a 4-way traffic intersection controlled by a Fuzzy Logic Inference System. It dynamically prioritizes lanes based on real-time vehicle density, wait times, and the presence of emergency vehicles.

## 🚀 How to Run on a New PC

Follow these steps to set up and run the interactive dashboard on any new Windows, Mac, or Linux computer.

### Step 1: Install Python
Ensure that you have **Python 3.8 or higher** installed on the new computer.
You can download Python from [python.org](https://www.python.org/downloads/).
*(Make sure to check the box that says "Add Python to PATH" during installation).*

### Step 2: Extract the Project Files
Copy the entire `sc_mini` folder (containing `app.py`, `fuzzy_controller.py`, `visualization.py`, etc.) onto the new PC.

### Step 3: Open terminal/Command Prompt
Navigate to the project folder. For example, if you placed the folder on your Desktop:
```bash
cd Desktop/sc_mini
```

### Step 4: Install Dependencies
This project relies on strict versions of external math and visualization libraries. Install all required dependencies at once using pip:
```bash
pip install -r requirements.txt
```

### Step 5: Run the Interactive Dashboard
Launch the Streamlit web server:
```bash
streamlit run app.py
```
A browser window will automatically open to `http://localhost:8501/` displaying the live dashboard!

---

## 🛠 Project Structure
- **`app.py`**: The main Streamlit dashboard file.
- **`fuzzy_controller.py`**: Contains the 10-rule Fuzzy Logic engine and Queue Clearance mathematics.
- **`visualization.py`**: Handles drawing the animated traffic intersection using Matplotlib.
- **`main.py`**: *Optional* terminal script that brute-forces the 6 edge cases and generates static charts manually in the `/plots/` folder.
- **`report.md`**: The final detailed academic evaluation covering the heuristics, tie-breaking logic, and formula derivations.
