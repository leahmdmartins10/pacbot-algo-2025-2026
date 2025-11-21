import statistics
from datetime import datetime
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def analyze_time_log(file_path='time_log.txt', output_file=None):
    try:
        with open(file_path, 'r') as file:
            numbers = [float(line.strip()) for line in file]
        
        max_val = max(numbers)
        min_val = min(numbers)
        mean_val = statistics.mean(numbers)
        median_val = statistics.median(numbers)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        results = f"Timestamp: {timestamp}\nMax: {max_val}\nMin: {min_val}\nMean: {mean_val}\nMedian: {median_val}\n"
        
        if output_file:
            with open(output_file, 'a') as file:
                file.write(results + "\n")
        else:
            print(results)
            
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except ValueError:
        print("Error processing file: make sure it contains floating point number")

def clear_time_log(file_path='time_log.txt'):
    open(file_path, 'w').close()

def clear_analysis(file_path='analysis_results.txt'):
    open(file_path, 'w').close()
    
if __name__ == '__main__':
    analyze_time_log()
    #analyze_time_log(output_file='analysis_results.txt')
    #clear_time_log()
    #clear_analysis()
