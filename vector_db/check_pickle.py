# check_pickle.py
import pickle
import os

def check_pickle_file(file_path):
    try:
        print(f"Checking pickle file: {file_path}")
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
            return False
        
        # Try opening with pickle directly
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                print(f"Successfully loaded with pickle. Type: {type(data)}")
                if hasattr(data, 'shape'):
                    print(f"Shape: {data.shape}")
                return True
        except Exception as e1:
            print(f"Error loading with pickle: {e1}")
            return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Check the embeddings file in various possible locations
    paths_to_check = [
        'job_embeddings.pkl',
        'linkedin_jobs_with_embeddings.pkl',
        '../linkedin_jobs_with_embeddings.pkl',
        './linkedin_jobs_with_embeddings.pkl'
    ]
    
    for path in paths_to_check:
        print(f"\nChecking {path}:")
        check_pickle_file(path)