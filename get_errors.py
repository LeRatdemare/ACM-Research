import csv
from vocabulary import Vocabulary

def run_script():
    try:
        with open('semantic_tree.py') as file:
            code = file.read()
            exec(code)
    except Exception as e:
        with open('error_log.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([str(e)])

for _ in range(10):
    run_script()