import os
import argparse
from deepface import DeepFace

def recognize_face(test_image_path, db_path="images/", model_name="Facenet", distance_metric="cosine"):
    """
    Recognizes a face in the test image by comparing it with the database of known images.
    Returns the name of the identified person (derived from the filename) or 'Unknown'.
    """
    if not os.path.exists(test_image_path):
        print(f"Error: Test image '{test_image_path}' not found.")
        return "Unknown"

    if not os.path.exists(db_path):
        print(f"Error: Database path '{db_path}' not found.")
        return "Unknown"

    print(f"Analyzing {test_image_path} against database in {db_path}...")
    try:
        # DeepFace.find returns a list of pandas DataFrames (one per face detected)
        # We enforce enforce_detection=True so it complains if no face is found in test_image.
        # But we can set it to False if we just want it to quietly fail if no face is in the image.
        dfs = DeepFace.find(
            img_path=test_image_path, 
            db_path=db_path, 
            model_name=model_name,
            distance_metric=distance_metric,
            enforce_detection=True,
            silent=True
        )

        if len(dfs) > 0 and not dfs[0].empty:
            # Match found
            best_match_path = dfs[0].iloc[0]['identity']
            
            # Extract name from file path (e.g., 'images/John_Doe.jpeg' -> 'John_Doe')
            filename = os.path.basename(best_match_path)
            person_name = os.path.splitext(filename)[0]
            
            # remove underscores for cleaner formatting
            person_name = person_name.replace("_", " ")
            print(f"Match found! This is: {person_name}")
            return person_name
        else:
            print("No matching face found in the database. Output: Unknown")
            return "Unknown"

    except ValueError as val_err:
        print(f"Face Detection Error: {val_err}")
        return "Unknown"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Unknown"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face Recognizer utilizing DeepFace")
    parser.add_argument("--test", type=str, required=True, help="Path to the test image")
    parser.add_argument("--db", type=str, default="images/", help="Path to the directory containing known faces")
    
    args = parser.parse_args()
    
    result = recognize_face(args.test, args.db)
    print(f"FINAL RESULT: {result}")
